"""Isolate the cost of the RDFS reasoner.

Services/fuseki/config.ttl mounts the deployed dataset as a ja:InfModel with an
RDFSExptRuleReasoner on top of TDB2, so the reasoner is part of the deployment
rather than an option. This script runs the same queries over the same data with
and without it.

The script first checks that the reasoner is actually active by comparing the
number of visible triples; without that check a null result would be
indistinguishable from a misconfigured dataset.

Usage:
    python Evaluation/05_reasoner_cost.py
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
FACTORS = [1, 4, 16]

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
WITH_REASONER = """<#g> rdf:type ja:InfModel ; ja:baseModel <#base> ;
    ja:reasoner [ ja:reasonerURL <http://jena.hpl.hp.com/2003/RDFSExptRuleReasoner> ] .
<#base> rdf:type ja:MemoryModel ."""
PLAIN = """<#g> rdf:type ja:MemoryModel ."""


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


def create(name, payload, reasoning):
    try:
        call("%s/$/datasets/%s" % (BASE, name), method="DELETE")
    except Exception:
        pass
    config = (SERVICE % (name, WITH_REASONER if reasoning else PLAIN)).encode()
    call("%s/$/datasets" % BASE, data=config, method="POST", content_type="text/turtle")
    call("%s/%s/data?default" % (BASE, name), data=payload, method="PUT",
         content_type="application/n-triples")


def run(dataset, query, runs=30):
    url = "%s/%s/sparql" % (BASE, dataset)
    body = urllib.parse.urlencode({"query": query}).encode()
    for _ in range(5):
        call(url, body, accept="application/sparql-results+json")
    samples = []
    for _ in range(runs):
        started = time.perf_counter()
        call(url, body, accept="application/sparql-results+json")
        samples.append((time.perf_counter() - started) * 1000)
    return st.median(samples)


def visible_triples(dataset):
    body = urllib.parse.urlencode({"query": "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"}).encode()
    payload = call("%s/%s/sparql" % (BASE, dataset), body,
                   accept="application/sparql-results+json")
    return int(json.loads(payload)["results"]["bindings"][0]["n"]["value"])


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

    print("%-30s %8s %11s %11s %8s"
          % ("query", "points", "no RDFS", "with RDFS", "factor"))
    print("-" * 74)
    for factor in FACTORS:
        payload = replicate(factor).serialize(format="nt").encode("utf-8")
        create("plain%d" % factor, payload, False)
        create("infer%d" % factor, payload, True)
        plain_triples = visible_triples("plain%d" % factor)
        infer_triples = visible_triples("infer%d" % factor)
        if infer_triples <= plain_triples:
            raise SystemExit(
                "the reasoner is not active: %d visible triples with it, %d without"
                % (infer_triples, plain_triples))
        for name, query in QUERIES.items():
            plain = run("plain%d" % factor, query)
            infer = run("infer%d" % factor, query)
            print("%-30s %8d %8.1f ms %8.1f ms %7.1fx"
                  % (name, 214 * factor, plain, infer, infer / plain))
        print("   reasoner check: %d visible triples without, %d with"
              % (plain_triples, infer_triples))
        print("-" * 74)
        for dataset in ("plain%d" % factor, "infer%d" % factor):
            try:
                call("%s/$/datasets/%s" % (BASE, dataset), method="DELETE")
            except Exception:
                pass


if __name__ == "__main__":
    main()
