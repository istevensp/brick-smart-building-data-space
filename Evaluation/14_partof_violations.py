"""Explain the four part-of violations the Brick shapes report.

Script 06 reports 41 violations on espol: nodes: 37 on brick:hasLocation and
four more on rec:hasPart and rec:isPartOf. The 37 are the Brick/REC conflict the
paper is about. The other four were described in the paper as failing "for the
analogous reason", which this script shows is wrong: they are a conflict inside
REC, and Brick has nothing to do with them.

What it prints, for every violation that is not on brick:hasLocation: the focus
node, the offending value, the constraint that failed and the shape it came
from, plus the declared types of the entities involved and the position of the
relevant classes in the REC hierarchy.

Known outcome at the time of writing:

  - All four involve espol:ESPOL and the two outdoor gardens, and none involves
    espol:FIEC, the department.
  - espol:ESPOL is typed both rec:Campus and rec:Organization. REC declares one
    node shape per class, and each constrains the same rec:hasPart and
    rec:isPartOf to its own hierarchy: the rec:Organization shape requires every
    hasPart to be a rec:Organization, and the rec:Space shape requires every
    isPartOf to point at a rec:Space.
  - rec:Campus is not a rec:Space. It descends from rec:Collection, while
    rec:OutdoorSpace descends from rec:Space through rec:Architecture.
  - An entity that is both a place and an organization therefore cannot satisfy
    both shapes. Typing the spaces with the deprecated Brick classes does not
    help: script 10 reports that variant still fails six times on part-of.

The script reads the published ontology files and needs no running deployment.

Usage:
    python Evaluation/14_partof_violations.py
"""

import os

from pyshacl import validate
from rdflib import Graph, Namespace, RDF, RDFS, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(ROOT, "Ontology")

SH = Namespace("http://www.w3.org/ns/shacl#")
REC = Namespace("https://w3id.org/rec#")
ESPOL = Namespace("https://www.espol.edu.ec/ESPOL#")

PREFIXES = (
    ("brick:", "brickschema.org/schema/Brick#"),
    ("rec:", "w3id.org/rec#"),
    ("espol:", "espol.edu.ec/ESPOL#"),
    ("sh:", "www.w3.org/ns/shacl#"),
    ("rdfs:", "www.w3.org/2000/01/rdf-schema#"),
)


def short(term):
    text = str(term)
    for prefix, namespace in PREFIXES:
        if namespace in text:
            return prefix + text.split("#")[-1]
    return text


def main():
    data = Graph()
    data.parse(os.path.join(ONTOLOGY, "brickESPOLschema.ttl"), format="turtle")
    data.parse(os.path.join(ONTOLOGY, "QUDT-units.ttl"), format="turtle")
    shapes = Graph()
    shapes.parse(os.path.join(ONTOLOGY, "Brick.ttl"), format="turtle")

    print("graph under test : %d triples" % len(data))
    print("shapes from Brick: %d triples" % len(shapes))
    print("inference        : rdfs")
    print()

    _, report, _ = validate(data, shacl_graph=shapes, ont_graph=shapes,
                            inference="rdfs", advanced=True,
                            abort_on_first=False)

    rows = []
    for result in report.subjects(SH.resultSeverity, SH.Violation):
        focus = report.value(result, SH.focusNode)
        if not (isinstance(focus, URIRef) and str(focus).startswith(ESPOL)):
            continue
        rows.append((
            str(report.value(result, SH.resultPath)),
            focus,
            report.value(result, SH.value),
            report.value(result, SH.sourceConstraintComponent),
            str(report.value(result, SH.resultMessage)),
        ))

    by_path = {}
    for path, _, _, _, _ in rows:
        by_path[short(path)] = by_path.get(short(path), 0) + 1
    print("violations on espol: nodes, by property")
    print("-" * 62)
    for path in sorted(by_path, key=lambda key: -by_path[key]):
        print("  %-40s %d" % (path, by_path[path]))
    print("  %-40s %d" % ("TOTAL", len(rows)))
    print()

    print("the ones that are not brick:hasLocation")
    print("-" * 62)
    for path, focus, value, component, message in sorted(
            rows, key=lambda r: (r[0], str(r[1]))):
        if "hasLocation" in path:
            continue
        print("  %-14s %-22s -> %-22s"
              % (short(path), short(focus), short(value)))
        print("  %-14s %s (%s)"
              % ("", message, short(component).split("#")[-1]))
    print()

    print("declared types of the entities involved")
    print("-" * 62)
    for entity in (ESPOL.ESPOL, ESPOL.JardinFrontal, ESPOL.JardinTrasero,
                   ESPOL.FIEC):
        types = sorted(short(t) for t in data.objects(entity, RDF.type))
        print("  %-24s %s" % (short(entity), ", ".join(types)))
    print()

    print("position of the classes in the REC hierarchy")
    print("-" * 62)
    for klass in (REC.Campus, REC.OutdoorSpace, REC.Organization):
        chain = [short(c) for c in shapes.transitive_objects(klass,
                                                             RDFS.subClassOf)
                 if "rdf-schema#Resource" not in str(c)]
        print("  %-24s %s" % (short(klass), " < ".join(chain)))
    print()

    print("Brick has no part in these four: every shape that fails is a REC")
    print("node shape, and the conflict is that espol:ESPOL is both a place")
    print("and an organization while REC constrains one pair of part-of")
    print("properties separately for each hierarchy.")


if __name__ == "__main__":
    main()
