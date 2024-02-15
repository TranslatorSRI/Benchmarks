###
###  get_indications.py
###
###  This program will use mychem.info to download drug indications from DrugCentral
###  

from biothings_client import get_client
import pandas as pd

mc = get_client("chem")
drugs = mc.query(
        "_exists_:drugcentral.drug_use.indication", 
        fields="drugcentral.drug_use.indication,drugcentral.xrefs,drugcentral.synonyms", 
        fetch_all=True)

df = pd.DataFrame(columns=['_id', 'chebi', 'drug_umls', 'disease_umls', 'drug_name', 'disease_name' ])

count = 0
for drug in drugs:
    count = count + 1
#    if(count > 50):
#        break;

    _id = drug['_id']

    # skip if drug central is list -- unusual case?
    if(isinstance(drug['drugcentral'], list)):
        continue

    ### Parse drug names
    if(isinstance(drug['drugcentral']['synonyms'], list)):
        synonyms = ",".join(drug['drugcentral']['synonyms'])
    else:
        synonyms = drug['drugcentral']['synonyms']
#    print(synonyms)

    ### Parse xrefs
    if 'chebi' in drug['drugcentral']['xrefs'].keys():
        if isinstance(drug['drugcentral']['xrefs']['chebi'], list):
            continue
        chebi = drug['drugcentral']['xrefs']['chebi']
    else:
        chebi = ''
        ### for the moment, skip entries with no ChEBI ID
        continue
    
    if 'umlscui' in drug['drugcentral']['xrefs'].keys():
        if isinstance(drug['drugcentral']['xrefs']['umlscui'], list):
            continue
        drug_umls = "UMLS:"+drug['drugcentral']['xrefs']['umlscui']
    else:
        drug_umls = ''

    ### Parse indications
    if isinstance(drug['drugcentral']['drug_use']['indication'], list):
        for ind in drug['drugcentral']['drug_use']['indication']:
            if 'umls_cui' in ind.keys():
#                print(ind['umls_cui'] + ": " + ind['concept_name'])
                disease_umls = "UMLS:"+ind['umls_cui']
                disease_name = ind['concept_name']
                new_record = {
                        '_id': _id,
                        'drug_name': synonyms,
                        'chebi': chebi,
                        'drug_umls': drug_umls,
                        'disease_umls': disease_umls,
                        'disease_name': disease_name
                        }
#                print(new_record)
                df.loc[len(df)] = new_record
    else:
        ind = drug['drugcentral']['drug_use']['indication']
        if 'umls_cui' in ind.keys():
#            print(ind['umls_cui'] + ": " + ind['concept_name'])
            disease_umls = "UMLS:"+ind['umls_cui']
            disease_name = ind['concept_name']
            new_record = {
                    '_id': _id,
                    'drug_name': synonyms,
                    'chebi': chebi,
                    'drug_umls': drug_umls,
                    'disease_umls': disease_umls,
                    'disease_name': disease_name
                    }
#            print(new_record)
            df.loc[len(df)] = new_record

### sort the data file 
df = df.sort_values('_id')

### export full data file
df.to_csv("data_full.tsv", sep="\t", index=False)

### restrict to indications where there is only one drug listed for a disease
df = df.drop_duplicates('disease_umls', keep=False)

### sample a set of 50 records
df = df.sample(n=50, random_state=42)

### export
df.to_csv("data.tsv", sep="\t", index=False)
