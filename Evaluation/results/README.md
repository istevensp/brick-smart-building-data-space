# Measurement results

Raw output of the evaluation scripts, kept verbatim. **Every number this
directory reports is reproducible by running the script it names**, and every
script writes exactly one file here.

Files are named `YYYY-MM-DD_<script>_<configuration>.txt`.

## What each measurement reports

| Measurement | Script | Result file |
|---|---|---|
| 280 entities, 37 equipment, 214 points, 14 sensor classes | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` |
| 1,257 triples with an `espol:` subject; 2.3 % of the file; 5.9 per point, the density of the whole model | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` |
| A point costs four or five triples and a device three of its own, which is what growth costs | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| 37 / 37 equipment carry `db_id`, 214 / 214 points carry `point_type` | `01_graph_audit.py`, `12_defects_by_family.py` | `2026-09-11_01_graph_audit.txt`, `2026-09-13_12_defects_by_family.txt` |
| 80 points on eight devices in the electrical-panel zone, down to two on a single device | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| 177 energy points, 31 indoor, 6 on the weather station | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| 254 node shapes in the Brick 1.4.4 distribution | `06_brick_validation.py` | `2026-09-11_06_brick_validation.txt` |
| 46 of 214 points with an unresolvable unit IRI | `12_defects_by_family.py` | `2026-09-13_12_defects_by_family.txt` |
| The 46 fall on 2 of 6 families, 40 + 6, none on the other four | `12_defects_by_family.py` | `2026-09-13_12_defects_by_family.txt` |
| Link coverage is complete in every family | `12_defects_by_family.py` | `2026-09-13_12_defects_by_family.txt` |
| 78 violations in all, 41 of them on the building model | `06_brick_validation.py`, `10_crossvalidation.py` | `2026-09-11_06_brick_validation.txt`, `2026-09-11_10_crossvalidation.txt` |
| 37 of them on `brick:hasLocation` | `06_brick_validation.py` | `2026-09-11_06_brick_validation.txt` |
| The release carries two shapes for `brick:hasLocation` that disagree: `brick:Equipment` accepts `rec:Space`, `brick:Entity` does not | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| The remaining four are internal to REC: the campus is typed both `rec:Campus` and `rec:Organization` | `14_partof_violations.py` | `2026-09-12_14_partof_violations.txt` |
| 246 terms carry `owl:deprecated` in the release | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| Official Brick–REC alignment, 130 triples, 15 `owl:equivalentClass`, changes the count by +0 | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` |
| Typing the spaces with the deprecated classes removes all 37 and still leaves 6 | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` |
| The administrative layer REC adds is twelve triples | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| Query latency 11.5 / 4.3 / 4.2 ms with IQR | `08_query_latency_repeated.py` | `2026-09-11_08_query_latency_100trials.txt` |
| Scalability 6.5 / 14.7 / 47.9 ms with IQR | `07_scalability_repeated.py` | `2026-09-11_07_scalability_100trials.txt` |
| 16× the data costs 7.4× the time; cost per point 0.030 → 0.014 ms; IQR 3.4–6.2 % of the median | `07_scalability_repeated.py` | `2026-09-11_07_scalability_100trials.txt` |
| Reasoner: structural queries 0.98–1.04, seven of nine IQRs contain 1.0; join 1.49 / 1.85 / 2.08 | `11_reasoner_cost_repeated.py` | `2026-09-11_11_reasoner_cost_repeated.txt` |
| Readings in the graph: 6.7 → 7.3 ms, IQRs 6.5–7.0 and 7.1–7.9, non-overlapping; 9 % for 8.8× the data | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` |
| 55,219 → 483,219 triples; 7.9 → 76 MB | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` |
| Order of 450 million triples a year | arithmetic from the row above | derived, and labelled as an extrapolation |
| One laboratory in 5.6 ms for 3 rows, the building in 5.0 ms for 14, IQRs overlap | `13_scenario_query.py` | `2026-09-11_13_scenario_query.txt` |
| Three MongoDB collections, one per laboratory | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| Devices carry between two and eighteen points each | `15_model_summary.py` | `2026-09-13_15_model_summary.txt` |
| Five services: Fuseki, MongoDB, Node-RED, Django, React | repository inspection, `Services/` and `WebApp/` | nothing to time |
| TDB store 193 MB for a 1.8 MB source file | `du -h` on `Services/fuseki/databases/brickESPOL` and on `Ontology/brickESPOLschema.ttl` | measured on the deployed store, which the repository does not carry |

## Superseded runs, kept on purpose

| File | Script | Why it is kept |
|---|---|---|
| `2026-09-11_05_reasoner_cost.txt` | `05_reasoner_cost.py` | Single pass. Gave 1.3× / 1.6× / 2.1× and a structural factor of **0.5×**, which is impossible. Kept as the evidence that one invocation is not a measurement |

`02_query_latency.py`, `03_scalability.py` and `04_readings_in_graph.py` are the
single-pass versions of `08`, `07` and `09`. They stay in `Evaluation/` so the
repeated versions can be compared against them, and **none of the figures
above comes from them.**

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
| `2026-09-13_12_defects_by_family.txt` | `12_defects_by_family.py` | released model and the earlier snapshot, by family | <2 s |
| `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials × 20 timed queries, deployed endpoint | ~40 s |
| `2026-09-12_14_partof_violations.txt` | `14_partof_violations.py` | published files only, no deployment | ~25 s |
| `2026-09-13_15_model_summary.txt` | `15_model_summary.py` | published files only, no deployment | ~20 s |

Scripts `01`, `06`, `10`, `12`, `14` and `15` read the published ontology files
and need no running deployment. `07`, `09` and `11` build in-memory datasets.
`08` and `13` query the deployed endpoint and need Fuseki up.

Counts do not vary between runs: they are over a fixed graph. **Every timing
above is a median across repeated trials with the interquartile
range between them, and none comes from a single invocation.**

### Determinism

Where a script prints counts, ties are broken by name, so two runs produce
byte-identical files. What varies legitimately is the elapsed time `10` prints
per configuration, and the timings in `07`, `08`, `09`, `11` and `13`, which are
measurements.

## The one number with no file here

**The 193 MB of the TDB store.** It is a property of the deployed store, not of
the published files, so there is no output to keep: the repository carries the
Turtle source and the store is built by loading it. Both figures come from
`du -h`, on `Services/fuseki/databases/brickESPOL` and on
`Ontology/brickESPOLschema.ttl`.

Everything else above has a file in this directory behind it.
