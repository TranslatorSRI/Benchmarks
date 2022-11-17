from benchmarks.request import fetch_results, score_results
from benchmarks.eval import evaluate_results
import os

##print(os.getcwd())
fetch_results('ameliorates', 'aragorn', 'unscored_results_dir', scored=False)
score_results('unscored_results_dir', 'aragorn', 'results_dir')
evaluate_results('ameliorates', 'results_dir')

