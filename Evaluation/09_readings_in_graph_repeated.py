"""Repeated-trial version of the readings-in-the-graph comparison.

Script 04 reports one invocation, and the conclusion it supports is a negative
one: loading the observations into the graph does not slow the metadata query.
A negative result reported from a single run is weak, because the difference it
denies is of the same order as the run-to-run variation. This script establishes
the spread so that the denial can be read against it.

The graphs are built once, since building them is expensive and deterministic.
Each trial reloads the dataset before measuring.

Usage:
    python Evaluation/09_readings_in_graph_repeated.py
    TRIALS=100 python Evaluation/09_readings_in_graph_repeated.py
"""

import base64
import json
import os
import statistics as st
import time
import urllib.parse
import urllib.request

from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL = os.path.join(ROOT, "Ontology", "brickESPOLschema.ttl")

BASE = os.environ.get("FUSEKI_BASE", "http://localhost:3030")
USER = os.environ.get("FUSEKI_USER", "admin")
PASSWORD = os.environ.get("FUSEKI_PASSWORD", "")
TRIALS = int(os.environ.get("TRIALS", "10"))
RUNS_PER_TRIAL = 40
WARMUP = 10

BRICK = Namespace("https://brickschema.org/schema/Brick#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
VOLUMES = [int(x) for x in os.environ.get("VOLUMES", "0,10,100,500").split(",")]

QUERY = """PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX espol: <https://www.espol.edu.ec/ESPOL#>
SELECT ?sensor ?equipment ?unit ?db_id
WHERE {
    ?sensor brick:isPointOf ?equipment .
    OPTIONAL { ?sensor brick:hasUnit ?unit. }
    FILTER(STRSTARTS(STR(?sensor), STR(espol:)))
    ?equipment a brick:Equipment ;
               espol:db_id ?db_id .
}"""


def call(url, data=None, method=None, content_type=None, accept=None):
    request = urllib.request.Request(url, data=data, method=method)
    if PASSWORD:
        token = base64.b64encode(("%s:%s" % (USER, PASSWORD)).encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    if content_type:
        request.add_header("Content-Type", content_type)
    if accept:
        request.add_header("Accept", accept)
    with urllib.request.urlopen(request, timeout=900) as response:
        return response.read()


def with_readings(graph, points, per_point):
    out = Graph()
    for triple in graph:
        out.add(triple)
    for point in points:
        for index in range(per_point):
            observation = URIRef("%s_obs%d" % (str(point), index))
            out.add((observation, RDF.type, SOSA.Observation))
            out.add((observation, SOSA.hasSimpleResult,
                     Literal(23.5 + index % 7, datatype=XSD.double)))
            out.add((observation, SOSA.resultTime,
                     Literal("2026-09-11T%02d:%02d:00Z"
                             % (index // 60 % 24, index % 60), datatype=XSD.dateTime)))
            out.add((observation, SOSA.madeBySensor, point))
    return out


def drop(dataset):
    try:
        call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
    except Exception:
        pass


def trial(dataset, payload):
    drop(dataset)
    call("%s/$/datasets?dbName=%s&dbType=mem" % (BASE, dataset), data=b"", method="POST")
    call("%s/%s/data?default" % (BASE, dataset), data=payload, method="PUT",
         content_type="application/n-triples")
    url = "%s/%s/sparql" % (BASE, dataset)
    body = urllib.parse.urlencode({"query": QUERY}).encode()
    for _ in range(WARMUP):
        call(url, body, accept="application/sparql-results+json")
    samples = []
    for _ in range(RUNS_PER_TRIAL):
        started = time.perf_counter()
        call(url, body, accept="application/sparql-results+json")
        samples.append((time.perf_counter() - started) * 1000)
    drop(dataset)
    return st.median(samples)


def main():
    started_all = time.perf_counter()
    graph = Graph()
    graph.parse(TTL, format="turtle")
    points = sorted(set(graph.subjects(BRICK.isPointOf, None)), key=str)
    print("measurement points: %d, %d trials each" % (len(points), TRIALS))
    print()
    print("%-26s %10s %8s %9s %9s %9s %9s %9s"
          % ("store", "triples", "MB", "median", "Q1", "Q3", "min", "max"))
    print("-" * 96)
    for per_point in VOLUMES:
        variant = graph if per_point == 0 else with_readings(graph, points, per_point)
        payload = variant.serialize(format="nt").encode("utf-8")
        medians = [trial("read%d" % per_point, payload) for _ in range(TRIALS)]
        medians.sort()
        q1 = medians[len(medians) // 4]
        q3 = medians[(3 * len(medians)) // 4]
        label = "structure only" if per_point == 0 else "+ %d readings/point" % per_point
        print("%-26s %10d %8.1f %9.1f %9.1f %9.1f %9.1f %9.1f"
              % (label, len(variant), len(payload) / 1e6,
                 st.median(medians), q1, q3, medians[0], medians[-1]))
    print()
    print("milliseconds. 500 readings per point is about 8.3 hours at one per minute.")
    print("total elapsed: %.1f s" % (time.perf_counter() - started_all))


if __name__ == "__main__":
    main()
