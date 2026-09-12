# Measurement results

Raw output of the evaluation scripts, kept verbatim. Every figure printed in the
paper must be traceable to a file here, and every file here must be reproducible
by running the script it names.

Files are named `YYYY-MM-DD_<script>_<configuration>.txt`.

## Traceability: which result backs which claim

| Figure in the paper | Where it appears | Script | Result file | Status |
|---|---|---|---|:--|
| 280 entities, 37 equipment, 214 points | Table I, §V-A | `01_graph_audit.py` | deterministic, reproduced on demand | current |
| 1,257 triples with an `espol:` subject | Table I, §V-A, §VI, contribution 4 | `01_graph_audit.py` | deterministic | current |
| 2.3 % of the file is instance data | Table I, §V-A | `01_graph_audit.py` | deterministic | current |
| 6 triples per measurement point | §V-A | `01_graph_audit.py` | deterministic | current |
| 37 / 37 equipment carry `db_id` | Table I, §V-B | `01_graph_audit.py` | deterministic | current |
| 214 / 214 points carry `point_type` | Table I, §V-B | `01_graph_audit.py` | deterministic | current |
| 46 of 214 points with an unresolvable unit IRI | §V-C, contribution 3 | `01_graph_audit.py`, `06_brick_validation.py` | deterministic | current |
| 114 of 214 points on Sonoff S31, 6 families, 4 vendors | §IV-A, contribution 2 | `01_graph_audit.py` | deterministic | current |
| 254 node shapes, Brick 1.4.4 | §V-C | `06_brick_validation.py` | deterministic | current |
| 41 violations on the building model | §V-C | `06_brick_validation.py` | deterministic | current |
| 37 of them on `brick:hasLocation` | §V-C, contribution 1 | `06_brick_validation.py` | deterministic | current |
| Official Brick-REC alignment, 130 triples, changes nothing | §V-C | cross-validation matrix | deterministic | current |
| Repairing with deprecated classes drops 41 to 7 | §V-C | cross-validation matrix | deterministic | current |
| Query latency: Q1 11.5, Q2 4.3, Q3 4.2 ms, with IQR | Table II, §V-D | `08_query_latency_repeated.py` | `2026-09-11_08_query_latency_100trials.txt` | current |
| Scalability: 6.5 / 14.7 / 47.9 ms, with IQR | Table II, §V-D | `07_scalability_repeated.py` | `2026-09-11_07_scalability_100trials.txt` | current |
| 16x the data costs 7.4x the time | §V-D | `07_scalability_repeated.py` | same file | current |
| Cost per point falls from 0.030 to 0.014 ms | §V-D | `07_scalability_repeated.py` | same file | current |
| Reasoner: 1.0-1.1x structural, 1.5x to 2.2x for the join query | §V-D, §VI | `05_reasoner_cost.py` | measured twice, consistent | current |
| Readings in the graph: 6.7 to 7.3 ms, IQRs 6.5-7.0 and 7.1-7.9, non-overlapping | §V-E, §VI | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` | current |
| Store grows 7.9 MB to 76.1 MB | §V-E | `04_readings_in_graph.py` | deterministic | current |
| 55,219 to 483,219 triples | §V-E | `04_readings_in_graph.py` | deterministic | current |
| Order of 450 million triples a year | §V-E, §VI | arithmetic from the above | derived | current, and labelled as extrapolation |
| TDB store 193 MB for a 1.8 MB source | §VI | `du` on `Services/fuseki/databases` | deterministic | current |

Rows marked deterministic do not vary between runs: they are counts over a fixed
graph. Every timing figure in the paper is now the median of 100 trials with the
interquartile range between trials, and none is taken from a single invocation.

## Why the raw output is kept

The scalability measurement was first reported from a single invocation. Three
invocations of the same script over the same data gave 7.6, 11.3 and 8.0 ms at
the smallest size; the 11.3 was a cold start. The ratio between the largest and
smallest size, which the paper quotes, was 6.4, then 4.4, then 6.1 depending on
which invocation was used, and 100 trials produced 7.4. Keeping only the summary
would have hidden that the number was unstable.

Timing figures are therefore reported as the median across trials with the
interquartile range, never from one invocation, and the output that produced them
is stored here.

## Hardware and versions

All measurements on one machine: Windows 11, Docker Desktop 29.7.2, Fuseki from
the `stain/jena-fuseki` image, dataset mounted from `Services/fuseki`. Client is
Python 3.14 with `urllib`; graph handling is rdflib 7.1.4 and validation pySHACL
0.30.1. The vocabulary is the Brick 1.4.4 distribution in `Ontology/Brick.ttl`,
with the QUDT unit vocabulary in `Ontology/QUDT-units.ttl` resolved into the data
graph during validation.

Latency depends on all of the above. The figures are not portable to other
hardware; the scripts are the part that is.

## Index

| File | Script | Configuration | Elapsed |
|---|---|---|---:|
| `2026-09-11_07_scalability_100trials.txt` | `07_scalability_repeated.py` | 100 trials, 40 timed queries each, 214 to 3,424 points | 858.8 s |
| `2026-09-11_08_query_latency_100trials.txt` | `08_query_latency_repeated.py` | 100 trials, 40 timed queries each, three queries | 167.5 s |
| `2026-09-11_09_readings_in_graph_100trials.txt` | `09_readings_in_graph_repeated.py` | 100 trials, 40 timed queries each, four store sizes | 756.2 s |
