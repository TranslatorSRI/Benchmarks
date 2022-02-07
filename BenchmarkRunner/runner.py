import requests
from copy import deepcopy
import json
import os
from csv import DictReader
from collections import defaultdict
import argparse

class SystemRunner:
    def __init__(self,configfile):
        with open(configfile,'r') as inf:
            config = json.load(inf)
        self.url= config['url']
        if 'workflow' in config:
            self.workflow = config['workflow']
        else:
            self.workflow = None
        self.result_cache = {}
    def syncquery(self,message):
        #We are going to cache results to this endpoint so we don't ask the same question over and over
        # when we have multiple results we are looking for.
        #This is memory inefficient.  It would probably be smarter to group the queries ahead of time
        smess = json.dumps(message,sort_keys=True,indent = 4)
        if smess in self.result_cache:
            return self.result_cache[smess]
        qurl = f'{self.url}/query'
        results = requests.post(qurl,json=message)
        j = results.json()
        self.result_cache[smess] = j
        return j
    def run(self,message):
        newmessage = deepcopy(message)
        if self.workflow is not None:
            newmessage['workflow'] = self.workflow
        return self.syncquery(newmessage)
    def dump_cache(self):
        i = 0
        for k,v in self.result_cache.items():
            with open(f'result_{i}.json','w') as outf:
                json.dump(v,outf,indent=4)
            i += 1

class Accumulator:
    def __init__(self,name):
        self.test_name = name
        self.ranks = []
    def accumulate(self,result_found,result_rank):
        if not result_found:
            self.ranks.append(False)
        else:
            self.ranks.append(result_rank)
    def generate_report(self):
        for rank in self.ranks:
            print(rank)


class Scorer:
    def __init__(self,bdef,data_map,case):
        #Where do we get the rank we must achieve?
        self.rank = int(bdef['N'])
        #What node in the result graph do we need to look at and what should we find?
        output_nodes = data_map['node_mappings']['output']
        self.expected_node_mappings = { node_id: case[case_column] for node_id, case_column in output_nodes.items() }
    def score(self,response):
        results = response['message']['results']
        #First pull the relevant parts of all results.  The important part might show up in more than one result
        results_to_rank = defaultdict(list)
        for rank,result in enumerate(results):
            #if there are multiple knodes per qnode, this will be wrong
            found_node_mappings = {node_id: [x['id'] for x in result['node_bindings'][node_id]][0] for node_id in self.expected_node_mappings}
            js = json.dumps(found_node_mappings,sort_keys=True)
            results_to_rank[js].append(rank+1)
        #for j,n in results_to_rank.items():
        #    print(f'Result: {j}')
        #    print(n)
        e = json.dumps(self.expected_node_mappings,sort_keys=True)
        print('looking for',e)
        if e not in results_to_rank:
            print('Not found')
            return False,0
        rank = min(results_to_rank[e])
        print(f'Found at rank {rank}')
        return True,rank

def template_message(query_template, data_map, case):
    q = deepcopy(query_template)
    for node_id, case_header in data_map['node_mappings']['input'].items():
        input_id = case[case_header]
        q['message']['query_graph']['nodes'][node_id]['ids']=[input_id]
    return q

def generate_tests(benchmark_definition,benchmark_dir):
    assert benchmark_definition['constructor_type'] == 'query'
    with open(os.path.join(benchmark_dir,benchmark_definition['query_file']),'r') as inf:
        query_template = json.load(inf)
    with open(os.path.join(benchmark_dir,benchmark_definition['mapping_file']),'r') as inf:
        data_map = json.load(inf)
    datadir = os.path.join(benchmark_dir.split('/')[0],'Data')
    mx = 3
    n=0
    with open(os.path.join(datadir,benchmark_definition['case_file']),'r') as inf:
        reader = DictReader(inf,delimiter='\t')
        for case in reader:
            if n < mx:
                message = template_message(query_template,data_map,case)
                n += 1
                yield message,Scorer(benchmark_definition,data_map,case)
            else:
                break
    print('all done')

def run_benchmark(benchmark_definition_file,runner):
    benchmark_dir = os.path.dirname(benchmark_definition_file)
    with open(benchmark_definition_file,'r') as inf:
        bdef = json.load(inf)
    result_accumulator = Accumulator(bdef['name'])
    test_generator = generate_tests(bdef,benchmark_dir)
    for test_message, scorer  in test_generator:
        result = runner.run(test_message)
        found, result_score = scorer.score(result)
        result_accumulator.accumulate(found, result_score)
    runner.dump_cache()
    result_accumulator.generate_report()

def handle_args():
    parser = argparse.ArgumentParser(description='Run queries to produce unscored results')
    parser.add_argument('--defs', type=str, nargs='+', help='Paths to benchmark_definition')
    parser.add_argument('--runners', type=str, nargs='+', help='Paths to runner configurations')
    args = parser.parse_args()
    return args

def run(args):
    defs = args.defs
    runconfigs = args.runners
    runners = [ SystemRunner(runconfig) for runconfig in runconfigs ]
    for bench_def in defs:
        #er, right now, just use the first runner...
        run_benchmark(bench_def,runners[0])

if __name__ == '__main__':
    #python BenchmarkRunner/runner.py --defs MostPrescribed_2019/benchmarks/treats/benchmark_definition.json
    run(handle_args())

#if __name__ == '__main__':
#    run_benchmark('MostPrescribed_2019/benchmarks/treats/benchmark_definition.json',AragornRunner('http://aragorn-dev.apps.renci.org/1.2'))