import json
import pathlib

PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / 'config'

with open(CONFIG_DIR / 'benchmarks.json', 'r') as file:
    BENCHMARKS = json.load(file)
