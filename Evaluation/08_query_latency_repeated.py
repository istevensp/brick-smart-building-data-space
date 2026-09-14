"""Repeated-trial version of the query latency measurement.

Script 02 reports one invocation. Repeating the scalability measurement showed
that a single invocation can land on a cold start and be off by 40 %, so the
figures reported are produced here instead: the median across trials
and the spread between them.

This measurement runs against the deployed dataset, which cannot be reloaded
between trials without disturbing it. Each trial is therefore a fresh warm-up
followed by a fresh batch of timed queries, which is what varies once the
dataset itself is fixed.

Usage:
    python Evaluation/08_query_latency_repeated.py
    TRIALS=100 python Evaluation/08_query_latency_repeated.py
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
TRIALS = int(os.environ.get("TRIALS", "10"))
RUNS_PER_TRIAL = 40
WARMUP = 10

PREFIXES = (
    "PREFIX brick: <https://brickschema.org/schema/Brick#>\n"
    "PREFIX espol: <https://www.espol.edu.ec/ESPOL#>\n"
)

QUERIES = [
    ("Q1  all sensors with equipment and handle", PREFIXES + """
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
    body = urllib.parse.urlencode({"query": query}).encode()
    request = urllib.request.Request(ENDPOINT, data=body)
    if PASSWORD:
        token = base64.b64encode(("%s:%s" % (USER, PASSWORD)).encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    request.add_header("Accept", "application/sparql-results+json")
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    return (time.perf_counter() - started) * 1000, len(
        json.loads(payload)["results"]["bindings"])


def main():
    started_all = time.perf_counter()
    print("endpoint: %s" % ENDPOINT)
    print("%d trials per query, %d timed queries each" % (TRIALS, RUNS_PER_TRIAL))
    print()
    print("%-44s %6s %9s %9s %9s %9s %9s"
          % ("query", "rows", "median", "Q1", "Q3", "min", "max"))
    print("-" * 102)
    for name, query in QUERIES:
        medians, rows = [], 0
        for _ in range(TRIALS):
            for _ in range(WARMUP):
                ask(query)
            samples = []
            for _ in range(RUNS_PER_TRIAL):
                elapsed, rows = ask(query)
                samples.append(elapsed)
            medians.append(st.median(samples))
        medians.sort()
        q1 = medians[len(medians) // 4]
        q3 = medians[(3 * len(medians)) // 4]
        print("%-44s %6d %9.1f %9.1f %9.1f %9.1f %9.1f"
              % (name, rows, st.median(medians), q1, q3, medians[0], medians[-1]))
    print()
    print("milliseconds, including the HTTP round trip.")
    print("total elapsed: %.1f s" % (time.perf_counter() - started_all))


if __name__ == "__main__":
    main()
