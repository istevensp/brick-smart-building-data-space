# Measurement results

Raw output of the evaluation scripts, kept verbatim. **Every figure printed in
the paper must be traceable to a file here, and every file here must be
reproducible by running the script it names.**

Files are named `YYYY-MM-DD_<script>_<configuration>.txt`.

## Traceability: which result backs which figure

| Figure in the paper | Where it appears | Script | Result file |
|---|---|---|---|
| 280 entities, 37 equipment, 214 points, 14 sensor classes | Table I, §IV-A | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` |
| 1,257 triples with an `espol:` subject; 2.3 % of the file; 5.9 triples per point | Table I, §IV-A, §V | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` |
| 37 / 37 equipment carry `db_id`, 214 / 214 points carry `point_type` | Table I, §IV-A, abstract | `01_graph_audit.py`, `12_defects_by_family.py` | `2026-09-11_01_graph_audit.txt`, `2026-09-11_12_defects_by_family.txt` |
| 80 points on eight devices in the panel area, down to two on a single device | §IV-A | `15_paper_figures.py` | `2026-09-13_15_paper_figures.txt` |
| 177 energy points, 31 indoor, 6 on the weather station | §IV-A | `15_paper_figures.py` | `2026-09-13_15_paper_figures.txt` |
| 254 node shapes in the Brick 1.4.4 distribution | §IV-B | `06_brick_validation.py` | `2026-09-11_06_brick_validation.txt` |
| 46 of 214 points with an unresolvable unit IRI | §IV-B, §V, contribution 3 | `12_defects_by_family.py` | `2026-09-11_12_defects_by_family.txt` |
| The 46 fall on 2 of 6 families, 40 + 6, none on the other four | §IV-B, contribution 2 | `12_defects_by_family.py` | `2026-09-11_12_defects_by_family.txt` |
| Link coverage is complete in every family | §IV-B, contribution 2 | `12_defects_by_family.py` | `2026-09-11_12_defects_by_family.txt` |
| 41 violations on the building model | §IV-B, abstract | `06_brick_validation.py`, `10_crossvalidation.py` | `2026-09-11_06_brick_validation.txt` |
| 37 of them on `brick:hasLocation` | §IV-B, §V, contribution 1, abstract | `06_brick_validation.py` | `2026-09-11_06_brick_validation.txt` |
| The remaining four are internal to REC: the campus is typed both `rec:Campus` and `rec:Organization` | §IV-B, §V | `14_partof_violations.py` | `2026-09-12_14_partof_violations.txt` |
| 246 terms carry `owl:deprecated` in the release | §IV-B | `15_paper_figures.py` | `2026-09-13_15_paper_figures.txt` |
| Official Brick–REC alignment, 130 triples, 15 `owl:equivalentClass`, changes the count by +0 | §IV-B, abstract | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` |
| Typing the spaces with the deprecated classes removes all 37 | §IV-B | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` |
| The administrative layer REC adds is twelve triples | §IV-B | `15_paper_figures.py` | `2026-09-13_15_paper_figures.txt` |
| Query latency 11.5 / 4.3 / 4.2 ms with IQR | Table II, §IV-C, §V, abstract | `08_query_latency_repeated.py` | `2026-09-11_08_query_latency_100trials.txt` |
| Scalability 6.5 / 14.7 / 47.9 ms with IQR | Table II, §IV-C | `07_scalability_repeated.py` | `2026-09-11_07_scalability_100trials.txt` |
| 16× the data costs 7.4× the time; cost per point 0.030 → 0.014 ms; IQR 3.4–6.2 % of the median | §IV-C | `07_scalability_repeated.py` | `2026-09-11_07_scalability_100trials.txt` |
| Reasoner: structural queries 0.98–1.04, seven of nine IQRs contain 1.0; join 1.49 / 1.85 / 2.08 | §IV-C, §V | `11_reasoner_cost_repeated.py` | `2026-09-11_11_reasoner_cost_repeated.txt` |
| Readings in the graph: 6.7 → 7.3 ms, IQRs 6.5–7.0 and 7.1–7.9, non-overlapping; 9 % for 8.7× the data | §IV-D, §V | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` |
| 55,219 → 483,219 triples; 7.9 → 76 MB | §IV-D | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` |
| Order of 450 million triples a year | §IV-D, §V, abstract | arithmetic from the row above | derived, and labelled as an extrapolation |
| Scenario: 3 rows in 5.6 ms, 14 rows in 5.0 ms, IQRs overlap | §IV-E | `13_scenario_query.py` | `2026-09-11_13_scenario_query.txt` |
| Three MongoDB collections, one per laboratory | §IV-E | `15_paper_figures.py` | `2026-09-13_15_paper_figures.txt` |
| Devices carry between two and eighteen points each | §V | `12_defects_by_family.py` | `2026-09-11_12_defects_by_family.txt` |
| Five services: Fuseki, MongoDB, Node-RED, Django, React | §V | repository inspection, `Services/` and `WebApp/` | nothing to time |
| **TDB store 193 MB for a 1.8 MB source file** | §V | `du -sh Services/fuseki/databases/brickESPOL` | **command recorded, output not kept** |

## Superseded runs, kept on purpose

| File | Script | Why it is kept |
|---|---|---|
| `2026-09-11_05_reasoner_cost.txt` | `05_reasoner_cost.py` | Single pass. Gave 1.3× / 1.6× / 2.1× and a structural factor of **0.5×**, which is impossible. Kept as the evidence that one invocation is not a measurement |

`02_query_latency.py`, `03_scalability.py` and `04_readings_in_graph.py` are the
single-pass versions of `08`, `07` and `09`. They stay in `Evaluation/` so the
repeated versions can be compared against them, and **no figure in the paper
comes from them.**

## How to reproduce

| File | Script | Configuration | Time |
|---|---|---|---|
| `2026-09-11_01_graph_audit.txt` | `01_graph_audit.py` | released model, counts only | <1 s |
| `2026-09-11_06_brick_validation.txt` | `06_brick_validation.py` | Brick 1.4.4 shapes, QUDT resolved, RDFS inference | ~20 s |
| `2026-09-11_07_scalability_100trials.txt` | `07_scalability_repeated.py` | 100 trials × 40 timed queries, five sizes | 858.8 s |
| `2026-09-11_08_query_latency_100trials.txt` | `08_query_latency_repeated.py` | 100 trials × 40 timed queries, deployed endpoint | 167.5 s |
| `2026-09-11_09_readings_in_graph_100trials.txt` | `09_readings_in_graph_repeated.py` | 100 trials, four store sizes | 756.2 s |
| `2026-09-11_10_crossvalidation.txt` | `10_crossvalidation.py` | four configurations compared | 69.3 s |
| `2026-09-11_11_reasoner_cost_repeated.txt` | `11_reasoner_cost_repeated.py` | 20 trials, 15 timed queries per block | 135.9 s |
| `2026-09-11_12_defects_by_family.txt` | `12_defects_by_family.py` | released model and pre-repair backup, by family | <2 s |
| `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials × 20 timed queries, deployed endpoint | ~40 s |
| `2026-09-12_14_partof_violations.txt` | `14_partof_violations.py` | published files only, no deployment | ~25 s |
| `2026-09-13_15_paper_figures.txt` | `15_paper_figures.py` | published files only, no deployment | ~20 s |

Scripts `01`, `06`, `10`, `12`, `14` and `15` read the published ontology files
and need no running deployment. `07`, `09` and `11` build in-memory datasets.
`08` and `13` query the deployed endpoint and need Fuseki up.

Counts do not vary between runs: they are over a fixed graph. **Every timing
figure in the paper is a median across repeated trials with the interquartile
range between them, and none comes from a single invocation.**

### Determinism

Where a script prints counts, ties are broken by name, so two runs produce
byte-identical files. What varies legitimately is the elapsed time `10` prints
per configuration, and the timings in `07`, `08`, `09`, `11` and `13`, which are
measurements.

## The one row still without an artefact

**The 193 MB of the TDB store.** The command is recorded and the figure is
verifiable locally, but the output was never saved, so it is not reproducible
from this directory. It is on the to-do list rather than hidden here.

Every other figure in the paper has a file in this directory behind it.
