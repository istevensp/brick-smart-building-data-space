"""Repeated-trial version of the scalability measurement.

A single run of 03_scalability.py gave a median of 11.3 ms at the smallest size
on its first invocation and 8.0 ms on the two that followed. The difference was
a cold start, not the data, and it was only visible by repeating. Timing figures
reported from one invocation are therefore not reproducible, and this script
exists to replace them.

Design: each replicated graph is built once, because building it is expensive
and does not vary. Each trial then reloads the dataset from scratch before
measuring, so that the per-trial variation includes the state a freshly loaded
dataset starts from, which is what varied between invocations.

Reports median, interquartile range and extremes across trials.

Usage:
    python Evaluation/07_scalability_repeated.py            # 10 trials
    TRIALS=100 python Evaluation/07_scalability_repeated.py
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
TRIALS = int(os.environ.get("TRIALS", "10"))
FACTORS = [int(x) for x in os.environ.get("FACTORS", "1,2,4,8,16").split(",")]
RUNS_PER_TRIAL = 40
WARMUP = 10
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
    with urllib.request.urlopen(request, timeout=900) as response:
        return response.read()


def replicate(vocabulary, instances, times):
    out = Graph()
    for triple in vocabulary:
        out.add(triple)
    for copy in range(times):
        suffix = "" if copy == 0 else "_c%d" % copy
        for subject, predicate, obj in instances:
            new_obj = (URIRef(str(obj) + suffix)
                       if isinstance(obj, URIRef) and str(obj).startswith(ESPOL)
                       else obj)
            out.add((URIRef(str(subject) + suffix), predicate, new_obj))
    return out


def drop(dataset):
    try:
        call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
    except Exception:
        pass


def trial(dataset, payload):
    """Load the dataset from scratch, then measure. Returns the median."""
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
        payload_back = call(url, body, accept="application/sparql-results+json")
        samples.append((time.perf_counter() - started) * 1000)
    rows = len(json.loads(payload_back)["results"]["bindings"])
    drop(dataset)
    return st.median(samples), rows


def main():
    started_all = time.perf_counter()
    graph = Graph()
    graph.parse(TTL, format="turtle")
    instances, vocabulary = Graph(), Graph()
    for triple in graph:
        (instances if str(triple[0]).startswith(ESPOL) else vocabulary).add(triple)
    print("vocabulary %d triples, instances %d triples"
          % (len(vocabulary), len(instances)))
    print("%d trials per size, %d timed queries each" % (TRIALS, RUNS_PER_TRIAL))
    print()
    print("%8s %8s %9s %9s %9s %9s %9s"
          % ("points", "trials", "median", "Q1", "Q3", "min", "max"))
    print("-" * 68)

    for factor in FACTORS:
        payload = replicate(vocabulary, instances, factor).serialize(
            format="nt").encode("utf-8")
        medians, rows = [], 0
        for _ in range(TRIALS):
            median, rows = trial("rep%d" % factor, payload)
            medians.append(median)
        medians.sort()
        q1 = medians[len(medians) // 4]
        q3 = medians[(3 * len(medians)) // 4]
        print("%8d %8d %9.1f %9.1f %9.1f %9.1f %9.1f"
              % (rows, TRIALS, st.median(medians), q1, q3, medians[0], medians[-1]))

    print()
    print("milliseconds. Each trial reloads the dataset before measuring.")
    print("total elapsed: %.1f s" % (time.perf_counter() - started_all))


if __name__ == "__main__":
    main()
