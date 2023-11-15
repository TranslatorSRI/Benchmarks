from argparse import ArgumentParser
import asyncio

from benchmarks_runner.request import fetch_results


def main():
    parser = ArgumentParser(description="Fetches results for a specific benchmark.")
    parser.add_argument(
        'benchmark',
        type=str,
        help='Name of benchmark to run; see benchmarks.json for a list.'
    )
    parser.add_argument(
        'target',
        type=str,
        help='Name of target to query; see targets.json for a list.'
    )
    parser.add_argument(
        'results_dir',
        type=str,
        help='Directory containing results of the benchmark queries.'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='If true, overwrites existing query results in results_dir.'
    )
    parser.add_argument(
        '--unscored',
        action='store_true',
        help='If true, fetches and stores unscored results.'
    )
    parser.add_argument(
        '--n',
        default=5,
        type=int,
        help='Number of concurrent requests.'
    )
    args = parser.parse_args()

    output_dir = asyncio.run(fetch_results(
        args.benchmark,
        args.target,
        args.results_dir,
        overwrite=args.overwrite,
        scored=not args.unscored,
        num_concurrent_requests=args.n
    ))

    print(f"Results saved to: {output_dir}")
