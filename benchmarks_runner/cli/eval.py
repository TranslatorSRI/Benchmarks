from argparse import ArgumentParser
import base64
import io
from matplotlib import pyplot as plt
from pathlib import Path
import os


from benchmarks_runner.eval import evaluate_results

metrics_at_k = {
    'Precision @ k\t\t': 'precision_at_k',
    'Recall @ k\t\t': 'recall_at_k',
    'mAP @ k\t\t\t': 'mAP_at_k',
    'Top-k Accuracy\t\t': 'top_k_accuracy'
}

metrics = {
    'Mean Reciprocal Rank\t': 'mean_reciprocal_rank'
}

def evaluate_ara_results(
    benchmark,
    results_dir,
    k: int = 20,
    save_plots: bool = False,
    save_json: bool = False,
):
    results = evaluate_results(
        benchmark,
        results_dir,
        k=k,
    )
    imgs = {}

    if save_plots:
        plots_dir = Path(results_dir)
        assert plots_dir.exists(), f"{plots_dir} does not exist."

        results.plot_precision()
        plt.gcf().savefig(plots_dir / 'precision.png')
        with io.BytesIO() as buffer:
            plt.gcf().savefig(buffer, format="png")
            buffer.seek(0)
            imgs["precision"] = base64.b64encode(buffer.read()).decode()
        
        results.plot_recall()
        plt.gcf().savefig(plots_dir / 'recall.png')
        with io.BytesIO() as buffer:
            plt.gcf().savefig(buffer, format="png")
            buffer.seek(0)
            imgs["recall"] = base64.b64encode(buffer.read()).decode()
        
        results.plot_mAP()
        plt.gcf().savefig(plots_dir / 'mAP.png')
        with io.BytesIO() as buffer:
            plt.gcf().savefig(buffer, format="png")
            buffer.seek(0)
            imgs["mAP"] = base64.b64encode(buffer.read()).decode()

        results.plot_top_k_accuracy()
        plt.gcf().savefig(plots_dir / 'top_k_accuracy.png')
        with io.BytesIO() as buffer:
            plt.gcf().savefig(buffer, format="png")
            buffer.seek(0)
            imgs["top_k_accuracy"] = base64.b64encode(buffer.read()).decode()

    ks = [1, 5, 10, 20, 50, 100, 200, 500]
    while ks[-1] >= k:
        ks.pop()
    ks.append(k)

    if save_json:
        results.to_json(results_dir)

    output = [
        '',
        "Benchmark: {}".format(benchmark),
        "Results Directory: {}\n".format(results_dir),
        "\t\t\t{}".format('\t'.join(['k={}'.format(k) for k in ks]))
    ]

    # Append @k metrics
    for name, fn_name in metrics_at_k.items():
        output.append("{}{}".format(
            name,
            '\t'.join([f'{getattr(results, fn_name)(k):.4f}' for k in ks])
        ))
    output.append('')

    # Append other metrics
    for name, attribute in metrics.items():
        output.append('{}{}'.format(name, getattr(results, attribute)))
    output.append('')

    print("\n".join(output))
    return results.output_dict, imgs

def main():
    parser = ArgumentParser(description="Run a benchmark on a set of results.")
    parser.add_argument(
        'benchmark',
        type=str,
        help='Name of benchmark to run; see benchmarks.json for a list.'
    )
    parser.add_argument(
        'target',
        type=str,
        help='Name of target of query; see targets.json for a list.'
    )
    parser.add_argument(
        'results_dir',
        type=str,
        help='Directory containing results of the benchmark queries. Should be a timestamp folder.'
    )
    parser.add_argument(
        '--k',
        default=20,
        type=int,
        help='Number of results of each query to consider.'
    )
    parser.add_argument(
        '--plots',
        action='store_true',
        help='If true, save plots that visualize the results. Defaults to false.'
    )
    parser.add_argument(
        '--json',
        action='store_false',
        help='If true, save a JSON file summarizing evaluation. Defaults to true.'
    )
    args = parser.parse_args()

    if args.target == 'ars':
        # evaluate results for each ARA
        for ara in [ara for ara in os.listdir(args.results_dir) if os.path.isdir(args.results_dir)]:
            results_dir = os.path.join(args.results_dir, ara)
            evaluate_ara_results(args.benchmark, results_dir, args.k, args.plots, args.json)
    else:
        evaluate_ara_results(args.benchmark, args.results_dir, args.k, args.plots, args.json)
