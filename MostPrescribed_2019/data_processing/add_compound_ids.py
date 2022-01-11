import requests

def lookup(name):
    url = f'https://name-resolution-sri.renci.org/lookup?string={name}&offset=0&limit=1'
    result =  requests.post(url).json()
    ids =  list(result.keys())
    if len(ids) > 0:
        return ids[0]
    return ''

def add_ids_from_label():
    with open('source_data.txt','r') as inf, open('drugs_with_ids','w') as outf:
        _ = inf.readline()
        outf.write(f'drugname\tdrug_id\n')
        for line in inf:
            drugname = line.split('\t')[1]
            drug_id = lookup(drugname)
            print( drugname, drug_id )
            outf.write(f'{drugname}\t{drug_id}\n')

def add_round_trip():
    ids = []
    with open('drugs_with_ids','r') as inf:
        _ = inf.readline()
        for line in inf:
            x = line.strip().split('\t')
            if len(x) != 2:
                print(x)
            else:
                ids.append(x[1])
    url = 'https://nodenormalization-sri.renci.org/get_normalized_nodes'
    results = requests.post(url,json={"curies":ids}).json()
    with open('drugs_with_ids','r') as inf, open('drugs.txt','w') as outf:
        _ = inf.readline()
        outf.write('OriginalName\tID\tRoundtripName\tMatch\n')
        for line in  inf:
            x = line.strip().split('\t')
            if len(x) == 1:
                outf.write('x[0]\t\t\tFalse\n')
            else:
                try:
                    label = results[x[1]]['id']['label']
                    outf.write(f'{x[0]}\t{x[1]}\t{label}\t{label==x[0]}\n')
                except KeyError:
                    import json
                    print(json.dumps(results[x[1]],indent=4))
                    exit()
    

if __name__ == '__main__':
    #add_ids_from_label()
    add_round_trip()
