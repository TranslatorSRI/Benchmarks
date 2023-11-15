
import csv
import json
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Sequence, Tuple

from benchmarks_runner.utils.constants import BENCHMARKS, CONFIG_DIR

from .normalize import get_normalizer


def get_uid(source: str, template: str, datum: Dict[str, str], message: dict):
    """
    Computes the UID of a query, which is based on its (1) source, (2) query
    template, and (3) the CURIEs that fill the template slots.

    The UID has this form:

    `{source}.{template}.{CURIEs_in_template_slots}`

    where

    `CURIEs_in_template_slots` is a string made up of the CURIEs fitted into the
    template slots separated by a periods in the order they appear. For example,
    if `n0` and `n1` are the slots of some template, then

    `{ "n0": {ids: ["MONDO:1234"]}, "n1": {ids: ["MONDO:4321"]} }`

    will use `MONDO:1234.MONDO:4321` for `CURIEs_in_template_slots`.

    Args:
        source: (str) The source of the query - e.g., DrugMechDB,
            MostPrescribed_2019
        template: (str) Name of one of the templates applicable to the source.
        datum: (dict) map from qnode_ids to CURIEs of this datum 
        message: (dict) Message containing the query graph. Since `datum`
            contains CURIE information, `message` can also be an empty template.

    Returns:
        uid (str)
    """
    qnodes = message['message']['query_graph']['nodes']
    curies = [
        datum[qnode_id]
        for qnode_id in datum
        if 'ids' in qnodes.get(qnode_id, tuple())
    ]
    return f'{source}.{template}.{".".join(curies)}'

def benchmark_uids(benchmark: str) -> List[str]:
    """
    For each query in the specified benchmark, compute its UID.

    Args:
        benchmark: (str) Name of the benchmark. Benchmark names are listed in
            `benchmark.json`.
    
    Returns:
        UIDs of each query in the benchmark.
    """
    uids = set()
    for source_dict in BENCHMARKS[benchmark]:
        source_dir = CONFIG_DIR / source_dict['source']

        # Load data
        with open(source_dir / 'data.tsv' ,'r') as file:
            reader = csv.reader(file, delimiter='\t')
            qnode_ids = next(reader)
            data = list(reader)

        # Load query templates
        templates = []
        templates_dir = source_dir / 'templates'
        for template in source_dict['templates']:
            with open(templates_dir / f'{template}.json', 'r') as file:
                templates.append((template, json.load(file)))

        # Prepare messages using data and templates
        for template, template_dict in templates:
            for datum in data:
                datum_dict = {
                    qnode_id: curie for qnode_id, curie in zip(qnode_ids, datum)
                }
                uid = get_uid(source_dict['source'], template, datum_dict, template_dict)
                uids.add(uid)

    return sorted(uids)

def benchmark_messages(benchmark: str) -> Tuple[List[str], List[dict]]:
    """
    For each query in the specified benchmark, compute its UID and message
    (containing the query graph).

    Args:
        benchmark: (str) Name of the benchmark. Benchmark names are listed in
            `benchmark.json`.
    
    Returns:
        (uids, messages)
            uids: UIDs of each query in the benchmark.
            messages: messages (as a dict) of each query in the benchmark.
    """
    messages = {}
    for source_dict in BENCHMARKS[benchmark]:
        source_dir = CONFIG_DIR / source_dict['source']

        # Load data
        with open(source_dir / 'data.tsv' ,'r') as file:
            reader = csv.reader(file, delimiter='\t')
            qnode_ids = next(reader)
            data = list(reader)

        # Load query templates
        templates = []
        templates_dir = source_dir / 'templates'
        for template in source_dict['templates']:
            with open(templates_dir / f'{template}.json', 'r') as file:
                templates.append((template, json.load(file)))

        # Prepare messages using data and templates
        # NOTE: If memory ever becomes an issue, make this a generator that yields messages
        for template, template_dict in templates:
            for datum in data:
                datum_dict = {
                    qnode_id: curie for qnode_id, curie in zip(qnode_ids, datum)
                }
                # Skip duplicate queries
                uid = get_uid(source_dict['source'], template, datum_dict, template_dict)
                if uid in messages:
                    continue

                # Fill message template with CURIEs
                message = deepcopy(template_dict)
                nodes = message['message']['query_graph']['nodes']
                for qnode_id, curie in zip(qnode_ids, datum):
                    if qnode_id in nodes and 'ids' in nodes[qnode_id]:
                        nodes[qnode_id]['ids'].append(curie)
                messages[uid] = message

    return list(messages.keys()), list(messages.values())

def benchmark_ground_truth(benchmark: str) -> Tuple[List[str], List[dict], Dict[str, str]]:
    """
    For each query in the specified benchmark, compute its UID and the set of
    (qnode_id, CURIE) pairs for each unpinned qnode, which is need to discern
    whether a result is relevant or not.

    Args:
        benchmark: (str) Name of the benchmark. Benchmark names are listed in
            `benchmark.json`.
    
    Returns
        (uids, gts, normalizer)
            uids: UIDs of each query in the benchmark.
            ground_truths: set of a list of tuple pairs (qnode_id, CURIE) that represent
                the set of relevant results.
            normalizer: Map from CURIEs to the equivalent, preferred CURIE
                representing the same entity (from Node Normalizer).
    """
    uid_ground_truths = defaultdict(list)
    curies = []
    for source in BENCHMARKS[benchmark]:
        source_dir = CONFIG_DIR / source['source']

        # Load data
        with open(source_dir / 'data.tsv' ,'r') as file:
            reader = csv.reader(file, delimiter='\t')
            qnode_ids = next(reader)
            data = list(reader)

        # Load query templates
        templates = []
        templates_dir = source_dir / 'templates'
        for template in source['templates']:
            with open(templates_dir / f'{template}.json', 'r') as file:
                templates.append((template, json.load(file)))

        # Prepare messages using data and templates
        for template, template_dict in templates:
            qnodes = template_dict['message']['query_graph']['nodes']
            slot_ids = [
                qnode_id
                for qnode_id, qnode in qnodes.items()
                if 'ids' not in qnode and qnode_id in qnode_ids
            ]
            for datum in data:
                datum_dict = {
                    qnode_id: curie for qnode_id, curie in zip(qnode_ids, datum)
                }
                uid = get_uid(source['source'], template, datum_dict, template_dict)
                ground_truth = [(slot_id, datum_dict[slot_id]) for slot_id in slot_ids]
                uid_ground_truths[uid].append(ground_truth)
                curies.extend([datum_dict[slot_id] for slot_id in slot_ids])

    # Normalize CURIEs and put the results in a set (for quick contains check)
    normalizer = get_normalizer(curies)
    uids, ground_truths = [], []
    for uid, ground_truth in uid_ground_truths.items():
        uids.append(uid)
        results = set()
        for result in ground_truth:
            results.add(tuple(sorted([(slot_id, normalizer.get(curie, curie)) for slot_id, curie in result])))
        ground_truths.append(results)

    return uids, ground_truths, normalizer
