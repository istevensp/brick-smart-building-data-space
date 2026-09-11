# Evaluation

Scripts that produce every figure reported in the Results section of the paper.
They exist so that a reader can reproduce the numbers instead of taking them on
trust.

## What each script measures

| Script | Measures | Needs a running Fuseki |
|---|---|:--:|
| `01_graph_audit.py` | Graph composition, coverage of the link to the operational store, and the defects the audit exposes | No |
| `02_query_latency.py` | Latency of the three SPARQL queries, including the HTTP round trip | Yes |
| `03_scalability.py` | How query cost grows with the number of described devices | Yes |
| `04_readings_in_graph.py` | The architecture against the alternative of storing readings in the graph | Yes |
| `05_reasoner_cost.py` | The cost of the RDFS reasoner the deployment enables | Yes |
| `06_brick_validation.py` | Whether the graph validates against the SHACL shapes Brick ships with | No |

`01` and `06` read `Ontology/brickESPOLschema.ttl` directly, so they run
anywhere the repository is checked out.

## Running them

```bash
pip install -r Evaluation/requirements.txt

# Scripts 02 to 05 need the endpoint. Never hard-code the password.
export FUSEKI_BASE=http://localhost:3030
export FUSEKI_SPARQL_ENDPOINT=http://localhost:3030/brickESPOL/sparql
export FUSEKI_USER=admin
export FUSEKI_PASSWORD=...

python Evaluation/01_graph_audit.py
python Evaluation/02_query_latency.py
```

Scripts `03`, `04` and `05` create temporary in-memory datasets through the
Fuseki admin API and delete them when they finish. **They never write to the
deployed `brickESPOL` dataset.**

## Reading the results honestly

Three things are worth stating plainly, because the scripts make them visible
and a reader will see them anyway.

**The replication in `03` is synthetic.** It is one building duplicated with
renamed IRIs, not a campus. It measures how the cost of a query grows with the
number of devices a graph describes, and nothing about interoperability across
real, independently modelled buildings.

**`04` does not show that the architecture makes queries faster.** It does not:
the metadata query is largely insensitive to the size of the store in the range
tested. What the separation buys is a graph whose size is a function of the
installed equipment rather than of how long the building has been monitored.

**The total number of triples has two correct answers.** The deployment mounts
the dataset as a `ja:InfModel` with an RDFS reasoner, so a count with inference
differs from a count without it by about a third. Instance counts do not have
this problem, which is why the paper reports those.

## Requirements

Python 3.9 or later. See `requirements.txt`; `rdflib` and `pyshacl` are already
pinned in the project's top-level `requirements.txt` at the same versions.
