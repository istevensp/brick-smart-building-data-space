# Measurement results

Raw output of the evaluation scripts, kept verbatim. Every figure printed in the
paper must be traceable to a file here, and every file here must be reproducible
by running the script it names.

Files are named `YYYY-MM-DD_<script>_<configuration>.txt`.

## Traceability: which result backs which claim

| Figure in the paper | Where it appears | Script | Result file | Status |
|---|---|---|---|:--|
| 280 entities, 37 equipment, 214 points | Table I, §V-A | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` | current |
| 1,257 triples with an `espol:` subject | Table I, §V-A, §VI, contribution 4 | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` | current |
| 2.3 % of the file is instance data | Table I, §V-A | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` | current |
| 5.9 triples per measurement point | §V-A | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` | current. It is a global average over 1,257 triples that also cover spaces and equipment, not the marginal cost of one more point |
| 37 / 37 equipment carry `db_id` | Table I, §V-B | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` | current. Established by this audit, **not** by conformance to Brick |
| 214 / 214 points carry `point_type` | Table I, §V-B | `01_graph_audit.py` | `2026-09-11_01_graph_audit.txt` | current. Same caveat |
| 46 of 214 points with an unresolvable unit IRI | §V-C, contribution 3 | `12_defects_by_family.py` | `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials, 20 timed queries each, deployed dataset | ~40 s |
| `2026-09-11_12_defects_by_family.txt` | current. The script runs over both the released model and `brickESPOLschema.ttl.bak`, so the before/after is reproducible |
| The 46 defects fall on 2 of 6 families, 40 + 6, none on the other four | §V-C, contribution 2 | `12_defects_by_family.py` | `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials, 20 timed queries each, deployed dataset | ~40 s |
| `2026-09-11_12_defects_by_family.txt` | current |
| Link coverage is 100 % in every family | §V-C, contribution 2 | `12_defects_by_family.py` | `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials, 20 timed queries each, deployed dataset | ~40 s |
| `2026-09-11_12_defects_by_family.txt` | current |
| 114 of 214 points on Sonoff S31, 6 families, 4 vendors | §IV-A, contribution 2 | `01_graph_audit.py` | deterministic | current |
| 254 node shapes, Brick 1.4.4 | §V-C | `06_brick_validation.py` | `2026-09-11_06_brick_validation.txt` | current |
| 41 violations on the building model | §V-C | `06_brick_validation.py`, `10_crossvalidation.py` | `2026-09-11_06_brick_validation.txt` | current. Breaks down as `hasLocation` 37 + `isPartOf` 2 + `hasPart` 2 |
| 37 of them on `brick:hasLocation` | §V-C, contribution 1 | `06_brick_validation.py` | `2026-09-11_06_brick_validation.txt` | current. Message is verbatim *Value does not have class brick:Location* |
| Official Brick-REC alignment, 130 triples, 15 `owl:equivalentClass`, changes nothing | §V-C | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` | current. The count on `espol:` nodes changes by **+0** |
| Typing the spaces with the deprecated classes removes all 37 `hasLocation` violations | §V-C | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` | current. The residual count depends on how the counterfactual is built: the hand-written patch left 7, the script's vocabulary-derived variant leaves 6. **The paper should quote the 37, which both agree on** |
| Violations by SHACL path on `espol:` nodes | §V-C | `10_crossvalidation.py` | `2026-09-11_10_crossvalidation.txt` | current |
| Scenario query: 3 rows in 5.6 ms, 14 rows in 5.0 ms, IQRs overlap | §V-H | `13_scenario_query.py` | `2026-09-11_13_scenario_query.txt` | current, 30 trials |
| Query latency: Q1 11.5, Q2 4.3, Q3 4.2 ms, with IQR | Table II, §V-D | `08_query_latency_repeated.py` | `2026-09-11_08_query_latency_100trials.txt` | current |
| Scalability: 6.5 / 14.7 / 47.9 ms, with IQR | Table II, §V-D | `07_scalability_repeated.py` | `2026-09-11_01_graph_audit.txt` | `01_graph_audit.py` | released model, counts only | <1 s |
| `2026-09-11_06_brick_validation.txt` | `06_brick_validation.py` | Brick 1.4.4 shapes, QUDT resolved, RDFS inference | ~20 s |
| `2026-09-11_10_crossvalidation.txt` | `10_crossvalidation.py` | four configurations compared | 69.3 s |
| `2026-09-11_05_reasoner_cost.txt` | `05_reasoner_cost.py` | single pass, superseded | ~60 s |
| `2026-09-11_11_reasoner_cost_repeated.txt` | `11_reasoner_cost_repeated.py` | 20 trials, 15 timed queries per block | 135.9 s |
| `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials, 20 timed queries each, deployed dataset | ~40 s |
| `2026-09-11_12_defects_by_family.txt` | `12_defects_by_family.py` | released model and pre-repair backup, by family | <2 s |
| `2026-09-11_07_scalability_100trials.txt` | current |
| 16x the data costs 7.4x the time | §V-D | `07_scalability_repeated.py` | same file | current |
| Cost per point falls from 0.030 to 0.014 ms | §V-D | `07_scalability_repeated.py` | same file | current |
| Reasoner: no measurable cost on structural queries; join 1.49x / 1.85x / 2.08x | §V-D, §VI | `11_reasoner_cost_repeated.py` | `2026-09-11_11_reasoner_cost_repeated.txt` | current, 20 trials with IQR |
| Reasoner, single pass | superseded | `05_reasoner_cost.py` | `2026-09-11_05_reasoner_cost.txt` | **superseded**: it gave 1.3x / 1.6x / 2.1x and a structural factor of 0.5x, which is noise. Kept as the evidence that one pass is not enough |
| Readings in the graph: 6.7 to 7.3 ms, IQRs 6.5-7.0 and 7.1-7.9, non-overlapping | §V-E, §VI | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` | current |
| Store grows 7.9 MB to 76.1 MB | §V-E | `04_readings_in_graph.py`, `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` | current. These are **N-Triples serialization sizes**, which is what the script labels them, not the on-disk size of a TDB store |
| 55,219 to 483,219 triples | §V-E | `09_readings_in_graph_repeated.py` | `2026-09-11_09_readings_in_graph_100trials.txt` | current |
| Order of 450 million triples a year | §V-E, §VI | arithmetic from the above | derived | current, and labelled as extrapolation |
| TDB store 193 MB for a 1.8 MB source | §VI | `du -sh Services/fuseki/databases/brickESPOL` | no output stored | **command recorded, output not kept**. Verifiable locally, not reproducible as a published figure |

Rows that name a file do not vary between runs unless they are timings: the
counts are over a fixed graph. Every timing figure in the paper is the median of
100 trials with the interquartile range between trials, and none is taken from a
single invocation.

**One row still does not have a reproducible artefact, and is marked as such:**
the 193 MB of the TDB store, whose command is recorded but whose output was not
kept. It is on the to-do list rather than hidden here. The 46 broken unit IRIs
were in the same position until `12_defects_by_family.py` made them measurable
again by reading the pre-repair model alongside the released one.

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
| `2026-09-11_01_graph_audit.txt` | `01_graph_audit.py` | released model, counts only | <1 s |
| `2026-09-11_06_brick_validation.txt` | `06_brick_validation.py` | Brick 1.4.4 shapes, QUDT resolved, RDFS inference | ~20 s |
| `2026-09-11_10_crossvalidation.txt` | `10_crossvalidation.py` | four configurations compared | 69.3 s |
| `2026-09-11_05_reasoner_cost.txt` | `05_reasoner_cost.py` | single pass, superseded | ~60 s |
| `2026-09-11_11_reasoner_cost_repeated.txt` | `11_reasoner_cost_repeated.py` | 20 trials, 15 timed queries per block | 135.9 s |
| `2026-09-11_13_scenario_query.txt` | `13_scenario_query.py` | 30 trials, 20 timed queries each, deployed dataset | ~40 s |
| `2026-09-11_12_defects_by_family.txt` | `12_defects_by_family.py` | released model and pre-repair backup, by family | <2 s |
| `2026-09-11_07_scalability_100trials.txt` | `07_scalability_repeated.py` | 100 trials, 40 timed queries each, 214 to 3,424 points | 858.8 s |
| `2026-09-11_08_query_latency_100trials.txt` | `08_query_latency_repeated.py` | 100 trials, 40 timed queries each, three queries | 167.5 s |
| `2026-09-11_09_readings_in_graph_100trials.txt` | `09_readings_in_graph_repeated.py` | 100 trials, 40 timed queries each, four store sizes | 756.2 s |
