
import collections.abc
from itertools import zip_longest
import json
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from typing import Sequence, Tuple, Union

from benchmarks.utils.benchmark import benchmark_ground_truth

def evaluate_results(benchmark: str, results_dir: str, k: int = 50) -> 'BenchmarkResults':
    """
    Computes metrics on the query results associated with the specified
    benchmark. See BenchmarkResults for the complete list of metrics.

    Args:
        benchmark: (str) Name of the benchmark to run; see benchmarks.json for a
            complete list of benchmarks.
        reuslts_dir: (str) Path to the directory containing scored results to
            to the queries associated with the specified benchmark.
        k: (int) Maximum number of results to consider for scoring.

    Returns:
        BenchmarkResults object with functions for getting and plotting metrics.
    """
    uids, gts = benchmark_ground_truth(benchmark)
    results_dir = Path(results_dir)

    total_num_relevant = 0
    tp_k = np.zeros(k)
    map_k = np.zeros(k)
    mrr = 0
    for uid, gt in zip(uids, gts):
        """
        `gt` is a set of a list of (qnode_id, CURIE) pairs. Each list of 
        (qnode_id, CURIE) pairs defines a relevant result. A result is
        linked/matched to a list of (qnode_id, CURIE) pairs iff the bound
        CURIE equals the ground truth CURIE for each (qnode_id, CURIE) pair.
        """
        # Load precomputed result for this query
        result_path = results_dir / f'{uid}.json'
        if not result_path.exists():
            raise Exception(
                f'Results for query {uid} were not found in {results_dir}'
            )
        with open(result_path) as file:
            results = json.load(file)['message']['results'][:k]

        # Compute unpinned qnode_ids (aka template slot_ids)
        slot_ids = [slot_id for slot_id, _ in next(iter(gt))]

        # Compute metrics for each result
        tp_count, ap_numerator = 0, 0
        num_relevant = len(gt)
        ap_k = np.zeros(k)
        rr = 0
        for index, result in zip_longest(range(k), results):
            if result is not None:
                # Check if result is relevant
                node_bindings = result['node_bindings']
                pred = tuple(sorted([(slot_id, node_bindings[slot_id][0]['id']) for slot_id in slot_ids])) # [0] only considers first CURIE bound to slot_id
                if pred in gt:
                    tp_count += 1
                    ap_numerator += tp_count / (index + 1)

                    if rr == 0:
                        rr = 1 / (index + 1)

                    # Remove result from gt to prevent double counting
                    gt.remove(pred)

            # Update once per result
            tp_k[index] += tp_count
            ap_k[index] = ap_numerator / min(index + 1, num_relevant)

        # Update once per UID
        total_num_relevant += num_relevant
        map_k += ap_k
        mrr += rr
    
    # Convert sums to means
    map_k /= len(uids)
    mrr /= len(uids)

    return BenchmarkResults(tp_k, map_k, mrr, total_num_relevant, len(uids)) 


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
    def __init__(self, tp_k, map_k, mrr, num_relevant, num_queries):
        self.k = np.arange(1, len(tp_k) + 1)
        self.p_k = tp_k / (self.k * num_queries)
        self.r_k = tp_k / num_relevant
        self.map_k = map_k
        self.top_k_acc = self.r_k
        self.mrr = mrr

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
            ax.legend(loc="lower right")
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

    @property
    def mean_reciprocal_rank(self):
        return self.mrr





    