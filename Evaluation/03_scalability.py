"""Measure how query cost grows with the number of described devices.

The replication is SYNTHETIC: the same building is duplicated with renamed IRIs.
These are not real buildings, and the README must say so. What the experiment
measures is how the cost of a query grows with the number of devices the graph
describes, not how the system behaves across a real campus.

Temporary in-memory datasets are created through the Fuseki admin API and
deleted afterwards. The deployed dataset is never modified.

Usage:
    python Evaluation/03_scalability.py
"""

import base64
import json
import os
import statistics as st
import time
import urllib.parse
import urllib.request

from rdflib import Graph, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL = os.path.join(ROOT, "Ontology", "brickESPOLschema.ttl")

BASE = os.environ.get("FUSEKI_BASE", "http://localhost:3030")
USER = os.environ.get("FUSEKI_USER", "admin")
PASSWORD = os.environ.get("FUSEKI_PASSWORD", "")
FACTORS = [1, 2, 4, 8, 16]
ESPOL = "https://www.espol.edu.ec/ESPOL#"

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
    with urllib.request.urlopen(request, timeout=600) as response:
        return response.read()


def split_graph(graph):
    """Separate imported vocabularies from the ESPOL instance data."""
    instances, vocabulary = Graph(), Graph()
    for triple in graph:
        (instances if str(triple[0]).startswith(ESPOL) else vocabulary).add(triple)
    return vocabulary, instances


def replicate(vocabulary, instances, times):
    """Return the vocabulary plus `times` copies of the instances."""
    out = Graph()
    for triple in vocabulary:
        out.add(triple)
    for copy in range(times):
        suffix = "" if copy == 0 else "_c%d" % copy
        for subject, predicate, obj in instances:
            new_subject = URIRef(str(subject) + suffix)
            new_obj = (URIRef(str(obj) + suffix)
                       if isinstance(obj, URIRef) and str(obj).startswith(ESPOL)
                       else obj)
            out.add((new_subject, predicate, new_obj))
    return out


def measure(dataset, runs=60):
    url = "%s/%s/sparql" % (BASE, dataset)
    body = urllib.parse.urlencode({"query": QUERY}).encode()
    for _ in range(10):
        call(url, body, accept="application/sparql-results+json")
    samples, rows = [], 0
    for _ in range(runs):
        started = time.perf_counter()
        payload = call(url, body, accept="application/sparql-results+json")
        samples.append((time.perf_counter() - started) * 1000)
        rows = len(json.loads(payload)["results"]["bindings"])
    samples.sort()
    return rows, st.median(samples), samples[int(0.95 * len(samples)) - 1]


def main():
    graph = Graph()
    graph.parse(TTL, format="turtle")
    vocabulary, instances = split_graph(graph)
    print("vocabulary %d triples, instances %d triples"
          % (len(vocabulary), len(instances)))
    print()
    print("%7s %9s %9s %11s %9s" % ("factor", "equipment", "points", "median ms", "p95 ms"))
    print("-" * 50)
    for factor in FACTORS:
        dataset = "scale%d" % factor
        try:
            call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
        except Exception:
            pass
        call("%s/$/datasets?dbName=%s&dbType=mem" % (BASE, dataset),
             data=b"", method="POST")
        scaled = replicate(vocabulary, instances, factor)
        call("%s/%s/data?default" % (BASE, dataset),
             data=scaled.serialize(format="nt").encode("utf-8"),
             method="PUT", content_type="application/n-triples")
        rows, median, p95 = measure(dataset)
        print("%7d %9d %9d %11.1f %9.1f" % (factor, 37 * factor, rows, median, p95))
        try:
            call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
        except Exception:
            pass
    print()
    print("Synthetic replication of one building with renamed IRIs.")


if __name__ == "__main__":
    main()
