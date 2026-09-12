"""Repeat 05 over many trials, because a single pass does not reproduce.

Script 05 runs the comparison once. The figures the paper prints from it -- 1.5x
at 214 points, 1.8 at 856, 2.2 at 3,424, and "between 1.0 and 1.1" for the
structural queries -- come from single invocations, and a later invocation of the
same script on the same data produced 1.3x, 1.6x, 2.1x and a structural factor
as low as 0.5x. A reasoner cannot make a query twice as fast; 0.5x is noise, and
its presence is enough to disqualify any single pass as evidence.

This script reports the distribution of the factor instead of one value. For
each size it builds both datasets once, then repeats a trial TRIALS times: a
fresh warm-up, a block of timed queries against the plain dataset, a block
against the inferencing one, and the ratio of the two medians. Plain and
inferencing blocks alternate inside the trial so that drift in the server
affects both.

What is reported per query and size is the median factor across trials and the
interquartile range between them. A factor whose IQR spans 1.0 is not evidence
of a cost.

Usage:
    python Evaluation/11_reasoner_cost_repeated.py
    TRIALS=40 python Evaluation/11_reasoner_cost_repeated.py
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
ESPOL = "https://www.espol.edu.ec/ESPOL#"

FACTORS = [int(x) for x in os.environ.get("FACTORS", "1,4,16").split(",")]
TRIALS = int(os.environ.get("TRIALS", "20"))
TIMED = int(os.environ.get("TIMED", "15"))

PREFIXES = (
    "PREFIX brick: <https://brickschema.org/schema/Brick#>\n"
    "PREFIX espol: <https://www.espol.edu.ec/ESPOL#>\n"
    "PREFIX rec: <https://w3id.org/rec#>\n"
)

QUERIES = {
    "hierarchy (rec:isPartOf)": PREFIXES + "SELECT ?a ?b WHERE { ?a rec:isPartOf ?b }",
    "relations (brick:isPointOf)": PREFIXES + "SELECT ?p ?e WHERE { ?p brick:isPointOf ?e }",
    "instances of a class": PREFIXES + "SELECT ?s WHERE { ?s a brick:Temperature_Sensor }",
    "metadata and handle (Q1)": PREFIXES + """SELECT ?sensor ?equipment ?unit ?db_id WHERE {
    ?sensor brick:isPointOf ?equipment .
    OPTIONAL { ?sensor brick:hasUnit ?unit. }
    FILTER(STRSTARTS(STR(?sensor), STR(espol:)))
    ?equipment a brick:Equipment ; espol:db_id ?db_id . }""",
}

SERVICE = """PREFIX fuseki: <http://jena.apache.org/fuseki#>
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ja:     <http://jena.hpl.hp.com/2005/11/Assembler#>
<#svc> rdf:type fuseki:Service ; fuseki:name "%s" ; fuseki:dataset <#ds> ;
    fuseki:endpoint [ fuseki:operation fuseki:query ; fuseki:name "sparql" ] ;
    fuseki:endpoint [ fuseki:operation fuseki:gsp-rw ; fuseki:name "data" ] .
<#ds> rdf:type ja:RDFDataset ; ja:defaultGraph <#g> .
%s
"""

PLAIN = "<#g> rdf:type ja:MemoryModel ."

WITH_REASONER = """<#g> rdf:type ja:InfModel ;
    ja:baseModel <#base> ;
    ja:reasoner [ ja:reasonerURL
        <http://jena.hpl.hp.com/2003/RDFSExptRuleReasoner> ] .
<#base> rdf:type ja:MemoryModel .
"""


def call(url, data=None, method=None, content_type=None, accept=None):
    request = urllib.request.Request(url, data=data, method=method)
    if content_type:
        request.add_header("Content-Type", content_type)
    if accept:
        request.add_header("Accept", accept)
    if PASSWORD:
        token = base64.b64encode(("%s:%s" % (USER, PASSWORD)).encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    with urllib.request.urlopen(request) as response:
        return response.read()


def create(name, payload, reasoning):
    config = (SERVICE % (name, WITH_REASONER if reasoning else PLAIN)).encode()
    call("%s/$/datasets" % BASE, data=config, method="POST", content_type="text/turtle")
    call("%s/%s/data?default" % (BASE, name), data=payload, method="PUT",
         content_type="application/n-triples")


def drop(name):
    try:
        call("%s/$/datasets/%s" % (BASE, name), method="DELETE")
    except Exception:
        pass


def block(dataset, query, warmup=3):
    """One timed block: warm up, then TIMED queries, return the median."""
    url = "%s/%s/sparql" % (BASE, dataset)
    body = urllib.parse.urlencode({"query": query}).encode()
    for _ in range(warmup):
        call(url, body, accept="application/sparql-results+json")
    samples = []
    for _ in range(TIMED):
        started = time.perf_counter()
        call(url, body, accept="application/sparql-results+json")
        samples.append((time.perf_counter() - started) * 1000)
    return st.median(samples)


def visible_triples(dataset):
    body = urllib.parse.urlencode(
        {"query": "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"}).encode()
    payload = call("%s/%s/sparql" % (BASE, dataset), body,
                   accept="application/sparql-results+json")
    return int(json.loads(payload)["results"]["bindings"][0]["n"]["value"])


def quartiles(values):
    ordered = sorted(values)
    half = len(ordered) // 2
    lower = ordered[:half]
    upper = ordered[half + 1:] if len(ordered) % 2 else ordered[half:]
    return st.median(lower), st.median(upper)


def main():
    graph = Graph()
    graph.parse(TTL, format="turtle")
    instances, vocabulary = Graph(), Graph()
    for triple in graph:
        (instances if str(triple[0]).startswith(ESPOL) else vocabulary).add(triple)

    def replicate(times):
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

    started_all = time.time()
    print("%d trials per query and size, %d timed queries per block"
          % (TRIALS, TIMED))
    print()
    print("%-30s %7s %9s %9s %16s"
          % ("query", "points", "median", "IQR", "spans 1.0?"))
    print("-" * 78)

    for factor in FACTORS:
        payload = replicate(factor).serialize(format="nt").encode("utf-8")
        plain_name, infer_name = "plain%d" % factor, "infer%d" % factor
        drop(plain_name)
        drop(infer_name)
        create(plain_name, payload, False)
        create(infer_name, payload, True)

        plain_triples = visible_triples(plain_name)
        infer_triples = visible_triples(infer_name)
        if infer_triples <= plain_triples:
            drop(plain_name)
            drop(infer_name)
            raise SystemExit(
                "the reasoner is not active: %d visible with it, %d without"
                % (infer_triples, plain_triples))

        for name, query in QUERIES.items():
            ratios = []
            for _ in range(TRIALS):
                plain = block(plain_name, query)
                infer = block(infer_name, query)
                ratios.append(infer / plain)
            low, high = quartiles(ratios)
            spans = "yes, no cost" if low <= 1.0 <= high else ""
            print("%-30s %7d %8.2fx %4.2f-%.2f %16s"
                  % (name, 214 * factor, st.median(ratios), low, high, spans))

        print("   reasoner check: %d visible triples without, %d with"
              % (plain_triples, infer_triples))
        print("-" * 78)
        drop(plain_name)
        drop(infer_name)

    print()
    print("total elapsed: %.1f s" % (time.time() - started_all))
    print("A factor whose interquartile range spans 1.0 is not evidence of a cost.")


if __name__ == "__main__":
    main()
