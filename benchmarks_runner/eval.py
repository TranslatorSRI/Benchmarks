
import collections.abc
import json
from itertools import zip_longest
from pathlib import Path
import os
from typing import Sequence, Tuple, Union
import warnings

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from benchmarks_runner.utils.benchmark import benchmark_ground_truth


def evaluate_results(
    benchmark: str,
    results_dir: Union[str, dict],
    k: int = 50,
    use_xref=True,
) -> 'BenchmarkResults':
    """
    Computes metrics on the query results associated with the specified
    benchmark. See BenchmarkResults for the complete list of metrics.

    Args:
        benchmark: (str) Name of the benchmark to run; see benchmarks.json for a
            complete list of benchmarks.
        results: (str or dict) Scored results to the queries associated with
            the specified benchmark. If str, path to the directory containing
            results. If dict, map from query UID to TRAPI-compliant message
            containing results.
        k: (int) Maximum number of results to consider for scoring.

    Returns:
        BenchmarkResults object with functions for getting and plotting metrics.
    """
    uids, ground_truths, normalizer = benchmark_ground_truth(benchmark)

    output_dict = {
        'k': k,
        'benchmark': {
            'name': benchmark,
            'num_queries': len(uids)
        },
        'metrics': {},
        'queries': {
            uid: {
                'precision_at_k': [],
                'recall_at_k': [],
                'average_precision_at_k': [],
                'relevant_result_ranks': []
            }
            for uid in uids
        }
    }

    total_num_relevant = 0
    tp_k = np.zeros(k)
    map_k = np.zeros(k)
    mrr = 0
    for uid, ground_truth in zip(uids, ground_truths):
        """
        `ground_truth` is a set of a list of (qnode_id, CURIE) pairs. Each list of 
        (qnode_id, CURIE) pairs defines a relevant result. A result is
        linked/matched to a list of (qnode_id, CURIE) pairs if the bound
        CURIE equals the ground truth CURIE for each (qnode_id, CURIE) pair.
        """
        message = {}

        if type(results_dir) is str:
            # Load precomputed result for this query
            result_path = Path(results_dir, f'{uid}.json')
            if not result_path.exists():
                warnings.warn(f'Results for query {uid} were not found in {results_dir}.')
            else:
                with open(result_path) as file:
                    response = json.load(file)
                    message = response.get('message', None)
                    if message is None:
                        # most likely came from the ARS
                        message = ((response.get('fields') or {}).get('data') or {}).get('message', {})
        elif type(results_dir) is dict:
            if uid not in results_dir:
                warnings.warn(f'Results for query {uid} were not found.')
            else:
                # Grab message from dict
                message = results_dir.get(uid, {}).get("message", {})

        results_k = sorted(
            message.get('results', []),
            key=lambda r: r['analyses'][0].get('score', 0),
            reverse=True
        )[:k]

        if use_xref:
            # Use the biolink:xref attribute to add additional aliases to the normalizer
            knowledge_graph = message.get("knowledge_graph", {})
            for curie, curie_info in knowledge_graph.get('nodes', {}).items():
                for attribute in curie_info.get('attributes', []):
                    if attribute.get('attribute_type_id', None) != 'biolink:xref':
                        continue
                    
                    aliases = set([curie] + [alias for alias in attribute.get('value', [])])
                    for alias in aliases:
                        if alias not in normalizer:
                            continue

                        for a in aliases:
                            normalizer[a] = normalizer[alias]
                        break

        uid_info = output_dict['queries'][uid]

        # Compute unpinned qnode_ids (aka template slot_ids)
        slot_ids = [slot_id for slot_id, _ in next(iter(ground_truth))]

        # Compute metrics for each query
        tp_count, ap_numerator = 0, 0
        num_relevant = len(ground_truth)
        ap_k = np.zeros(k)
        rr = 0
        for index, result in zip_longest(range(k), results_k):
            if result is not None:
                # Check if result is relevant
                node_bindings = result['node_bindings']
                # For now, only considers first CURIE bound to slot_id
                pred = [(slot_id, node_bindings[slot_id][0]['id']) for slot_id in slot_ids]
                normalized_pred = tuple(sorted((slot_id, normalizer.get(curie, curie)) for slot_id, curie in pred))
                if normalized_pred in ground_truth:
                    tp_count += 1
                    ap_numerator += tp_count / (index + 1)

                    if rr == 0:
                        rr = 1 / (index + 1)

                    uid_info['relevant_result_ranks'].append(index + 1)

                    # Remove result from ground_truth to prevent double counting
                    ground_truth.remove(normalized_pred)

            # Update once per result
            tp_k[index] += tp_count
            ap_k[index] = ap_numerator / min(index + 1, num_relevant)

            # Update output dict
            uid_info['precision_at_k'].append(tp_count / (index + 1))
            uid_info['recall_at_k'].append(tp_count / num_relevant)
            uid_info['average_precision_at_k'].append(ap_k[index])

        # Update once per UID
        total_num_relevant += num_relevant
        map_k += ap_k
        mrr += rr
    
    # Convert mAP @ k and MRR sums to means
    map_k /= len(uids)
    mrr /= len(uids)
    
    # Compute precision @ k and recall @ k
    k = np.arange(1, len(tp_k) + 1)
    p_k = tp_k / (k * len(uids))
    r_k = tp_k / total_num_relevant

    # Update output_dict
    metrics =  output_dict['metrics']
    metrics['precision_at_k'] = p_k.tolist()
    metrics['recall_at_k'] = r_k.tolist()
    metrics['mean_average_precision_at_k'] = map_k.tolist()
    metrics['top_k_accuracy'] = r_k.tolist()
    metrics['mean_reciprocal_rank'] = mrr
    output_dict['benchmark']['num_relevant_results'] = total_num_relevant

    return BenchmarkResults(k, p_k, r_k, map_k, r_k, mrr, output_dict) 


class BenchmarkResults:
    """
    Object that contains functions for getting and plotting metrics.
    
    Metrics:

    Precision @ k
        Out of the top-k results, what fraction of them are relevant?
            Single query:
                `Number of relevant results (in top-k) / k`
            Multiple queries: 
                `Number of relevant results (in top-k) / (Number of queries * k)`
    
    Recall @ k 
        Out of all relevant results, what fraction of them are in the top-k?
            Single query:
                `Number of relevant results (in top-k) / Number of relevant results`
            Multiple queries: 
                `Total number of relevant results (in top-k) / Total number of relevant results`

    Mean Average Precision (mAP) @ k
        Average Precision @ k, averaged over all queries. Intuitively, mAP @ k
        is similar to Precision @ k, but it factors in the ranking of the
        relevant results (better ranking of relevant results -> higher mAP).

    Top-k Accuracy
        The fraction of instances where the correct result is among the top-k
        results.
        
        Note that this metric requires a "correct" result (only 1
        relevant result), so it treats each row in the data (aka each relevant
        result) as a separate data case. As a result, this metric will count
        queries that have `n` relevant results `n` times. This metric is useful
        when the queries each have a small number of relevant results.

        Note that Top-k Accuracy is equal to Recall @ k under this definition.

    Mean Reciprocal Rank
        Reciprocal of the rank of the first relevant result, averaged over all
        queries.

        Equivalently, MRR is the reciprocal of the harmonic mean (across all
        queries) of the rank of the first relevant result.
    """
    def __init__(self, k, p_k, r_k, map_k, top_k_acc,  mrr, output_dict):
        self.k = k
        self.p_k = p_k
        self.r_k = r_k
        self.map_k = map_k
        self.top_k_acc = top_k_acc
        self.mrr = mrr
        self.output_dict = output_dict

    def _metric_at_k(self, metric: str, k: Union[int, Sequence[int]]) -> float:
        if isinstance(k, collections.abc.Sequence):
            k = np.array(k)
        return getattr(self, metric)[k - 1]

    def precision_at_k(self, k: Union[int, Sequence[int]]) -> float:
        """
        Computes the Precision @ k.
        
        Args:
            k: (int) Number of results to consider for Precision @ k.

        Returns:
            Precision @ k (float)
        """
        return self._metric_at_k('p_k', k)

    def recall_at_k(self, k: Union[int, Sequence[int]]) -> float:
        """
        Computes the Recall @ k.
        
        Args:
            k: (int) Number of results to consider for Recall @ k.

        Returns:
            Recall @ k (float)
        """
        return self._metric_at_k('r_k', k)

    def mAP_at_k(self, k: Union[int, Sequence[int]]) -> float:
        """
        Computes the mAP @ k
        
        Args:
            k: (int) Number of results to consider for mAP @ k.

        Returns:
            mAP @ k (float)
        """
        return self._metric_at_k('map_k', k)

    def top_k_accuracy(self, k: Union[int, Sequence[int]]) -> float:
        """
        Computes the Top-k Accuracy.
        
        Args:
            k: (int) Number of results to consider for Top-k Accuracy.

        Returns:
            Top-k Accuracy (float)
        """
        return self._metric_at_k('top_k_acc', k)

    def _plot_metric(self, x_field: str, y_field: str, ax: Axes, label: str = None, xlabel: str = None, ylabel: str = None, xlim: Tuple[int] = None, ylim: Tuple[int] = None) -> Axes:
        x = getattr(self, x_field)
        y = getattr(self, y_field)

        if ax is None:
            _, ax = plt.subplots(figsize=(8, 6))

        ax.plot(x, y, label=label)

        ax.grid(which="both", alpha=0.4)
        if label is not None:
            ax.legend()
        ax.autoscale(True)

        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)

        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

        return ax

    def plot_precision(self, ax: Axes = None, label: str = None) -> Axes:
        self._plot_metric('k', 'p_k', ax, label=label, xlabel='$k$', ylabel='Precision @ $k$', ylim=(0,1))

    def plot_recall(self, ax: Axes = None, label: str = None) -> Axes:
        self._plot_metric('k', 'r_k', ax, label=label, xlabel='$k$', ylabel='Recall @ $k$', ylim=(0,1))

    def plot_mAP(self, ax: Axes = None, label: str = None) -> Axes:
        self._plot_metric('k', 'map_k', ax, label=label, xlabel='$k$', ylabel='mAP @ $k$', ylim=(0,1))

    def plot_top_k_accuracy(self, ax: Axes = None, label: str = None) -> Axes:
        self._plot_metric('k', 'top_k_acc', ax, label=label, xlabel='$k$', ylabel='Top-$k$ Accuracy', ylim=(0,1))

    def to_json(self, output_dir, indent=4):
        output_path = os.path.join(output_dir, "output.json")
        with open(output_path, 'w') as file:
            json.dump(self.output_dict, file, indent=indent)

    @property
    def mean_reciprocal_rank(self):
        return self.mrr





    