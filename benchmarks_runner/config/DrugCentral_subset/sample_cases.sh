#!/bin/bash

# get header
head -1 ../DrugCentral_creative/data_full.tsv > data.tsv

# sample five random UMLS disease IDs
awk -F"\t" -v OFS="\t" '{print $4}' ../DrugCentral_creative/data_full.tsv | sort -u | shuf | head -5 | sort > selected_diseases.txt

# retrieve all records for those selected diseases
sort -t $'\t' -k4 ../DrugCentral_creative/data_full.tsv  > data_full_sorted.tsv
join -t $'\t' -1 1 -2 4 -o 2.1 2.2 2.3 2.4 2.5 2.6 selected_diseases.txt data_full_sorted.tsv >> data.tsv

# cleanup 
rm data_full_sorted.tsv 
