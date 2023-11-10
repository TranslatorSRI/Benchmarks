import asyncio
from datetime import datetime
import json
from copy import deepcopy
from pathlib import Path
import time
from typing import Optional, Sequence
import os

import httpx
from tqdm import tqdm
from reasoner_pydantic import Response

from .utils.asyncio import gather
from .utils.benchmark import benchmark_messages
from .utils.constants import CONFIG_DIR

# double the ARS timeout, just in case. The ARS should set all queries to error after 5 mins
MAX_QUERY_TIME = os.getenv("MAX_QUERY_TIME", 600)

async def fetch_results(
    benchmark: str,
    target: str,
    results_dir: str,
    overwrite: bool = False,
    scored: bool = True,
    num_concurrent_requests: int = 5,
    progress:bool = True
):
    """
    Fetches results to all the queries of a benchmark from a known target and
    stores them in the specified directory.

    Args:
        benchmark (str): Name of the benchmark to run; see benchmarks.json for a
            complete list of benchmarks.
        target (str): Name of the target to run the queries against; see
            targets.json for a complete list of known targets.
        results_dir (str): Path to the directory to store query results.
        overwrite: (bool, default False) Whether or not to overwrite existing
            query results.
        scored (bool, default True): Whether or not to fetch scored or unscored
            results. Note that scored=True uses the "fetch" entry in
            targets.json, while scored=False uses the "fetch_unscored" entry in
            targets.json.
        num_concurrent_requests (int, default 5): Number of concurrent requests
            used to fetch queries from the target.
        progress (bool, default True): Whether or not to show a progress bar.
    """
    uids, messages = benchmark_messages(benchmark)

    with open(CONFIG_DIR / 'targets.json') as file:
        targets_json = json.load(file)

    config = targets_json[target]['fetch' if scored else 'fetch_unscored']
    url = config['url']
    workflow = config.get('workflow', None)
    if workflow is not None:
        for message in messages:
            message['workflow'] = workflow
    
    if not overwrite:
        dir = Path(results_dir)

        u, m = [], []
        for uid, msg in zip(uids, messages):
            path = dir / f'{uid}.json'
            if path.exists():
                with open(path, 'r') as file:
                    msg_json = json.load(file)
                if 'benchmarks' not in msg_json:
                    continue
            
            u.append(uid)
            m.append(msg)
        
        uids = u
        messages = m

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join(results_dir, benchmark, target, timestamp)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if target == "ars":
        await send_requests_to_ars(
            uids,
            messages,
            url,
            output_dir,
            num_concurrent_requests,
            progress,
        )

    else:

        await send_requests_store_results(
            uids,
            messages,
            url,
            output_dir,
            num_concurrent_requests,
            progress,
        )
    
    return output_dir


async def send_requests_to_ars(
    uids: Sequence[str],
    messages: Sequence[dict],
    url: str,
    output_dir: str,
    num_concurrent_requests: int,
    progress: bool
):
    pbar = None if progress == False else tqdm(total=len(uids))
    coroutines = [
        send_request_to_ars(uid, msg, url, output_dir, pbar)
        for uid, msg in zip(uids, messages)
    ]
    await gather(*coroutines, limit=num_concurrent_requests)

    if pbar is not None:
        pbar.close()

async def send_request(uid: str, url: str, msg: dict, request_type: str = "post"):
    async with httpx.AsyncClient(timeout=None) as client:
        attempts = 0
        while True:
            response = None
            try:
                if request_type == "get":
                    response = await getattr(client, request_type)(url)
                else:
                    response = await getattr(client, request_type)(url, json=msg)
                response.raise_for_status()
                response_json = response.json()
                break
            except Exception as e:
                print(e)

                attempts += 1
                if attempts >= 3:
                    response_json = deepcopy(msg)
                    response_json['benchmarks'] = f'Fetch request failed {attempts} times.'
                    break

                print(f'Retrying in 5 seconds...')
                await asyncio.sleep(5)

    return response_json

async def send_request_to_ars(
    uid: str,
    msg: dict,
    url: str,
    output_dir: str,
    pbar: Optional[tqdm]
):
    # submit query to ARS
    response = await send_request(uid, f"{url}/submit", msg)
    # get parent pk
    parent_pk = response["pk"]

    # Get all children queries
    response = await send_request(uid, f"{url}/messages/{parent_pk}?trace=y", msg, request_type="get")

    start_time = time.time()
    for child in response.get("children", []):
        child_pk = child["message"]
        infores = child["actor"]["inforesid"].split("infores:")[1]
        current_time = time.time()
        # while we stay within the query max time
        while current_time - start_time <= MAX_QUERY_TIME:
            # get query status of child query
            response = await send_request(uid, f"{url}/messages/{child_pk}", msg, request_type="get")
            status = response.get("fields", {}).get("status")
            if status == "Done":
                break
            if status == "Error":
                # query errored, need to capture
                break
            current_time = time.time()
            await asyncio.sleep(5)
        
        # Store results
        Path(os.path.join(output_dir, infores)).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(output_dir, infores, f"{uid}.json"), "w") as file:
            json.dump(response, file)
    
    # After getting all individual ARA responses, get and save the merged version
    response = await send_request(uid, f"{url}/messages/{parent_pk}", msg, request_type="get")
    merged_pk = response.get("fields", {}).get("merged_version")
    if merged_pk is None:
        print(f"Failed to get the ARS merged message from pk: {parent_pk}.")
    else:
        merged_message = await send_request(uid, f"{url}/messages/{merged_pk}", msg, request_type="get")
        Path(os.path.join(output_dir, "ars")).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(output_dir, "ars", f"{uid}.json"), "w") as file:
            json.dump(merged_message, file)

    if pbar:
        pbar.update()


async def score_results(
    unscored_results_dir: str,
    target: str,
    scored_results_dir: str,
    num_concurrent_requests: int = 5,
    progress: bool = True
):
    """
    Scores results to all queries inside the specified unscored results
    directory and stores them in the specified scored results directory. Note
    that the "score" entry of the specified target must be provided in
    targets.json for this function to work.

    Args:
        benchmark (str): Path to the directory containing unscored results.
        target (str): Name of the target to score the queries against; see
            targets.json for a complete list of known targets.
        results_dir (str): Path to the directory to store scored results.
        num_concurrent_requests (int, default 5): Number of concurrent requests
            used to fetch queries from the target.
        progress (bool, default True): Whether or not to show a progress bar.
    """
    with open(CONFIG_DIR / 'targets.json') as file:
        targets_json = json.load(file)

    config = targets_json[target]['score']
    url = config['url']
    workflow = config.get('workflow', None)

    uids, messages = [], []
    unscored_results_dir = Path(unscored_results_dir)
    for file_path in unscored_results_dir.iterdir():
        if file_path.is_file():
            uids.append(file_path.stem)
            with open(file_path, 'r') as file:
                message = json.load(file)
            if workflow is not None:
                message['workflow'] = workflow
            messages.append(message)

    await send_requests_store_results(
        uids,
        messages,
        url,
        scored_results_dir,
        num_concurrent_requests,
        progress
    )

async def send_requests_store_results(
    uids: Sequence[str],
    messages: Sequence[dict],
    url: str,
    output_dir: str,
    num_concurrent_requests: int,
    progress: bool
):
    pbar = None if progress == False else tqdm(total=len(uids))
    coroutines = [
        send_request_store_result(uid, msg, url, output_dir, pbar)
        for uid, msg in zip(uids, messages)
    ]
    await gather(*coroutines, limit=num_concurrent_requests)
    
    if pbar is not None:
        pbar.close()

async def send_request_store_result(
    uid: str,
    msg: dict,
    url: str,
    output_dir: str,
    pbar: Optional[tqdm]
):
    # Make network call
    async with httpx.AsyncClient(timeout=None) as client:
        attempts = 0
        while True:
            response = None
            try:
                response = await client.post(url, json=msg)
                response.raise_for_status()
                response_json = response.json()
                Response.parse_obj(response_json)
            except Exception as e:
                print(e)
                if response is not None:
                    print(f'{response.status_code} {response.reason_phrase}')
                    print(uid)

                attempts += 1
                if attempts >= 3:
                    response_json = deepcopy(msg)
                    response_json['benchmarks'] = f'Fetch request failed {attempts} times.'
                    break

                print(f'Retrying in 5 seconds...')
                await asyncio.sleep(5)
                continue
            break

    # Store results
    with open(f'{output_dir}/{uid}.json', 'w') as file:
        json.dump(response_json, file)

    if pbar:
        pbar.update()
