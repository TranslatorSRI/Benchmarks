from ast import Str
from asyncio.windows_events import NULL
from dataclasses import replace
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import csv

url='https://ojrd.biomedcentral.com/articles/10.1186/s13023-021-01923-0/tables/1'

r=requests.get(url)

soup=BeautifulSoup(r.content, 'html.parser')

table_soup=soup.find('table')

header_tags=table_soup.find_all('th')
headers=[header.text.strip() for header in header_tags]
data_rows=table_soup.find_all("tr")

def lookUp(input: Str ):
    if(len(input)==0):
        return '', ''
    inputUrl='https://name-resolution-sri.renci.org/lookup?string='+input+'&offset=0&limit=1'
    response=requests.post(inputUrl)
    jsonFile: dict
    jsonFile=response.json()
    if (len(jsonFile)==0):
        return "None", "None"
    else:
        for k,v in jsonFile.items():
            if (len(v)>=3):
                indices=(0,1,2)
                v=[v[i] for i in indices]
            return k, v

with open('woutout.tsv','w') as outf:
    tsv_writer = csv.writer(outf, delimiter='\t', lineterminator='\n')
    tsv_writer.writerow(["OriginalCondition", "ConditionID", "ConditionNames", "OriginalDrug", "DrugID", "DrugNames"])
    for row in data_rows:
        value=row.find_all('td')
        beautified_value=[dp.text.strip() for dp in value]
        if(len(beautified_value)!=0 ):
            originalDisease=str(beautified_value[1]).replace('\u2009', '')
            stringVal=urllib.parse.quote(str(beautified_value[1]))
            diseaseId, dieseaseName=lookUp(stringVal)
            originalDrug=str(beautified_value[2]).replace('\u2009', '')
            stringDrugVal=urllib.parse.quote(str(beautified_value[2]))
            stringDrugVal=stringDrugVal.replace("/", "%2F")
            drugId, drugName=lookUp(stringDrugVal)
            tsv_writer.writerow([originalDisease, diseaseId, dieseaseName, originalDrug, drugId, drugName])
            #Write out row into columns diesease identifier, first couple disease names, drug name, drug identifier                     



