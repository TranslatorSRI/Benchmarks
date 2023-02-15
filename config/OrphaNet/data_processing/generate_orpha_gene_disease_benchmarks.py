import csv
import requests
import xmltodict

# use this if loading data from raw xml file (up-to-date as of 2/15/2023)
# with open('../en_product6.xml') as xml_file:
#    data_dict = xmltodict.parse(xml_file.read())

# us this if extracting from link from http://www.orphadata.org/cgi-bin/index.php
# Note, that file name is likely to change for newer versions and will require updating
r = requests.get('http://www.orphadata.org/data/xml/en_product6.xml')
data_dict = xmltodict.parse(r.content)

x = [['Disease_Curie', 'Disease_Name', 'Gene_Curie', 'Gene_Name']]
for data in data_dict['JDBOR']['DisorderList']['Disorder']:
    orpha_code = 'ORPHANET:{}'.format(data['OrphaCode'])
    orpha_name = data['Name']['#text']
    associations = data['DisorderGeneAssociationList']['DisorderGeneAssociation']
    if type(associations) is not list:
        associations = [associations]
        for association in associations:
            gene_name = association['Gene']['Name']['#text']
            references = association['Gene']['ExternalReferenceList']['ExternalReference']
            found = False
            if type(references) is not list:
                references = [references]
            for reference in references:
                if reference['Source'] == 'Ensembl':
                    gene_curie = 'ENSEMBL:{}'.format(reference['Reference'])
                    x.append([orpha_code, orpha_name, gene_curie, gene_name])
                    found = True
                    break
with open('../data.tsv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(x)

