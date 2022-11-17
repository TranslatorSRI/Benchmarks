from benchmarks.request import fetch_results, score_results
from benchmarks.eval import evaluate_results
import os

##print(os.getcwd())
fetch_results('treats_rare', 'aragorn', 'unscored_results_dir', scored=False)
score_results('unscored_results_dir', 'aragorn', 'results_dir')
evaluate_results('treats_rare', 'evaluated')

