import requests
from copy import deepcopy
import json
import os
from csv import DictReader

class SystemRunner:
    def __init__(self,url):
        self.url= url
    def syncquery(self,message):
        qurl = f'{self.url}/query'
        results = requests.post(qurl,json=message)
        print(results.status_code)
        return results.json()
    def run(self,message):
        return self.syncquery(message)

class AragornRunner(SystemRunner):
    def __init(self,url):
        super(url)
    def run(self,message):
        newmessage = deepcopy(message)
        newmessage['workflow'] = [{'id':'lookup'},{'id':'overlay_connect_knodes'},{'id':'score'}]
        return self.syncquery(newmessage)

class Accumulator:
    def __init__(self,name):
        self.test_name = name
        self.ntests = 0
        self.npass = 0
    def accumulate(self,result):
        self.ntests += 1
        if result:
            print('Pass')
            self.npass  += 1
        else:
            print('Fail')
    def generate_report(self):
        print(f'Ran {self.ntests} tests.')
        print(f'Passed {self.npass} tests.')

class TopNScorer:
    def __init__(self,bdef,data_map,case):
        #Where do we get the rank we must achieve?
        col_name = bdef["N_source_column"]
        #And what does that rank need to be?
        self.rank = int(case[col_name])
        #What node in the result graph do we need to look at and what should we find?
        output_nodes = data_map['node_mappings']['output']
        self.expected_node_mappings = { node_id: case[case_column] for node_id, case_column in output_nodes.items() }
    def score(self,response):
        results = response['message']['results']
        #Only look in the top N results for the hits
        success = { node_id: False for node_id in self.expected_node_mappings }
        for result in results[:min(self.rank,len(results))]:
            for node_id, expected_value in self.expected_node_mappings.items():
                print('Expected', expected_value)
                output_ids = [x['id'] for x in result['node_bindings'][node_id]]
                print('Found', output_ids)
                if expected_value in output_ids:
                    success[node_id] = True
        all_success = success.values()
        if False in all_success:
            return False
        return True

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
    with open(os.path.join(datadir,benchmark_definition['case_file']),'r') as inf:
        reader = DictReader(inf,delimiter='\t')
        for case in reader:
            message = template_message(query_template,data_map,case)
            yield message,TopNScorer(benchmark_definition,data_map,case)

def run_benchmark(benchmark_definition_file,runner):
    benchmark_dir = os.path.dirname(benchmark_definition_file)
    with open(benchmark_definition_file,'r') as inf:
        bdef = json.load(inf)
    result_accumulator = Accumulator(bdef['name'])
    test_generator = generate_tests(bdef,benchmark_dir)
    for test_message, scorer  in test_generator:
        result = runner.run(test_message)
        result_score = scorer.score(result)
        result_accumulator.accumulate(result_score)
    result_accumulator.generate_report()

if __name__ == '__main__':
    run_benchmark('MostPrescribed_2019/benchmarks/treats/benchmark_definition.json',AragornRunner('https://aragorn.renci.org/1.2'))