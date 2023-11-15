from argparse import ArgumentParser
import asyncio

from benchmarks_runner.request import score_results


def main():
    parser = ArgumentParser(description="Fetches results for a specific benchmark.")
    parser.add_argument(
        'unscored_results_dir',
        type=str,
        help='Directory containing unscored results.'
    )
    parser.add_argument(
        'target',
        type=str,
        help='Name of target to query; see targets.json for a list.'
    )
    parser.add_argument(
        'scored_results_dir',
        type=str,
        help='Directory where scored results will be stored.'
    )
    parser.add_argument(
        '--n',
        default=5,
        type=int,
        help='Number of concurrent requests.'
    )
    args = parser.parse_args()

    asyncio.run(score_results(
        args.unscored_results_dir,
        args.target,
        args.scored_results_dir,
        num_concurrent_requests=args.n
    ))
