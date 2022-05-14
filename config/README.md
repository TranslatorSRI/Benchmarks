# Benchmark Config

A benchmark is a collection of queries and their corresponding relevant results.

Queries within a benchmark often share the same graph structure, so we store each query in two parts. The structure of each query is stored as a template, which describes the query graph explicitly in the TRAPI format, excluding the CURIEs. The CURIEs of each query are stored in a tabular format, where each row in a data table contains the CURIEs used to build the query. 

Each benchmark is described by the (1) the sources (data tables) and (2) the query templates used to build its queries.

# Overview

## Directory Structure
```
config/
├── source_1/
│   ├── templates/
│   │   ├── template_1.json
│   │   ├── template_2.json
│   │   └── ...
│   └── data.tsv
├── source_2/
│   ├── templates/
│   │   └── ...
│   └── data.tsv
├── ...
├── benchmarks.json
└── targets.json
```
## Sources
Benchmarks consist of queries from one or more sources. Each source has its own data table `data.tsv` and set of query templates inside the `templates` directory.

### `data.tsv`
Each row of the data table describes a set of related CURIEs. The known relationship between columns of `data.tsv` is utilized by the source's templates to generate queries.

### `templates`
Each file inside the `templates` directory is a query template, which describes a query graph explicitly in the TRAPI format, excluding the CURIEs. At runtime, the template is populated with CURIEs from a row of `data.tsv`, resulting in a TRAPI-compliant query.

## `benchmarks.json`
Each entry in `benchmarks.json` corresponds to a benchmark, which consists of one or more query templates each from one or more sources. For each query template, a query is generated for each row in its source's `data.tsv`.

## `targets.json`
Each entry in `targets.json` describes a query target - e.g., ARAGORN, ARAX, BTE - and provides the URL (and optionally the workflow) needed to fetch results.

# Usage

## Add a Source
1. Create a directory in `config`
2. Create `data.tsv` inside this directory. The first row should contain named column headers. Every other row should containsets of related CURIEs.
3. Create a directory named `templates` inside this directory. Add query templates following [Add a Query Template](##add-a-query-template).

## Add a Query Template
Create a TRAPI-compliant message containing a query graph without CURIEs, and store it in the `templates` directory. For the query runner to populate the query template, each query graph node identifier (qnode ID) must match a column header in `data.tsv`. For each pinned node, add the `ids` key mapped to an empty list. For each unpinned node, exclude the `ids` key.

Consider this example:

`data.tsv`
```
┌──────────────┬──────────────┐
│     Drug     │   Disease    │
├──────────────┼──────────────┤
│ MESH:D000865 │ MESH:D012223 │
│ MESH:C004649 │ MESH:D003233 │
│ MESH:C047340 │ MESH:D003233 │
└──────────────┴──────────────┘
```

`templates/template_1.json`
```json
{
    "message": {
        "query_graph": {
            "nodes": {
                "Disease": {
                    "ids": [] // Indicates pinned node
                },
                "Drug": {
                    // Missing "ids" indicates unpinned node
                    "categories": ["biolink:SmallMolecule"]
                }
            },
            "edges": {
                "e01": {
                    "object": "Disease",
                    "subject": "Drug",
                    "predicates": ["biolink:treats"]
                }
            }
        }
    }
}
```
This template and data table pairing represents 2 unique queries with 3 relevant results.

The first query is built from the first row of `data.tsv`. The pinned node is the disease MESH:D012223 (first row, Disease column). The other node is unpinned, so a result is considered relevant if it binds the unpinned node to MESH:D000865 (first row, Drug column).

The second query is built from the second and third row of `data.tsv` because these rows share the same CURIE for all pinned nodes. The pinned node is the disease MESH:D003233 (second/third row, Disease column). The other node is unpinned, so a result is considered relevant if it binds the unpinned node to either MESH:C004649 (second row, Drug column) or MESH:C047340 (third row, Drug column).

## Add a Benchmark
Add a named entry to `benchmarks.json` following this format:
```json
"name_of_benchmark": [
    {
        "source": "name_of_source_1", 

        
        "templates": [
            "template_1", 
            "template_2"  
        ]
    },
    {
        "source": "name_of_source_2",
        "templates": ["template_1"]
    },
    ...
]
```
**Notes:**
- Source name must match a child directory of `config`
- Template names must match the name of a JSON file in `config/name_of_source/templates`

## Add a Target
Add a named entry to `targets.json` following this format:
```json
"name_of_target": {
    "fetch": {
        "url": "http://...",
        "workflow": [
            {"id": "lookup"},
            {"id": "score"}
        ]
    },
    "fetch_unscored": {
        "url": "http://...",
        "workflow": [{"id": "lookup"}]
    },
    "score": {
        "url": "http://...",
        "workflow": [{"id": "score"}]
    }
}
```
**Notes:**
- The workflow key is optional
- `fetch` URL and workflow are used to fetch scored results
- `fetch_unscored` URL and workflow are used to fetch unscored results
- `score` URL and workflow are used to score unscored results
- The `fetch`, `fetch_unscored`, and `score` entries are not strictly necessary. The absence of an entry just breaks the corresponding functionality.