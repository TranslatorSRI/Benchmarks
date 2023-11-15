# Translator Benchmarks

This repository provides a set of benchmarks as well as the code to send the queries and evaluate the returned results of a benchmark.

`benchmarks` contains the code to query targets and evaluate results.

`config` contains the data sets, query templates, targets, and benchmark definitions necessary to run a benchmark. See `config/README.md` for details about targets and benchmarks.

## Usage
Running a benchmark is a two-step process:
1. Execute the queries of a benchmark and store the scored results.
2. Evaluate the scored results against the set of ground-truth relevant results.

[Installation](#installation) of the `benchmarks` package provides access to the functions and command-line interface necessary to run benchmarks.
### CLI
The command-line interface is the easiest way to run a benchmark.

- `benchmarks_fetch`
    - Fetches (un)scored results given the name of a benchmark (specified in `config/benchmarks.json`), target (specified in `config/targets.json`), and a directory to store results.
    - By default, `benchmarks_fetch` fetches scored results using 5 concurrent requests. Run `benchmarks_fetch --help` for more details.

- `benchmarks_score`
    - Scores results given the name of a benchmark (specified in `config/benchmarks.json`), target (specified in `config/targets.json`), a directory containing unscored results, and a directory to store scored results.
    - By default, `benchmarks_score` uses 5 concurrent requests. Run `benchmarks_score --help` for more details.

- `benchmarks_eval`
    - Evaluates a set of scored results given the name of a benchmark (specified in `config/benchmarks.json`) and a directory containing scored results.
    - By default, the evaluation considers the top 20 results of each query, and plots are not generated. Run `benchmarks_eval --help` for more details.

### Functions
The CLI functionality is also available by importing functions from the `benchmarks` package.

```python
from benchmarks.request import fetch_results, score_results
from benchmarks.eval import evaluate_results

# Fetch unscored results
fetch_results('benchmark_name', 'target_name', 'unscored_results_dir', scored=False)

# Score unscored results
score_results('unscored_results_dir', 'target_name', 'results_dir')

# Evaluate scored results
evaluate_results('benchmark_name', 'results_dir OR results_dict')

```
See the documentation of each function for more information.


### Installation

Install the repository as an editable package using `pip`.

`pip install -e .`

## UI
These benchmarks come with a frontend for viewing the scored results.

### Installation
_Requires python 3.9._
- Create a python virtual environment: `python3.9 -m venv benchmark_venv`
- Activate your environment: `. ./benchmark_venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Start the frontend server: `python server.py`
- Open in your browser

## Benchmark Runner
The benchmarks can be installed from pypi and used as part of the Translator-wide automated testing.
- `pip install benchmarks-runner`
To run benchmarks:
```python
import asyncio
from benchmarks_runner import run_benchmarks

output = asyncio.run(run_benchmarks(<benchmark>, <target>))
```
where benchmark is the name of a benchmark that is specified in config/benchmarks.json, and a target that is specified in config/targets.json

### Sample Output
```
Benchmark: GTRx
Results Directory: /tmp/tmpaf10m9_q/GTRx/bte/2023-11-10_13-03-11
                        k=1     k=5     k=10    k=20
Precision @ k           0.0000  0.0500  0.0250  0.0125
Recall @ k              0.0000  0.2500  0.2500  0.2500
mAP @ k                 0.0000  0.0833  0.0833  0.0833
Top-k Accuracy          0.0000  0.2500  0.2500  0.2500
Mean Reciprocal Rank    0.08333333333333333
```
