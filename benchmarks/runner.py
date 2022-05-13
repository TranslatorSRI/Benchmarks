import asyncio
import json
from pathlib import Path

import httpx
from tqdm import tqdm

from .utils.asyncio import gather
from .utils.benchmark import benchmark_messages
from .utils.constants import CONFIG_DIR


def get_results(
    benchmark,
    target,
    results_dir,
    scored=True,
    num_concurrent_requests=5,
    progress=True
):
    uids, messages = benchmark_messages(benchmark)

    with open(CONFIG_DIR / 'targets.json') as file:
        targets_json = json.load(file)

    config = targets_json[target]['get' if scored else 'get_unscored']
    url = config['url']
    workflow = config.get('workflow', None)
    if workflow is not None:
        for message in messages:
            message['workflow'] = workflow
                
    send_requests_store_results(
        uids,
        messages,
        url,
        results_dir,
        num_concurrent_requests,
        progress
    )

def score_results(
    unscored_results_dir,
    target,
    scored_results_dir,
    num_concurrent_requests=5,
    progress=True
):
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
    uids,
    messages,
    url,
    results_dir,
    num_concurrent_requests,
    progress
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
    uid,
    msg,
    url,
    results_dir,
    pbar
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
