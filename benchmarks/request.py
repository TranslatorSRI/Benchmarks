import asyncio
import json
from pathlib import Path
from typing import Optional, Sequence

import httpx
from tqdm import tqdm

from .utils.asyncio import gather
from .utils.benchmark import benchmark_messages
from .utils.constants import CONFIG_DIR


def fetch_results(
    benchmark: str,
    target: str,
    results_dir: str,
    overwrite: bool = True,
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
        overwrite: (bool, default True) Whether or not to overwrite existing
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
        uid_msgs = [
            (uid, msg) 
            for uid, msg in zip(uids, messages)
            if not (dir / f'{uid}.json').exists()
        ]
        uids, messages = tuple(zip(*uid_msgs))
                
    send_requests_store_results(
        uids,
        messages,
        url,
        results_dir,
        num_concurrent_requests,
        progress
    )

def score_results(
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

    send_requests_store_results(
        uids,
        messages,
        url,
        scored_results_dir,
        num_concurrent_requests,
        progress
    )

def send_requests_store_results(
    uids: Sequence[str],
    messages: Sequence[dict],
    url: str,
    results_dir: str,
    num_concurrent_requests: int,
    progress: bool
):
    pbar = None if progress == False else tqdm(total=len(uids))
    coroutines = [
        send_request_store_result(uid, msg, url, results_dir, pbar)
        for uid, msg in zip(uids, messages)
    ]
    asyncio.run(gather(*coroutines, limit=num_concurrent_requests))
    
    if pbar is not None:
        pbar.close()

async def send_request_store_result(
    uid: str,
    msg: dict,
    url: str,
    results_dir: str,
    pbar: Optional[tqdm]
):
    # Make network call
    async with httpx.AsyncClient(timeout=None) as client:
        while True:
            response = None
            try:
                response = await client.post(url, json=msg)
                response.raise_for_status()
            except:
                if response is not None:
                    print(f'{response.status_code} {response.reason_phrase}')
                    print(uid)
                print(f'Retrying in 5 seconds...')
                await asyncio.sleep(5)
                continue
            break

    # Store results
    with open(f'{results_dir}/{uid}.json', 'w') as file:
        json.dump(response.json(), file)

    if pbar:
        pbar.update()
