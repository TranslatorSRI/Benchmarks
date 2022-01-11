# MostPrescribed_2019

##Goal
A benchmark data set for returning drugs that treat an indication.  Here we suppose that the most prescribed drugs should be well represented.

##Data Description
The file "ConditionsToTopDrugs.txt" contains condition/drug pairs, one per row.  Each condition may have one or more drugs from the top 300 drugs list, ordered by their position in that list.  Each row lists the number of rows for each condition, as well as the rank of this row in those condition rows.   The conditions may be either by a disease or a phenotypic feature.

##Benchmarks
This data set is used to create the following benchmarks:

### Treats
A single hop query looking for small molecules connected to the indication via a treats predicate

### Related 
A single hop query looking for small molecules connected to the indication via a related_to predicate

### Ranking only


##Data Creation
The top 300 drugs from https://clincalc.com/DrugStats/Top300Drugs.aspx were cut and pasted into a data file (original_data.txt).  The original source is US Govt data, which ClinCalc cleans and releases under CC BY-SA 4.0.  At the time of retrieval (Jan 6 2022) the data was collected in 2019. 

The original data does not contain either indications or identifiers.  add_compound_ids.py uses nameresolver to find a putative identifier for the drug, and then sends that identifier to nodenorm to see if the roundtrip name is preserved.  The document is then hand edited to check and resolve any drug name/id problems.

Conditions and condition identifiers are added by hand at this point, using online sources including drugcentral and wikipedia.  parse_final.py reformats this table into "ConditionsToTopDrugs.txt".  


