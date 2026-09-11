"""Audit the released graph: composition, link coverage and defects.

Reports the figures used in the Results section of the paper. Everything is
derived from Ontology/brickESPOLschema.ttl, so a reader can reproduce every
number without access to the deployment.

Usage:
    python Evaluation/01_graph_audit.py
"""

import os
from collections import Counter

from rdflib import Graph, Namespace, RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL = os.path.join(ROOT, "Ontology", "brickESPOLschema.ttl")

BRICK = Namespace("https://brickschema.org/schema/Brick#")
ESPOL = Namespace("https://www.espol.edu.ec/ESPOL#")
REC = Namespace("https://w3id.org/rec#")
QUDT_UNIT = "http://qudt.org/vocab/unit/"


def local(term):
    """Return the fragment of an IRI, e.g. brick:Room -> Room."""
    return str(term).split("#")[-1].split("/")[-1]


def main():
    g = Graph()
    g.parse(TTL, format="turtle")

    espol_subjects = {s for s in g.subjects() if str(s).startswith(str(ESPOL))}
    espol_triples = sum(1 for s, _, _ in g if str(s).startswith(str(ESPOL)))

    print("=" * 62)
    print("GRAPH COMPOSITION")
    print("=" * 62)
    print("triples in file (vocabularies + instances) : %6d" % len(g))
    print("entities in the espol: namespace           : %6d" % len(espol_subjects))
    print("triples with an espol: subject             : %6d" % espol_triples)
    print("share of the file that is instance data    : %5.1f %%"
          % (100.0 * espol_triples / len(g)))
    print()

    # Spatial and organizational layer comes from RealEstateCore, assets from Brick.
    by_class = Counter()
    for s in espol_subjects:
        for c in g.objects(s, RDF.type):
            prefix = "rec" if str(c).startswith(str(REC)) else (
                "brick" if str(c).startswith(str(BRICK)) else None)
            if prefix:
                by_class["%s:%s" % (prefix, local(c))] += 1

    print("Entities by class")
    for name, n in sorted(by_class.items(), key=lambda kv: (-kv[1], kv[0])):
        print("   %-34s %4d" % (name, n))
    print("   %-34s %4d" % ("total typed", sum(by_class.values())))
    print()

    # The join to the operational store is carried by two local properties.
    with_db_id = set(g.subjects(ESPOL.db_id, None))
    with_point_type = set(g.subjects(ESPOL.point_type, None))
    equipment = {s for s in espol_subjects if (s, RDF.type, BRICK.Equipment) in g}
    points = set(g.subjects(BRICK.isPointOf, None))

    print("=" * 62)
    print("COVERAGE OF THE LINK TO THE OPERATIONAL STORE")
    print("=" * 62)
    print("equipment carrying espol:db_id      : %3d / %3d"
          % (len(equipment & with_db_id), len(equipment)))
    print("points carrying espol:point_type    : %3d / %3d"
          % (len(points & with_point_type), len(points)))
    print("points carrying espol:db_id         : %3d / %3d   (the join is anchored"
          " at the equipment)" % (len(points & with_db_id), len(points)))
    print("triples per measurement point       : %5.1f" % (espol_triples / len(points)))
    print()

    # Defects an audit is meant to surface but a functional test is not.
    print("=" * 62)
    print("DEFECTS")
    print("=" * 62)
    units = Counter(local(o) for _, o in g.subject_objects(BRICK.hasUnit))
    bad = [(s, o) for s, o in g.subject_objects(BRICK.hasUnit)
           if str(o).startswith(QUDT_UNIT) and local(o) != local(o).upper()
           and local(o).upper() in units]
    print("unit IRIs in use                    : %3d distinct" % len(units))
    for s, o in bad:
        print("   invalid unit IRI: %s -> %s (should be %s)"
              % (local(s), local(o), local(o).upper()))
    if not bad:
        print("   no case-mismatched unit IRIs found")

    untyped = [s for s in espol_subjects if not list(g.objects(s, RDF.type))]
    print("entities without rdf:type           : %3d" % len(untyped))


if __name__ == "__main__":
    main()
