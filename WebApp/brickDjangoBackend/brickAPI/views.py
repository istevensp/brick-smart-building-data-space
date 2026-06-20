from django.http import *
from django.views.decorators.csrf import csrf_exempt
import os
import re
import datetime
import json
import requests
from dotenv import load_dotenv
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from pymongo import MongoClient

load_dotenv()
fuseki_endpoint = os.getenv("FUSEKI_SPARQL_ENDPOINT")
fuseki_endpoint_post = os.getenv("FUSEKI_UPDATE_ENDPOINT")
fuseki_auth = (
    os.getenv("FUSEKI_USER"),
    os.getenv("FUSEKI_PASSWORD")
)
mongo_endpoint = os.getenv("MONGODB_ENDPOINT")

################################################# VIEWS TO RETRIEVE ALL SENSORS AND SENSOR DATA ########################################################


# Get all sensors from ESPOL's RDF schema.
def getAllSensors(request):
    # Only GET Method is allowed
    if request.method == 'GET':
        try:   
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)
            
            query = """
            PREFIX brick: <https://brickschema.org/schema/Brick#> 
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            SELECT ?sensor ?equipment ?unit ?db_id
            WHERE {
                ?sensor brick:isPointOf ?equipment .
                OPTIONAL { ?sensor brick:hasUnit ?unit. }
                FILTER(STRSTARTS(STR(?sensor), STR(espol:)))
                ?equipment a brick:Equipment ;
                            espol:db_id ?db_id .
            }
            """
            
            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")
        finally:
            try:
                store.close()
            except:
                pass
            
        data = []
        for row in response:
            data.append({
                "sensor": str(row.sensor.split("#")[-1].split("/")[-1]) if row.sensor else None,
                "equipment": str(row.equipment.split("#")[-1].split("/")[-1]) if row.equipment else None,
                "unit": str(row.unit.split("#")[-1].split("/")[-1]) if row.unit else None,
                "db": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[0]) if row.db_id else None,
                "db_id": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[-1]) if row.db_id else None
            })
            
        if not data:
            return HttpResponse("No data was found...", status=204, content_type='text/plain')
        else:
            return JsonResponse(data, safe=False)
    else: 
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type='text/plain')


# Get all sensors from a specific Equipment of ESPOL's RDF schema
def getSensorsFromEquipment(request, equipment_id):
    # Sanitize the equipment_id argument to prevent SPARQL Injection
    if not re.fullmatch(r'[A-Za-z0-9_\-]+', equipment_id):
        return HttpResponseBadRequest("Invalid equipment ID", content_type="text/plain")
    #Only GET Method is allowed
    if request.method == 'GET':
        try:
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)

            # Build a URIRef safely instead of direct string interpolation OJO al piojo
            query = f"""
            PREFIX brick: <https://brickschema.org/schema/Brick#> 
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            SELECT ?sensor ?unit ?db_id
            WHERE {{
                ?sensor brick:isPointOf espol:{equipment_id} .
                OPTIONAL {{ ?sensor brick:hasUnit ?unit. }}

                espol:{equipment_id} a brick:Equipment ;
                            espol:db_id ?db_id .
            }}
            """

            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")
        finally:
            try:
                store.close()
            except:
                pass

        data = []
        for row in response:
            data.append({
                "sensor": str(row.sensor.split("#")[-1].split("/")[-1]) if row.sensor else None,
                "unit": str(row.unit.split("#")[-1].split("/")[-1]) if row.unit else None,
                "db": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[0]) if row.db_id else None,
                "db_id": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[-1]) if row.db_id else None
            })

        if not data:
            return HttpResponse("No data was found...\nCheck entity name and try again.", status=204, content_type='text/plain')
        else:
            return JsonResponse(data, safe=False)
    else:
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type="text/plain")


# Get the last data value from a specific sensor of ESPOL's RDF schema
def getSensorData(request, sensor_id):
    # Sanitize the sensor_id argument to prevent SPARQL Injection
    if not re.fullmatch(r'[A-Za-z0-9_\-]+', sensor_id):
        return HttpResponseBadRequest("Invalid sensor ID", content_type="text/plain")
    #Only GET Method is allowed
    if request.method == 'GET':
        try:
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)

            query = f"""
            PREFIX brick: <https://brickschema.org/schema/Brick#> 
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?equipment ?unit ?db_id ?type
            WHERE {{
                espol:{sensor_id} brick:isPointOf ?equipment .
                OPTIONAL {{ espol:{sensor_id} brick:hasUnit ?unit. }}
                espol:{sensor_id} espol:point_type ?type .
                ?equipment a brick:Equipment ;
                            espol:db_id ?db_id .
            }}
            """

            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")
        finally:
            try:
                store.close()
            except:
                pass

        data = []
        for row in response:
            data.append({
                "unit": str(row.unit.split("#")[-1].split("/")[-1]) if row.unit else None,
                "db": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[0]) if row.db_id else None,
                "db_id": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[-1]) if row.db_id else None,
                "point_type" : str(row.type.split("#")[-1].split("/")[-1]) if row.type else None,
            })
        if not data:
            return HttpResponse("No data was found...\nCheck entity name and try again.", status=204, content_type='text/plain')
        else:
            try:
                mongo_client = MongoClient(mongo_endpoint)
                database = mongo_client.get_database("brickSensores")
                collection = database.get_collection(data[-1]["db"])
                mongo_query = {"metadata.sensorId": data[-1]["db_id"]}
                projection = {"_id": 0,"timestamp":1, data[-1]["point_type"]: 1, "metadata" : 1}
                last_doc = collection.find(mongo_query, projection).sort("timestamp", -1).limit(1)
                doc = next(last_doc, None)
            except Exception as e:
                return HttpResponseBadRequest(f"MongoDB query error: {str(e)}", content_type="text/plain")
            finally:
                try:
                    mongo_client.close()
                except:
                    pass
                
            return JsonResponse(doc, safe=False)
    else:
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type="text/plain")

# Get data history from a specific sensor
def getSensorDataHistory(request, sensor_id, date_from=None, date_to=None, interval='h'):
    # Sanitize the sensor_id argument to prevent SPARQL Injection
    if not re.fullmatch(r'[A-Za-z0-9_-]+', sensor_id):
        return HttpResponseBadRequest("Invalid sensor ID", content_type="text/plain")
    # Default value for argument 'date_from'
    if date_from is None:
        date_from = (datetime.date.today() - datetime.timedelta(7)).isoformat()
    # Default value for argument 'date_to'
    if date_to is None:
        date_to = datetime.date.today().isoformat()
    # Validate date arguments' values
    try:
        date_from_obj = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        date_to_obj = datetime.datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD", content_type="text/plain")
    # Validate interval argument value
    interval = interval.lower()
    if interval not in ["d", "h", "m"]:
        return HttpResponseBadRequest("Invalid interval format. Use 'd' for days, 'h' for hours, 'm' for minutes.", content_type="text/plain")
    
    match interval:
        case "d":
            group = {"year": {"$year": "$timestamp"},"month": {"$month": "$timestamp"},"day": {"$dayOfMonth": "$timestamp"}}
            sort = {"_id.year": 1, "_id.month": 1, "_id.day": 1}
        case "h":
            group = {"year": {"$year": "$timestamp"},"month": {"$month": "$timestamp"},"day": {"$dayOfMonth": "$timestamp"}, "hour":{"$hour": "$timestamp"}}
            sort = {"_id.year": 1, "_id.month": 1, "_id.day": 1, "_id.hour": 1}
        case "m":
            group = {"year": {"$year": "$timestamp"},"month": {"$month": "$timestamp"},"day": {"$dayOfMonth": "$timestamp"}, "hour":{"$hour": "$timestamp"}, "minute":{"$minute": "$timestamp"}}
            sort = {"_id.year": 1, "_id.month": 1, "_id.day": 1, "_id.hour": 1, "_id.minute": 1}
            
    if request.method == 'GET':
        try:
            # Initialize the SPARQL store
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)

            query = f"""
            PREFIX brick: <https://brickschema.org/schema/Brick#> 
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?equipment ?unit ?db_id ?type
            WHERE {{
                espol:{sensor_id} brick:isPointOf ?equipment .
                OPTIONAL {{ espol:{sensor_id} brick:hasUnit ?unit. }}
                espol:{sensor_id} espol:point_type ?type .
                ?equipment a brick:Equipment ;
                            espol:db_id ?db_id .
            }}
            """

            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")

        data = []
        for row in response:
            data.append({
                "unit": str(row.unit.split("#")[-1].split("/")[-1]) if row.unit else None,
                "db": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[0]) if row.db_id else None,
                "db_id": str(row.db_id.split("#")[-1].split("/")[-1].split(":")[-1]) if row.db_id else None,
                "point_type" : str(row.type.split("#")[-1].split("/")[-1]) if row.type else None,
            })
        store.close()
        if not data:
            return HttpResponse("No data was found...\nCheck entity name or date and try again.", status=204, content_type='text/plain')
        else:
            try:
                mongo_client = MongoClient(mongo_endpoint)
                database = mongo_client.get_database("brickSensores")
                collection = database.get_collection(data[-1]["db"])
                agg_pipeline = [
                    {
                        "$match": {
                            "timestamp": {
                                "$gte": date_from_obj,
                                "$lte": date_to_obj
                            },
                            "metadata.sensorId": data[-1]["db_id"]
                        }
                    },
                    {
                        "$project": {
                            "_id": 0, "timestamp": 1, data[-1]["point_type"]: 1, "metadata.sensorId": 1
                        }
                    },
                    {
                        "$group": {
                            "_id": group,
                            "count": {
                                "$sum": 1
                            },
                            "avg_value": {
                                "$avg": "$" + data[-1]["point_type"]
                            }
                        }
                    },
                    {
                        "$sort": sort
                    }
                ]
                results = list(collection.aggregate(agg_pipeline))
            except Exception as e:
                return HttpResponseBadRequest(f"MongoDB query error: {str(e)}", content_type="text/plain")
            finally:
                try:
                    mongo_client.close()
                except:
                    pass
                
            return JsonResponse(results, safe=False)
    else:
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type="text/plain")
    
####################################### VIEWS TO CREATE ENTITIES AND ADD THEM TO SCHEMA  ########################################################

prefixes = {
    'https://brickschema.org/schema/Brick'       : 'brick',
    'https://brickschema.org/schema/BrickShape'  : 'bsh',
    'https://www.espol.edu.ec/ESPOL'             : 'espol',
    'http://www.w3.org/2002/07/owl'              : 'owl',
    'http://qudt.org/schema/qudt/Unit'           : 'qudt',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns' : 'rdf',
    'http://www.w3.org/2000/01/rdf-schema'       : 'rdfs',
    'https://w3id.org/rec'                       : 'rec',
    'http://www.w3.org/ns/shacl'                 : 'sh',
    'https://brickschema.org/schema/BrickTag'    : 'tag',
    'http://qudt.org/vocab/unit/Unit'            : 'unit',
    'http://www.w3.org/2001/XMLSchema'           : 'xsd',
    'https://www.espol.edu.ec/ESPOL#'            : 'espol'
}

def getAllSubClasses(request, pClass):
    # Sanitize the pClass argument to prevent SPARQL Injection
    if not re.fullmatch(r'[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+', pClass):
        return HttpResponseBadRequest("Invalid class argument. Use format {prefix}:{class}. Check and try again", content_type="text/plain")
    if request.method == 'GET':
        try:
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)

            query = f"""
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rec: <https://w3id.org/rec#>
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?entity
            WHERE {{
                ?entity rdfs:subClassOf* {pClass}.
                }}
            """

            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")
        finally:
            try:
                store.close()
            except:
                pass
        raw_json = response.serialize(format="json")
        parsed = json.loads(raw_json.decode("utf-8"))
        for value in parsed["results"]["bindings"]:
            value['entity']['value'] = prefixes[value['entity']['value'].split('#')[0]] + ':' + value['entity']['value'].split('#')[-1].split('/')[-1]
        entities = sorted([binding['entity']['value'] for binding in parsed["results"]["bindings"]])
        
        return JsonResponse({'entities': entities})
    else:
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type="text/plain")
    
def getClassProperties(request, pClass):
    # Sanitize the pClass argument to prevent SPARQL Injection
    if not re.fullmatch(r'[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+', pClass):
        return HttpResponseBadRequest("Invalid class argument. Use format {prefix}:{class}. Check and try again", content_type="text/plain")
    
    prefix = str(pClass).split(":")[0]
    clss = str(pClass).split(":")[-1]
    
    if request.method == 'GET':
        try:
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)

            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rec: <https://w3id.org/rec#>
            PREFIX bsh: <https://brickschema.org/schema/BrickShape#>

            SELECT DISTINCT ?path ?target
            WHERE {{
            # Set your starting class
            BIND({prefix}:{clss} AS ?class)

            # Get class and its superclasses
            ?class rdfs:subClassOf* ?superclass .

            {{
                # --- Case 1: BRICK-style shapes using sh:targetClass ---
                ?shape a sh:NodeShape ;
                    sh:targetClass ?superclass ;
                    sh:property ?propertyShape .
            }}
            UNION
            {{
                # --- Case 2: REC-style shapes directly on the class ---
                ?superclass a sh:NodeShape ;
                            sh:property ?propertyShape .
            }}

            # Get path
            ?propertyShape sh:path ?path .

            # Get target class or node (either may be used)
            OPTIONAL {{ ?propertyShape sh:class ?target. }}
            OPTIONAL {{ ?propertyShape sh:node ?target. }}
            OPTIONAL {{ ?propertyShape sh:datatype ?target. }}
            OPTIONAL {{ 
                ?propertyShape sh:or ?list.
                ?list rdf:first ?first.
                ?first sh:datatype ?target.
            }}
            OPTIONAL {{
                ?propertyShape sh:or ?list.
                ?list rdf:first ?first.
                ?first sh:class ?target.
            }}
            OPTIONAL {{ ?propertyShape sh:in ?target. }}
            }}
            ORDER BY ?superclass ?path

            """
            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")
        finally:
            try:
                store.close()
            except:
                pass
        raw_json = response.serialize(format="json")
        parsed = json.loads(raw_json.decode("utf-8"))
        bindings = parsed["results"]["bindings"]

        path_target_map = {
            prefixes[b["path"]["value"].split('#')[0]] + ':' + b["path"]["value"].split('#')[-1].split('/')[-1]:
            prefixes[b["target"]["value"].split('#')[0]] + ':' + b["target"]["value"].split('#')[-1].split('/')[-1]
            for b in bindings
            if "path" in b and "target" in b
        }

        
        return JsonResponse(path_target_map)
    else:
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type="text/plain")
    
def getInstancesFromEspol(request: HttpRequest, pClass):
     # Sanitize the pClass argument to prevent SPARQL Injection
    if not re.fullmatch(r'[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+', pClass):
        return HttpResponseBadRequest("Invalid class argument. Use format {prefix}:{class}. Check and try again", content_type="text/plain")
    if request.method == 'GET':
        try:
            store = SPARQLStore(fuseki_endpoint, returnFormat="json", auth=fuseki_auth)
            g = Graph(store=store)
            
            query= f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rec: <https://w3id.org/rec#>
            PREFIX bsh: <https://brickschema.org/schema/BrickShape#>
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            SELECT ?instance
            WHERE {{
            BIND({pClass} AS ?class)
            ?instance a ?class .
            FILTER(STRSTARTS(STR(?instance), STR(espol:)))
            }}ORDER BY ?instance
            """
            
            response = g.query(query)
        except Exception as e:
            return HttpResponseBadRequest(f"SPARQL query error: {str(e)}", content_type="text/plain")
        finally:
            try:
                store.close()
            except:
                pass
        raw_json = response.serialize(format="json")
        parsed = json.loads(raw_json.decode("utf-8"))
        bindings = parsed["results"]["bindings"]
        
        targets = []
        for binding in bindings:
            targets.append(prefixes[binding['instance']['value'].split('#')[0]] + ':' + binding["instance"]["value"].split('#')[-1].split('/')[-1])
        
        return JsonResponse({'targets' : targets})
    else:
        return HttpResponseNotAllowed(['GET'], "Method Not Allowed", content_type="text/plain")


# """
# Formato esperado del JSON de entrada para la vista insertEntityToEspolSchema:

# {
#     "name": "NombreEntidad",                          # (string, requerido) Nombre local de la entidad a insertar.
#     "class": "Prefijo:NombreDeLaClase",               # (string, requerido) Clase RDF (IRI con prefijo) de la entidad.
#     "properties": [                                   # (array, opcional) Lista de propiedades adicionales para la entidad.
#         {
#             "predicate": "rdfs:label",                # (string, requerido) Predicado RDF (IRI con prefijo).
#             "object": "\"Mi Etiqueta\"^^xsd:tipo",    # (string, requerido) Valor del objeto.
#                                                       #   - Los literales xsd deben ir entre comillas, seguidos de '^^' y el tipo de literal (ej: "\"12.5\"^^xsd:float").
                                                      
#         },
#         {
#             "predicate": "rec:locatedIn",
#             "object": "espol:Edificio1"               #   - Los IRIs deben incluir prefijo (ej: "brick:Room").
#         }
#     ]
# }

# Notas:
# - El campo "properties" es opcional; si no se incluye, solo se inserta el triple de tipo de la entidad.
# - El valor de "object" no se auto-escapa en el servidor; el cliente debe enviar literales con comillas.
# - Prefijos soportados: rdf:, rdfs:, sh:, brick:, rec:, bsh:, espol: .
# - El servidor ignorará propiedades mal definidas que no contengan tanto "predicate" como "object".
# - El servidor ignorará propiedades en la cual el valor de '
# """

@csrf_exempt           
def insertEntityToEspolSchema(request: HttpRequest):
    if request.method != 'POST' :
        return HttpResponseNotAllowed(['POST'], "Method Not Allowed", content_type="text/plain")
    elif request.headers.get('Content-Type') != 'application/json':
        return HttpResponseBadRequest(f'Invalid Content-Type, expected \'application/json\' but {request.headers.get('Content-Type')} was found', content_type="text/plain")
    else:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Malformed JSON"}, status=400)
        if not all(k in data for k in ("name", "class")):
            return JsonResponse({"error": "Missing 'name' or 'class' field"}, status=400)

        
        # Base
        triples = [f"espol:{data['name']} a {data['class']} ."]

        # Propiedades
        for prop in data.get("properties", []):
            predicate = prop.get("predicate")
            obj = prop.get("object")
            
            if not predicate or not obj:
                continue
            
            if not re.fullmatch(r'[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+', predicate):
                return JsonResponse({"error": f"Malformed predicate '{predicate}' in properties field. Must be a prefixed IRI."}, status=400)
            
            if not (
                re.fullmatch(r'[A-Za-z0-9_\-]+:[A-Za-z0-9_\-]+', obj) or
                re.fullmatch(r'"[^"]+"(\^\^xsd:[A-Za-z0-9_\-]+)?', obj)
            ):
                return JsonResponse({"error": f"Malformed object '{obj}' in the properties field. Check and try again."}, status=400)


            triples.append(f"espol:{data['name']} {predicate} {obj} .")

        
        triples_str = "\n".join(triples)
        
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rec: <https://w3id.org/rec#>
            PREFIX bsh: <https://brickschema.org/schema/BrickShape#>
            PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT {{
                {triples_str}
            }}
            WHERE {{
                FILTER NOT EXISTS {{
                    {triples_str}
                }}
            }}
            """
        
        try:
            response = requests.post(
                fuseki_endpoint_post,
                data={"update": query},
                auth=(fuseki_auth[0], fuseki_auth[1]),
                headers={"Content-Type": "application/x-www-form-urlencoded"})

            if not response.ok:
                return HttpResponseBadRequest(f"SPARQL query error: {response.text}", content_type="text/plain")
        except Exception as e:
            return HttpResponseBadRequest(f"Error executing SPARQL UPDATE: {str(e)}", content_type="text/plain")
        
        return JsonResponse({"message": "Entity inserted successfully"}, status=200)
    
@csrf_exempt
def deleteEntityFromEspolSchema(request: HttpRequest, entity):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], "Method Not Allowed", content_type="text/plain")
    
    if not re.fullmatch(r'^espol:[A-Za-z0-9_\-]+', entity):
        return HttpResponseBadRequest("Invalid entity argument. Use format espol:{entity}. Check and try again", content_type="text/plain")

    query = f"""
    PREFIX es: <http://eulersharp.sourceforge.net/2003/03swap/log-rules#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX rec: <https://w3id.org/rec#>
    PREFIX bsh: <https://brickschema.org/schema/BrickShape#>
    PREFIX espol: <https://www.espol.edu.ec/ESPOL#> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    DELETE {{
      {entity} ?p ?o .
      ?s ?pp {entity} .
    }}
    WHERE {{
      OPTIONAL {{ {entity} ?p ?o . }}
      OPTIONAL {{ ?s ?pp {entity} . }}
    }}
    """

    try:
        response = requests.post(
            fuseki_endpoint_post,
            data={"update": query},
            auth=(fuseki_auth[0], fuseki_auth[1]),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if not response.ok:
            return HttpResponseBadRequest(f"SPARQL DELETE error: {response.text}", content_type="text/plain")

    except Exception as e:
        return HttpResponseBadRequest(f"Error executing SPARQL DELETE: {str(e)}", content_type="text/plain")

    return JsonResponse({"message": f"Entity {entity} deleted successfully"}, status=200)

    