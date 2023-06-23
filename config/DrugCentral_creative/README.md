# DrugCentral Creative Mode

##Goal
A benchmark data set for returning drugs that treat an indication.  Indications are drawn from DrugCentral.

##Data Description
DrugCentral provides ~10k indications for ~3000 drugs. `get_indications.py` retrieves these indications and parses out chemical and disease identifiers. It removes cases where one disease has many known drugs. It also samples 50 indications that it writes to `data.tsv`.

##Benchmarks
This data set is used to create the following benchmarks:

### Treats
A creative mode query looking for small molecules connected to the indication via a treats predicate


##Data Creation
created from DrugCentral via mychem.info using `get_indications.py`.
