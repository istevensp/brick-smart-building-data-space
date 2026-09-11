"""Compare keeping the readings out of the graph against putting them in.

The architecture keeps the graph free of time series and reaches the
measurements through espol:db_id. The obvious alternative is to store the
readings in the graph as well. This script loads synthetic observations at
several volumes and measures both the size of the store and the latency of the
metadata query.

The readings are synthetic. What is measured is the effect of their presence on
the store, not their content.

Note on the result: the metadata query is largely insensitive to store size in
this range, so the argument for the separation is the size of the graph, not
query speed. Reporting it the other way round would not survive this table.

Usage:
    python Evaluation/04_readings_in_graph.py
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

BRICK = Namespace("https://brickschema.org/schema/Brick#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
VOLUMES = [0, 10, 100, 500]

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
    """Return a copy of the graph with `per_point` synthetic observations added."""
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


def measure(dataset, runs=40):
    url = "%s/%s/sparql" % (BASE, dataset)
    body = urllib.parse.urlencode({"query": QUERY}).encode()
    for _ in range(8):
        call(url, body, accept="application/sparql-results+json")
    samples = []
    for _ in range(runs):
        started = time.perf_counter()
        call(url, body, accept="application/sparql-results+json")
        samples.append((time.perf_counter() - started) * 1000)
    samples.sort()
    return st.median(samples), samples[int(0.95 * len(samples)) - 1]


def main():
    graph = Graph()
    graph.parse(TTL, format="turtle")
    points = sorted(set(graph.subjects(BRICK.isPointOf, None)), key=str)
    print("measurement points in the model: %d" % len(points))
    print()
    print("%-28s %11s %14s %11s %9s"
          % ("store", "triples", "MB (N-Triples)", "median ms", "p95 ms"))
    print("-" * 78)
    for per_point in VOLUMES:
        dataset = "readings%d" % per_point
        try:
            call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
        except Exception:
            pass
        call("%s/$/datasets?dbName=%s&dbType=mem" % (BASE, dataset),
             data=b"", method="POST")
        variant = graph if per_point == 0 else with_readings(graph, points, per_point)
        payload = variant.serialize(format="nt").encode("utf-8")
        call("%s/%s/data?default" % (BASE, dataset), data=payload,
             method="PUT", content_type="application/n-triples")
        median, p95 = measure(dataset)
        label = "structure only" if per_point == 0 else "+ %d readings/point" % per_point
        print("%-28s %11d %14.1f %11.1f %9.1f"
              % (label, len(variant), len(payload) / 1e6, median, p95))
        try:
            call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
        except Exception:
            pass
    print()
    print("500 readings per point is about 8.3 hours at one reading per minute.")


if __name__ == "__main__":
    main()
