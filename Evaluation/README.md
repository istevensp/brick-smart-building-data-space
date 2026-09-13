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
| `07_scalability_repeated.py` | `03` over 100 trials, reporting medians and interquartile ranges | Yes |
| `08_query_latency_repeated.py` | `02` over 100 trials | Yes |
| `09_readings_in_graph_repeated.py` | `04` over 100 trials | Yes |
| `10_crossvalidation.py` | Whether the location violations are an artefact of an incomplete import closure, by validating four configurations and comparing them | No |
| `13_scenario_query.py` | The query the end-to-end scenario describes, restricted to one laboratory through the REC hierarchy | Yes |
| `12_defects_by_family.py` | Link coverage and unit defects split by device family, over the released model and the pre-repair backup | No |
| `11_reasoner_cost_repeated.py` | `05` over 20 trials, reporting the distribution of the factor rather than one value | Yes |
| `14_partof_violations.py` | Why the four part-of violations fail. They are internal to REC and have nothing to do with Brick | No |
| `15_paper_figures.py` | The five figures the text stated that no other script produced: densest and sparsest zone, what the points measure, the administrative layer, the MongoDB collections, and the deprecated terms in the release | No |

`01`, `06`, `10`, `12`, `14` and `15` read the published ontology files
directly, so they run anywhere the repository is checked out.

`07`, `08`, `09` and `11` supersede `02`, `03`, `04` and `05` for every timing
figure in the paper: a single invocation of the same measurement is not reproducible, and the
ratio that was going to be printed came out as 6.4, 4.4, 6.1 and 7.4 depending
on the run. The single-pass scripts are kept because they are quicker to read.

`10` is the one that supports the Brick 1.4.4 finding. Reporting violations from
one configuration would establish nothing on its own: an unresolved import can
manufacture violations, as happened in this work with QUDT, where 183 of them
turned out to be noise. The script validates the released model against Brick
alone, against Brick with QUDT resolved, against both plus the official
`Brick-REC-alignment.ttl`, and against a variant whose spaces also carry the
deprecated Brick classes. That variant is derived from the vocabulary itself, by
reading `brick:isReplacedBy` backwards, rather than written by hand.

## Running them

```bash
pip install -r Evaluation/requirements.txt

# Scripts 02 to 05, 07 to 09 and 11 need the endpoint. Never hard-code the password.
export FUSEKI_BASE=http://localhost:3030
export FUSEKI_SPARQL_ENDPOINT=http://localhost:3030/brickESPOL/sparql
export FUSEKI_USER=admin
export FUSEKI_PASSWORD=...

python Evaluation/01_graph_audit.py
python Evaluation/02_query_latency.py

# No endpoint needed for these three
python Evaluation/06_brick_validation.py
python Evaluation/10_crossvalidation.py
```

`10` needs `Ontology/Brick-REC-alignment.ttl`, which is the official alignment
published by the Brick project at `alignments/rec/` in its repository. It is
vendored here, like `Brick.ttl` and `QUDT-units.ttl`, so that the comparison is
reproducible offline and against a fixed version rather than whatever the URL
serves later.

Scripts `03`, `04`, `05`, `07`, `09` and `11` create temporary in-memory
datasets through the Fuseki admin API and delete them when they finish. **They never write to the
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
