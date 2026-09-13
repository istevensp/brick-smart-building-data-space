"""Validate the graph against the SHACL shapes Brick ships with, unmodified.

The architecture adds two properties in a local namespace instead of extending
the Brick schema, so the graph should remain usable with stock Brick tooling.
This script tests that claim and reports what fails and why.

Outcome on the released model:

  - 183 violations on brick:hasUnit are an artefact of this setup, not a
    modelling error: the QUDT vocabulary is not imported into the graph, so the
    unit IRIs carry no rdf:type. Importing QUDT resolves them, and would also
    have caught the two lower-case unit:w IRIs automatically.
  - 37 violations on brick:hasLocation are real: equipment is linked with
    brick:hasLocation to rec:Zone and rec:OutdoorSpace entities, which are not
    brick:Location. This is the cost of mixing the two vocabularies.
  - 3 violations are datatype errors in the REC data (rec:levelNumber is not an
    xsd:integer, rec:logo is not an xsd:anyURI).
  - 0 violations involve espol:db_id or espol:point_type.

Usage:
    python Evaluation/06_brick_validation.py
"""

import os
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Namespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(ROOT, "Ontology")

SH = Namespace("http://www.w3.org/ns/shacl#")
ESPOL = "https://www.espol.edu.ec/ESPOL#"


def local(term):
    return str(term).split("#")[-1].split("/")[-1]


def main():
    data = Graph()
    data.parse(os.path.join(ONTOLOGY, "brickESPOLschema.ttl"), format="turtle")
    shapes = Graph()
    shapes.parse(os.path.join(ONTOLOGY, "Brick.ttl"), format="turtle")

    # QUDT is not part of the model, but Brick's shapes require unit IRIs to be
    # typed qudt:Unit. A consumer resolves that import before validating, so the
    # vocabulary is loaded into the data graph, not only into the shapes.
    qudt = os.path.join(ONTOLOGY, "QUDT-units.ttl")
    if os.path.exists(qudt):
        data.parse(qudt, format="turtle")
        print("QUDT vocabulary resolved into the data graph")

    print("graph under test : %d triples" % len(data))
    print("shapes from Brick: %d node shapes" % len(set(shapes.subjects(SH.property, None))))
    print()

    conforms, report, _ = validate(
        data, shacl_graph=shapes, ont_graph=shapes,
        inference="rdfs", abort_on_first=False)

    violations = list(report.subjects(SH.resultSeverity, SH.Violation))
    print("conforms  : %s" % conforms)
    print("violations: %d" % len(violations))
    print()

    by_path = Counter()
    on_espol = Counter()
    messages = Counter()
    for violation in violations:
        focus = list(report.objects(violation, SH.focusNode))
        path = list(report.objects(violation, SH.resultPath))
        message = list(report.objects(violation, SH.resultMessage))
        key = local(path[0]) if path else "(no path)"
        by_path[key] += 1
        if focus and str(focus[0]).startswith(ESPOL):
            on_espol[key] += 1
        if message:
            messages[str(message[0])[:70]] += 1

    print("%-26s %8s %16s" % ("property", "total", "on espol: nodes"))
    print("-" * 54)
    for key, count in sorted(by_path.items(),
                             key=lambda kv: (-kv[1], kv[0])):
        print("%-26s %8d %16d" % (key, count, on_espol[key]))
    print()
    print("messages")
    for message, count in sorted(messages.items(),
                                 key=lambda kv: (-kv[1], kv[0]))[:6]:
        print("  %4d  %s" % (count, message))
    print()

    custom = [key for key in by_path if key in ("db_id", "point_type")]
    print("violations involving the custom properties: %s"
          % (", ".join(custom) if custom else "none"))


if __name__ == "__main__":
    main()
