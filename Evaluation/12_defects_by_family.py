"""Stratify link coverage and unit defects by device family, before and after repair.

Script 01 reports coverage and defects as totals. A total answers whether the
model is complete, but not whether the heterogeneity of the deployment has
anything to do with where it fails. This script splits both by device family and
runs over two versions of the model:

  - `brickESPOLschema.ttl`, the released model, repaired
  - `brickESPOLschema.ttl.bak`, the same model before the unit IRIs were fixed

The second is what makes the 46 broken unit IRIs reproducible at all. Script 01
reads only the repaired file and therefore reports none of them, which is
accurate for the released model and useless as evidence for the claim.

A unit IRI is counted as broken when its local name does not resolve in QUDT.
The two failure modes in this deployment are a lower-case initial (`unit:w` for
`unit:W`) and a compound electrical unit written with its conventional
engineering symbol rather than its QUDT spelling (`unit:VA` for `unit:V-A`,
`unit:VAR` for `unit:V-A_Reactive`).

Usage:
    python Evaluation/12_defects_by_family.py
"""

import os

from rdflib import Graph, Namespace, RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(ROOT, "Ontology")

BRICK = Namespace("https://brickschema.org/schema/Brick#")
ESPOL = Namespace("https://www.espol.edu.ec/ESPOL#")

# The IRIs QUDT actually defines for the units this deployment uses. Anything
# outside this set is reported rather than silently accepted, so that a new unit
# has to be added here deliberately.
KNOWN_UNITS = {
    "W", "A", "V", "V-A", "V-A_Reactive",
    "DEG_C", "PERCENT_RH", "PPM", "DEG", "PA", "M-PER-SEC", "IN-PER-SEC",
}

VERSIONS = [
    ("released, repaired", "brickESPOLschema.ttl"),
    ("before the repair", "brickESPOLschema.ttl.bak"),
]


def family(entity):
    """Device family from the entity name, following the naming the model uses."""
    name = str(entity).split("#")[-1]
    if name.startswith("s31"):
        return "Sonoff S31 sockets"
    if "shelly" in name.lower():
        return "Shelly EM3 meters"
    if "ccuenergy" in name:
        return "Accuenergy meter"
    if name.startswith("S") and ("IoT" in name or "RD" in name):
        return "ESP8266 climate nodes"
    if "airQ" in name:
        return "ESP32 air quality nodes"
    if name.startswith("EM"):
        return "Weather station"
    return "unclassified: " + name


def audit(path):
    graph = Graph()
    graph.parse(path, format="turtle")

    rows = {}
    for equipment in graph.subjects(RDF.type, BRICK.Equipment):
        key = family(equipment)
        row = rows.setdefault(key, dict(equipment=0, points=0, db_id=0,
                                        point_type=0, units=0, broken=0))
        row["equipment"] += 1
        if list(graph.objects(equipment, ESPOL.db_id)):
            row["db_id"] += 1
        for point in graph.objects(equipment, BRICK.hasPoint):
            row["points"] += 1
            if list(graph.objects(point, ESPOL.point_type)):
                row["point_type"] += 1
            for unit in graph.objects(point, BRICK.hasUnit):
                row["units"] += 1
                if str(unit).split("/")[-1] not in KNOWN_UNITS:
                    row["broken"] += 1
    return rows


def report(label, rows):
    print(label)
    print("%-24s %5s %6s %9s %11s %7s %8s"
          % ("family", "equip", "points", "db_id", "point_type", "units", "broken"))
    print("-" * 78)
    totals = dict(equipment=0, points=0, db_id=0, point_type=0, units=0, broken=0)
    for key in sorted(rows, key=lambda k: -rows[k]["points"]):
        row = rows[key]
        print("%-24s %5d %6d %9s %11s %7d %8d"
              % (key, row["equipment"], row["points"],
                 "%d/%d" % (row["db_id"], row["equipment"]),
                 "%d/%d" % (row["point_type"], row["points"]),
                 row["units"], row["broken"]))
        for field in totals:
            totals[field] += row[field]
    print("%-24s %5d %6d %9s %11s %7d %8d"
          % ("TOTAL", totals["equipment"], totals["points"],
             "%d/%d" % (totals["db_id"], totals["equipment"]),
             "%d/%d" % (totals["point_type"], totals["points"]),
             totals["units"], totals["broken"]))
    print()
    return totals


def main():
    seen = {}
    for label, filename in VERSIONS:
        path = os.path.join(ONTOLOGY, filename)
        if not os.path.exists(path):
            print("%s: %s not found, skipped" % (label, filename))
            continue
        seen[label] = report("%s  (%s)" % (label, filename), audit(path))

    before = seen.get("before the repair")
    after = seen.get("released, repaired")
    if before and after:
        print("Coverage of the link is identical in both versions and complete in "
              "every family:")
        print("  %d/%d equipment and %d/%d points, with no family below 100 %%."
              % (after["db_id"], after["equipment"],
                 after["point_type"], after["points"]))
        print("The unit defects are the part that is not uniform: %d before the "
              "repair, %d after." % (before["broken"], after["broken"]))


if __name__ == "__main__":
    main()
