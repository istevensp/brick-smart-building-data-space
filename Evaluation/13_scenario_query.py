"""Time the query the worked scenario actually describes.

Script 08 times three queries, and the third asks for every temperature sensor
in the building. The worked scenario is narrower: the
temperature sensors of one laboratory, reached by walking the REC spatial
hierarchy from the equipment's zone up to the laboratory it is part of. That
query was described in prose and never measured, so the scenario carried no
number.

This script runs it. The traversal is the part worth timing: the engineer names
a laboratory, not a zone, and the model has to cross rec:isPartOf to find the
equipment. For contrast it also runs the same query without the spatial
restriction, which is what script 08 measures, so the cost of the traversal can
be read off the difference.

Reported times are medians across trials with the interquartile range between
them, and each trial is a fresh warm-up followed by a block of timed queries.
Times include the HTTP round trip. The query reads the deployed dataset and
writes nothing.

Usage:
    python Evaluation/13_scenario_query.py
    TRIALS=40 python Evaluation/13_scenario_query.py
"""

import base64
import json
import os
import statistics as st
import time
import urllib.parse
import urllib.request

ENDPOINT = os.environ.get("FUSEKI_SPARQL_ENDPOINT",
                          "http://localhost:3030/brickESPOL/sparql")
USER = os.environ.get("FUSEKI_USER", "admin")
PASSWORD = os.environ.get("FUSEKI_PASSWORD", "")

TRIALS = int(os.environ.get("TRIALS", "30"))
TIMED = int(os.environ.get("TIMED", "20"))

# The laboratory the scenario names. Zones are attached to it with rec:isPartOf.
LABORATORY = os.environ.get("LABORATORY", "LabRedesDeDatos")

PREFIXES = (
    "PREFIX brick: <https://brickschema.org/schema/Brick#>\n"
    "PREFIX espol: <https://www.espol.edu.ec/ESPOL#>\n"
    "PREFIX rec:   <https://w3id.org/rec#>\n"
)

SCENARIO = PREFIXES + """
SELECT ?sensor ?unit ?point_type ?db_id
WHERE {
    ?sensor a brick:Temperature_Sensor ;
            brick:isPointOf ?equipment ;
            espol:point_type ?point_type .
    OPTIONAL { ?sensor brick:hasUnit ?unit }
    ?equipment brick:hasLocation ?zone ;
               espol:db_id ?db_id .
    ?zone rec:isPartOf espol:%s .
}""" % LABORATORY

WHOLE_BUILDING = PREFIXES + """
SELECT ?sensor ?unit ?point_type ?db_id
WHERE {
    ?sensor a brick:Temperature_Sensor ;
            brick:isPointOf ?equipment ;
            espol:point_type ?point_type .
    OPTIONAL { ?sensor brick:hasUnit ?unit }
    ?equipment brick:hasLocation ?zone ;
               espol:db_id ?db_id .
}"""

QUERIES = [
    ("scenario: one laboratory, via rec:isPartOf", SCENARIO),
    ("same query, whole building", WHOLE_BUILDING),
]


def ask(query):
    body = urllib.parse.urlencode({"query": query}).encode()
    request = urllib.request.Request(ENDPOINT, data=body)
    request.add_header("Accept", "application/sparql-results+json")
    if PASSWORD:
        token = base64.b64encode(("%s:%s" % (USER, PASSWORD)).encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    started = time.perf_counter()
    with urllib.request.urlopen(request) as response:
        payload = response.read()
    elapsed = (time.perf_counter() - started) * 1000
    rows = len(json.loads(payload)["results"]["bindings"])
    return elapsed, rows


def quartiles(values):
    ordered = sorted(values)
    half = len(ordered) // 2
    lower = ordered[:half]
    upper = ordered[half + 1:] if len(ordered) % 2 else ordered[half:]
    return st.median(lower), st.median(upper)


def main():
    print("endpoint: %s" % ENDPOINT)
    print("laboratory: espol:%s" % LABORATORY)
    print("%d trials per query, %d timed queries each" % (TRIALS, TIMED))
    print()
    print("%-44s %6s %9s %12s" % ("query", "rows", "median", "IQR"))
    print("-" * 76)

    results = {}
    for label, query in QUERIES:
        _, rows = ask(query)
        medians = []
        for _ in range(TRIALS):
            for _ in range(3):
                ask(query)
            samples = [ask(query)[0] for _ in range(TIMED)]
            medians.append(st.median(samples))
        low, high = quartiles(medians)
        print("%-44s %6d %8.1f %5.1f-%.1f"
              % (label, rows, st.median(medians), low, high))
        results[label] = (st.median(medians), rows)

    print()
    scenario = results["scenario: one laboratory, via rec:isPartOf"]
    building = results["same query, whole building"]
    print("The spatial restriction narrows %d rows to %d and changes the median "
          "by %+.1f ms." % (building[1], scenario[1], scenario[0] - building[0]))
    print("milliseconds, including the HTTP round trip.")


if __name__ == "__main__":
    main()
