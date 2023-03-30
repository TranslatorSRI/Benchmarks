"""Query Logger Backend Server."""
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import glob
import json
import os
import uvicorn

from pydantic import BaseModel
from typing import List, Dict

load_dotenv()

class Benchmark(BaseModel):
  __root__: Dict[str, List[str]]

class AvailableBenchmarksResponse(BaseModel):
  __root__: Dict[str, Benchmark]

class BenchmarkResults(BaseModel):
  __root__: Dict[str, Dict]


APP = FastAPI(
  title="Translator SRI Benchmark Tool UI",
  description="Visualize benchmark results from ARAs and the ARS",
  version="0.1.0",
  translator_teams=["SRI"],
  contact={
      "name": "Max Wang",
      "email": "max@covar.com",
      "x-id": "maxwang",
      "x-role": "responsible developer",
  },
)

@APP.get("/api/available_benchmarks")
async def get_available_benchmarks() -> AvailableBenchmarksResponse:
  """
    GET the file system results structure.

    {
      benchmark: {
        ara: [
          timestamp,
          timestamp,
        ],
        ara: [
          timestamp,
          timestamp,
        ],
        ars: [
          timestamp,
        ],
      },
      benchmark: {
        ara: [
          timestamp,
          timestamp,
        ],
        ara: [
          timestamp,
          timestamp,
        ],
        ars: [
          timestamp,
        ],
      }
    }
  """
  available_benchmarks = {}
  results_path = os.getenv("RESULTS_PATH", ".")
  benchmarks = glob.glob(os.path.join(results_path, "*"))
  for benchmark in benchmarks:
    targets = glob.glob(os.path.join(benchmark, "*"))
    benchmark_name = os.path.basename(os.path.normpath(benchmark))
    available_benchmarks[benchmark_name] = {}
    for target in targets:
      # TODO: do we treat the ars results differently?
      timestamps = glob.glob(os.path.join(target, "*"))
      target_name = os.path.basename(os.path.normpath(target))
      available_benchmarks[benchmark_name][target_name] = [
        os.path.basename(os.path.normpath(timestamp)) for timestamp in timestamps
      ]
  return available_benchmarks
  

@APP.get("/api/{benchmark}/{target}/{timestamp}")
async def get_benchmark_results(benchmark: str, target: str, timestamp: str) -> BenchmarkResults:
  """
    Get benchmark results.

    Return:
      {
        ara: {
          results
        },
        ara: {
          results,
        }
      }
  """
  results_path = os.getenv("RESULTS_PATH", ".")
  result_path = os.path.join(results_path, benchmark, target, timestamp)
  if target == "ars":
    ara_responses = {}
    aras = glob.glob(os.path.join(result_path, "*"))
    for ara in aras:
      ara_name = os.path.basename(os.path.normpath(ara))
      result_file = os.path.join(ara, "output.json")
      with open(result_file, "r") as f:
        result = json.load(f)
      ara_responses[f"ars-{ara_name}"] = result
    return ara_responses
  else:
    result_file = os.path.join(result_path, "output.json")
    with open(result_file, "r") as f:
      result = json.load(f)
    return {
      target: result
    }
  

# servers UI
APP.mount("/", StaticFiles(directory="ui/build/", html=True), name="ui")

if __name__ == "__main__":
  uvicorn.run("server:APP", port=8346, reload=True)
