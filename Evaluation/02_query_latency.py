"""Measure SPARQL query latency against the deployed Fuseki endpoint.

Q1 and Q2 are the two queries printed in the paper. Q3 is the use case the
paper describes in prose: find the temperature sensors and obtain the handle
with which their readings are fetched from MongoDB.

Reported times include the HTTP round trip to localhost, which is what a client
of the Django backend actually pays.

Usage:
    python Evaluation/02_query_latency.py
    FUSEKI_URL=... FUSEKI_USER=... FUSEKI_PASSWORD=... python Evaluation/02_query_latency.py
"""

import base64
import json
import os
import statistics as st
import time
import urllib.parse
import urllib.request

ENDPOINT = os.environ.get(
    "FUSEKI_SPARQL_ENDPOINT", "http://localhost:3030/brickESPOL/sparql")
USER = os.environ.get("FUSEKI_USER", "admin")
PASSWORD = os.environ.get("FUSEKI_PASSWORD", "")

WARMUP = 20
RUNS = 200

PREFIXES = (
    "PREFIX brick: <https://brickschema.org/schema/Brick#>\n"
    "PREFIX espol: <https://www.espol.edu.ec/ESPOL#>\n"
)

QUERIES = [
    ("Q1  all sensors with equipment and db_id", PREFIXES + """
SELECT ?sensor ?equipment ?unit ?db_id
WHERE {
    ?sensor brick:isPointOf ?equipment .
    OPTIONAL { ?sensor brick:hasUnit ?unit. }
    FILTER(STRSTARTS(STR(?sensor), STR(espol:)))
    ?equipment a brick:Equipment ;
               espol:db_id ?db_id .
}"""),
    ("Q2  one point, full metadata", PREFIXES + """
SELECT ?equipment ?unit ?db_id ?type
WHERE {
    espol:airQuality1_temp brick:isPointOf ?equipment .
    OPTIONAL { espol:airQuality1_temp brick:hasUnit ?unit. }
    espol:airQuality1_temp espol:point_type ?type .
    ?equipment a brick:Equipment ;
               espol:db_id ?db_id .
}"""),
    ("Q3  temperature sensors and their handles", PREFIXES + """
SELECT ?sensor ?db_id ?type
WHERE {
    ?sensor a brick:Temperature_Sensor ;
            espol:point_type ?type ;
            brick:isPointOf ?equipment .
    ?equipment brick:hasLocation ?zone ;
               espol:db_id ?db_id .
}"""),
]


def ask(query):
    """Run one query and return (elapsed milliseconds, number of rows)."""
    body = urllib.parse.urlencode({"query": query}).encode()
    request = urllib.request.Request(ENDPOINT, data=body)
    if PASSWORD:
        token = base64.b64encode(("%s:%s" % (USER, PASSWORD)).encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    request.add_header("Accept", "application/sparql-results+json")
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    elapsed = (time.perf_counter() - started) * 1000
    return elapsed, len(json.loads(payload)["results"]["bindings"])


def main():
    print("endpoint: %s" % ENDPOINT)
    print("warm-up %d, measured runs %d" % (WARMUP, RUNS))
    print()
    print("%-44s %5s %7s %7s %7s %7s %7s"
          % ("query", "rows", "min", "median", "mean", "p95", "max"))
    print("-" * 96)
    for name, query in QUERIES:
        for _ in range(WARMUP):
            ask(query)
        samples, rows = [], 0
        for _ in range(RUNS):
            elapsed, rows = ask(query)
            samples.append(elapsed)
        samples.sort()
        print("%-44s %5d %7.1f %7.1f %7.1f %7.1f %7.1f" % (
            name, rows, samples[0], st.median(samples), st.mean(samples),
            samples[int(0.95 * len(samples)) - 1], samples[-1]))
    print()
    print("milliseconds, including the HTTP round trip.")


if __name__ == "__main__":
    main()
