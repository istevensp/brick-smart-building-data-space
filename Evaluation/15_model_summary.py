"""Counts of the released model that the other scripts do not report.

Scripts 01 to 14 cover the composition of the graph, its conformance and the
timings. This one derives the remaining figures the Results section uses:

  - the densest and the sparsest zone, by points and by devices;
  - how the 214 measurement points split into energy, indoor environment and
    weather station;
  - what one measurement point and one device cost in triples, which is not the
    instance graph divided by its points: that ratio also carries the spatial
    and administrative layers, which do not grow with the points;
  - the size of the administrative layer REC contributes beyond the spaces;
  - the number of MongoDB collections the deployment writes to;
  - the number of terms the Brick release carries as owl:deprecated, and
    the REC class each spatial one names as its replacement;
  - the two shapes the release carries for brick:hasLocation, which do not
    agree: the one on brick:Equipment accepts a rec:Space and the one on
    brick:Entity does not, and Equipment is an Entity;
  - the unit IRIs in use before and after the repair, by identifier.

It reads the published ontology files and needs no running deployment.

Usage:
    python Evaluation/15_model_summary.py
"""

import os
from collections import Counter, defaultdict

from rdflib import Graph, Namespace, OWL, RDF, RDFS, SH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(ROOT, "Ontology")

BRICK = Namespace("https://brickschema.org/schema/Brick#")
REC = Namespace("https://w3id.org/rec#")
ESPOL = Namespace("https://www.espol.edu.ec/ESPOL#")

ENERGY = ("Active_Power_Sensor", "Current_Sensor", "Power_Factor_Sensor",
          "Voltage_Sensor", "Power_Sensor", "Reactive_Power_Sensor",
          "Energy_Sensor")
INDOOR = ("Temperature_Sensor", "Humidity_Sensor", "CO2_Sensor")


def local(term):
    return str(term).split("#")[-1]


def main():
    g = Graph()
    g.parse(os.path.join(ONTOLOGY, "brickESPOLschema.ttl"), format="turtle")
    print("model: %d triples" % len(g))
    print()

    # ---- points per zone, through the equipment that carries them ----
    print("POINTS PER ZONE")
    print("-" * 58)
    zones = defaultdict(lambda: [0, 0])          # zone -> [equipment, points]
    for equipment in g.subjects(RDF.type, BRICK.Equipment):
        zone = g.value(equipment, BRICK.hasLocation)
        if zone is None:
            continue
        points = len(list(g.objects(equipment, BRICK.hasPoint)))
        zones[local(zone)][0] += 1
        zones[local(zone)][1] += points
    for zone, (equipment, points) in sorted(
            zones.items(), key=lambda kv: (-kv[1][1], kv[0])):
        print("  %-28s %2d equipment  %3d points" % (zone, equipment, points))
    densest = max(zones.items(), key=lambda kv: (kv[1][1], kv[0]))
    sparsest = min(zones.items(), key=lambda kv: (kv[1][1], kv[0]))
    print()
    print("  densest : %s, %d points on %d devices"
          % (densest[0], densest[1][1], densest[1][0]))
    print("  sparsest: %s, %d points on %d devices"
          % (sparsest[0], sparsest[1][1], sparsest[1][0]))
    print()

    # ---- what the 214 points measure ----
    print("WHAT THE POINTS MEASURE")
    print("-" * 58)
    station = set()
    for equipment in g.subjects(RDF.type, BRICK.Equipment):
        zone = g.value(equipment, BRICK.hasLocation)
        if zone is not None and "Jardin" in local(zone):
            station.update(g.objects(equipment, BRICK.hasPoint))
    counts = Counter()
    for point in g.subjects(BRICK.isPointOf, None):
        klass = local(g.value(point, RDF.type))
        if point in station:
            counts["weather station"] += 1
        elif klass in ENERGY:
            counts["energy"] += 1
        elif klass in INDOOR:
            counts["indoor environment"] += 1
        else:
            counts["other: " + klass] += 1
    for name in sorted(counts, key=lambda k: (-counts[k], k)):
        print("  %-28s %3d" % (name, counts[name]))
    print("  %-28s %3d" % ("TOTAL", sum(counts.values())))
    print()

    # ---- what a point and a device cost in triples ----
    print("MARGINAL COST OF A POINT AND OF A DEVICE")
    print("-" * 58)
    points = set(g.subjects(BRICK.isPointOf, None))
    equipment = set(g.subjects(RDF.type, BRICK.Equipment))
    instance = set(s for s in g.subjects() if str(s).startswith(str(ESPOL)))

    # a point pays for its own description and for the hasPoint that names it
    # on the device, which is the same link stated in the other direction
    own_points = sum(1 for s in points for _ in g.predicate_objects(s))
    has_point = sum(1 for _ in g.subject_objects(BRICK.hasPoint))
    own_equipment = (sum(1 for s in equipment for _ in g.predicate_objects(s))
                     - has_point)
    rest = sum(1 for s in (instance - points - equipment)
               for _ in g.predicate_objects(s))

    print("  a point: %d of its own + %d hasPoint = %d, or %.2f per point"
          % (own_points, has_point, own_points + has_point,
             (own_points + has_point) / len(points)))
    spread = Counter(len(list(g.predicate_objects(s))) + 1 for s in points)
    for size in sorted(spread):
        print("     %d triples : %3d points" % (size, spread[size]))
    print("  a device: %d over %d devices, or %.2f each, the hasPoint aside"
          % (own_equipment, len(equipment), own_equipment / len(equipment)))
    carried = Counter(o for _, o in g.subject_objects(BRICK.isPointOf))
    print("     and it carries between %d and %d points"
          % (min(carried.values()), max(carried.values())))
    predicates = Counter(local(p) for s in equipment for p in g.predicates(s)
                         if p != BRICK.hasPoint)
    print("     %s" % ", ".join(
        "%s %d" % (name, predicates[name])
        for name in sorted(predicates, key=lambda k: (-predicates[k], k))))
    print("  the spatial and administrative layers: %d triples, and they do"
          % rest)
    print("     not grow with the points")
    print("  %d + %d + %d = %d instance triples, %.2f per point: the density"
          % (own_points + has_point, own_equipment, rest,
             own_points + has_point + own_equipment + rest,
             (own_points + has_point + own_equipment + rest) / len(points)))
    print("     of the whole model, which is not what a new point costs")
    print()

    # ---- the administrative layer REC contributes ----
    print("ADMINISTRATIVE LAYER (what REC adds beyond spaces)")
    print("-" * 58)
    # what REC lets the model say and Brick cannot: who owns a space, which
    # department, the postal address and the level number.
    admin = []
    for predicate, obj in g.predicate_objects(ESPOL.FIEC):
        if local(predicate) == "owns":
            admin.append(("FIEC", local(predicate), local(obj)))
    for subject in g.subjects(RDF.type, REC.PostalAddress):
        admin.extend((local(subject), local(p), local(o))
                     for p, o in g.predicate_objects(subject)
                     if p != RDF.type)
    for subject in g.subjects(RDF.type, REC.Level):
        admin.extend((local(subject), local(p), local(o))
                     for p, o in g.predicate_objects(subject)
                     if local(p) == "levelNumber")
    for subject in g.subjects(RDF.type, REC.Department):
        admin.append((local(subject), "rdf:type", "rec:Department"))
    for row in admin:
        print("  %-24s %-22s %s" % row)
    print("  %-24s %d triples" % ("TOTAL", len(admin)))
    print()

    # ---- MongoDB collections named by the db_id values ----
    print("MONGODB COLLECTIONS NAMED BY espol:db_id")
    print("-" * 58)
    collections = Counter()
    for value in g.objects(None, ESPOL.db_id):
        collections[str(value).split(":")[0]] += 1
    for name in sorted(collections):
        print("  %-28s %2d equipment" % (name, collections[name]))
    print("  %-28s %d" % ("distinct collections", len(collections)))
    print()

    # ---- the broken unit IRIs, by identifier ----
    print("UNIT IRIs IN USE, BEFORE AND AFTER THE REPAIR")
    print("-" * 58)
    before = Graph()
    before.parse(os.path.join(ONTOLOGY,
                              "brickESPOLschema-before-unit-repair.ttl"),
                 format="turtle")
    # QUDT unit IRIs are slash-separated, so local() does not shorten them
    def unit_name(term):
        return str(term).rstrip("/").split("/")[-1].split("#")[-1]

    for label, graph in (("before", before), ("after", g)):
        counts = Counter(unit_name(u) for u in graph.objects(None, BRICK.hasUnit))
        print("  %s:" % label)
        for unit in sorted(counts, key=lambda k: (-counts[k], k)):
            print("     unit:%-18s %3d" % (unit, counts[unit]))
        print("     %-23s %3d" % ("TOTAL", sum(counts.values())))
    counts = Counter(unit_name(u) for u in before.objects(None, BRICK.hasUnit))
    compound = sum(counts[k] for k in ("VA", "VAR"))
    case = counts["w"]
    print()
    print("  broken identifiers: %d" % (compound + case))
    print("     compound, symbol diverges from the QUDT IRI : %d" % compound)
    print("     simple, lower-case letter (unit:w for unit:W): %d" % case)
    print()

    # ---- deprecated terms in the Brick release ----
    print("DEPRECATED TERMS IN THE BRICK DISTRIBUTION")
    print("-" * 58)
    brick = Graph()
    brick.parse(os.path.join(ONTOLOGY, "Brick.ttl"), format="turtle")
    deprecated = set(brick.subjects(OWL.deprecated, None))
    print("  terms carrying owl:deprecated : %d" % len(deprecated))
    spatial = ("Site", "Building", "Floor", "Room", "Zone", "Outdoor_Area",
               "Location")
    print("  of which the spatial classes this model replaces:")
    for name in spatial:
        replacement = brick.value(BRICK[name], BRICK.isReplacedBy)
        print("     %-16s %-14s %s"
              % ("brick:" + name,
                 "deprecated" if BRICK[name] in deprecated else "NOT deprecated",
                 "-> %s" % replacement if replacement else ""))
    print()

    # ---- the two shapes the release carries for brick:hasLocation ----
    print("SHAPES ON brick:hasLocation IN THE SAME DISTRIBUTION")
    print("-" * 58)

    def shacl_list(node):
        items = []
        while node is not None and node != RDF.nil:
            items.append(brick.value(node, RDF.first))
            node = brick.value(node, RDF.rest)
        return items

    for shape in sorted(brick.subjects(SH.path, BRICK.hasLocation), key=str):
        holders = sorted(local(h) for h in brick.subjects(SH.property, shape))
        klass = brick.value(shape, SH["class"])
        alternatives = shacl_list(brick.value(shape, SH["or"]))
        count = brick.value(shape, SH.maxCount)
        if klass is not None:
            rule = "sh:class %s" % klass
        elif alternatives:
            rule = "sh:or " + " | ".join(
                "sh:class %s" % brick.value(a, SH["class"]) for a in alternatives)
        else:
            rule = "sh:maxCount %s" % count
        print("  attached to %-12s %s" % (", ".join(holders) or "(none)", rule))

    # both reach the same nodes: Equipment is an Entity
    chain, current = [], BRICK.Equipment
    while current is not None:
        chain.append(local(current))
        current = brick.value(current, RDFS.subClassOf)
    print("  %s" % " -> ".join(chain))
    print("  so a device located at a rec:Space satisfies the Equipment shape")
    print("  and violates the Entity one")


if __name__ == "__main__":
    main()
