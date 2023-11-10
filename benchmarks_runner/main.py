"""Main Benchmarks Test Runner entry."""
import asyncio
import os
import tempfile

from benchmarks_runner.request import fetch_results
from benchmarks_runner.cli.eval import evaluate_ara_results


async def run_benchmarks(
    benchmark: str,
    target: str,
):
    """Run benchmark tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = await fetch_results(benchmark, target, tmpdir)
        output_dict = {}
        output_imgs = {}
        if target == 'ars':
            # evaluate results for each ARA
            for ara in [ara for ara in os.listdir(output_dir) if os.path.isdir(output_dir)]:
                results_dir = os.path.join(output_dir, ara)
                ara_output_dict, ara_imgs = evaluate_ara_results(benchmark, results_dir, save_plots=True)
                output_imgs[ara] = ara_imgs
        else:
            output_dict, imgs = evaluate_ara_results(benchmark, output_dir, save_plots=True)
            output_imgs[target] = imgs

    return output_dict, imgs


if __name__ == "__main__":
    asyncio.run(run_benchmarks(
        "ameliorates",
        "aragorn",
    ))
