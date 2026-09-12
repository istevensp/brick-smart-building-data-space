"""Cross-validate the Brick 1.4.4 location conflict against alternative closures.

Script 06 validates one configuration and reports 41 violations on the released
model. That number alone does not support the claim, because an incomplete
import closure can manufacture violations out of nothing: it already happened
once in this work, when 183 violations on brick:hasUnit turned out to be the
unresolved QUDT import rather than a modelling error.

The claim is therefore tested as a comparison across four configurations:

  1. released model, Brick shapes alone
  2. released model, Brick + QUDT resolved
  3. released model, Brick + QUDT + the official Brick-REC alignment
  4. a variant whose spaces also carry the deprecated Brick classes

If the violations were an artefact of a missing import, configuration 3 would
clear them. If they are the cost of following Brick 1.4.4's own recommendation,
3 changes nothing and only 4 reduces them, at the price of typing the model with
terms the same release withdraws.

The deprecated-typed variant in configuration 4 is not written by hand: it is
derived from the vocabulary itself, by reading brick:isReplacedBy backwards and
adding, for every entity typed with a REC class, the Brick class that the
release retired in its favour.

Usage:
    python Evaluation/10_crossvalidation.py
"""

import os
import sys
import time
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Namespace, RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(ROOT, "Ontology")

SH = Namespace("http://www.w3.org/ns/shacl#")
BRICK = Namespace("https://brickschema.org/schema/Brick#")

MODEL = os.path.join(ONTOLOGY, "brickESPOLschema.ttl")
SHAPES = os.path.join(ONTOLOGY, "Brick.ttl")
QUDT = os.path.join(ONTOLOGY, "QUDT-units.ttl")
ALIGNMENT = os.path.join(ONTOLOGY, "Brick-REC-alignment.ttl")


def local(term):
    """Last segment of an IRI, for printing."""
    return str(term).split("#")[-1].split("/")[-1]


def espol_namespace(graph):
    """Read the local namespace off the model instead of hard-coding it."""
    for prefix, namespace in graph.namespaces():
        if prefix == "espol":
            return str(namespace)
    raise SystemExit("the model declares no espol: prefix")


def with_deprecated_types(base, shapes):
    """Add, for every REC-typed entity, the Brick class it replaced.

    Brick 1.4.4 states the mapping as `brick:X brick:isReplacedBy rec:Y`, so the
    variant is obtained by reading that backwards. This reconstructs the patch
    that was applied and then reverted during development.
    """
    replaced_by = {}
    for brick_class, rec_class in shapes.subject_objects(BRICK.isReplacedBy):
        replaced_by.setdefault(rec_class, []).append(brick_class)

    variant = Graph()
    for triple in base:
        variant.add(triple)
    for prefix, namespace in base.namespaces():
        variant.bind(prefix, namespace)

    added = 0
    entities = set()
    for subject, rec_class in base.subject_objects(RDF.type):
        for brick_class in replaced_by.get(rec_class, []):
            if (subject, RDF.type, brick_class) not in variant:
                variant.add((subject, RDF.type, brick_class))
                entities.add(subject)
                added += 1
    return variant, added, len(entities)


def run(label, data, closure_files, shapes, espol):
    """Validate one configuration and return its counts."""
    graph = Graph()
    for triple in data:
        graph.add(triple)
    for path in closure_files:
        graph.parse(path, format="turtle")

    started = time.time()
    _, report, _ = validate(
        graph, shacl_graph=shapes, ont_graph=shapes,
        inference="rdfs", abort_on_first=False)
    elapsed = time.time() - started

    violations = list(report.subjects(SH.resultSeverity, SH.Violation))
    by_path = Counter()
    on_espol = Counter()
    for violation in violations:
        focus = list(report.objects(violation, SH.focusNode))
        path = list(report.objects(violation, SH.resultPath))
        key = local(path[0]) if path else "(no path)"
        by_path[key] += 1
        if focus and str(focus[0]).startswith(espol):
            on_espol[key] += 1

    total_espol = sum(on_espol.values())
    print("%-46s %7d %8d %9.1fs" % (label, len(violations), total_espol, elapsed))
    sys.stdout.flush()
    return len(violations), total_espol, by_path, on_espol


def main():
    for path in (MODEL, SHAPES, ALIGNMENT):
        if not os.path.exists(path):
            raise SystemExit("missing input: %s" % path)

    released = Graph()
    released.parse(MODEL, format="turtle")
    espol = espol_namespace(released)

    shapes = Graph()
    shapes.parse(SHAPES, format="turtle")

    alignment = Graph()
    alignment.parse(ALIGNMENT, format="turtle")

    deprecated, added, entities = with_deprecated_types(released, shapes)

    print("model            : %d triples" % len(released))
    print("shapes           : %s, %d triples" % (os.path.basename(SHAPES), len(shapes)))
    print("alignment        : %d triples, %d owl:equivalentClass"
          % (len(alignment),
             len(list(alignment.subject_objects(
                 Namespace("http://www.w3.org/2002/07/owl#").equivalentClass)))))
    print("deprecated variant: +%d type triples on %d entities" % (added, entities))
    print("local namespace  : %s" % espol)
    print()
    print("%-46s %7s %8s %10s" % ("configuration", "total", "on espol", "time"))
    print("-" * 74)

    results = []
    results.append(("released model, Brick shapes alone",)
                   + run("released model, Brick shapes alone",
                         released, [], shapes, espol))
    results.append(("released model, Brick + QUDT",)
                   + run("released model, Brick + QUDT",
                         released, [QUDT], shapes, espol))
    results.append(("released model, Brick + QUDT + REC alignment",)
                   + run("released model, Brick + QUDT + REC alignment",
                         released, [QUDT, ALIGNMENT], shapes, espol))
    results.append(("deprecated-typed variant, Brick + QUDT",)
                   + run("deprecated-typed variant, Brick + QUDT",
                         deprecated, [QUDT], shapes, espol))

    print()
    print("Breakdown on espol: nodes, by property")
    print("%-46s %s" % ("configuration", "paths"))
    print("-" * 74)
    for label, _, _, _, on_espol in results:
        detail = ", ".join("%s %d" % (key, count)
                           for key, count in on_espol.most_common())
        print("%-46s %s" % (label, detail if detail else "none"))

    print()
    baseline = results[1][2]
    aligned = results[2][2]
    repaired = results[3][2]
    print("The official alignment changes the count on espol: nodes by %+d."
          % (aligned - baseline))
    print("Typing the spaces with the deprecated classes changes it by %+d."
          % (repaired - baseline))


if __name__ == "__main__":
    main()
