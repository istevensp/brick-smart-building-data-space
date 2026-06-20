import brickschema
from brickschema.namespaces import A, BRICK, TAG, UNIT
from rdflib import Namespace, Literal, RDF, RDFS, XSD, OWL, SH, BNode

# Namespaces adicionales
REC = Namespace("https://w3id.org/rec#") # Namespace para l aontología Real State Core
ESPOL = Namespace("https://www.espol.edu.ec/ESPOL#")  # Namespace para ESPOL

# Crear grafo
g = brickschema.Graph(load_brick=True)
g.bind("espol", ESPOL)
g.bind("rec", REC)
g.bind("brick", BRICK)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)
g.bind("unit", UNIT)  # Bind de UNIT para las unidades estándar
g.bind("sh", SH)
g.bind("owl", OWL)

# Mapeo de clase de sensor → unidad correspondiente
CLASS_TO_UNIT = {
    "Active_Power_Sensor":      "W",           # Watts
    "Power_Sensor":             "VA",          # Volt-Amperios
    "Reactive_Power_Sensor":    "VAR",         # Volt-Amperios Reactivos
    "Power_Factor_Sensor":      None,          # adimensional valor solo de 100 o 0
    "Current_Sensor":           "A",           # Amperios
    "Voltage_Sensor":           "V",           # Voltios
    "Rain_Level_Sensor":        "IN-PER-SEC",  # pulgada por segundo es una unidad de velocidad
    "Temperature_Sensor":       "DEG_C",       # Celsius (para temperatura)
    "Humidity_Sensor":          "PERCENT_RH",  # Porcentaje (para humedad relativa)
    "Pressure_Sensor":          "PA",          # Pascales (para presión)
    "CO2_Sensor":               "PPM"          # partes por millón (ppm)
    "Energy_Sensor"             "W"            # Watts
    "Wind_Speed_Sensor"         "M-PER-SEC"    # m/s (metro sobre segundo)
    "Wind_Direction_Sensor"     "DEG"          #Un grado, representa 1/360 de una rotación completa 
    # Ir agregando otras clases de sensores según sea necesario
}

# Declarar la propiedad personalizada de db_id, que usaremos para hacer consultas a MongoDB
g.add((ESPOL["db_id"], A, RDF.Property))
g.add((ESPOL["db_id"], RDFS.label, Literal("db_id")))  # human-readable label
g.add((ESPOL["db_id"], RDFS.comment, Literal("MongoDB sensor ID for linking sensor metadata.")))

# Declarar las propiedad como una clase PropertyShape para validación SHACL
g.add((ESPOL["db_idShape"], A, SH.PropertyShape))
g.add((ESPOL["db_idShape"], SH.maxCount, Literal(1, datatype=XSD.integer)))
g.add((ESPOL["db_idShape"], SH.path, ESPOL["db_id"]))
g.add((ESPOL["db_idShape"], SH.datatype, XSD.string))

# Añadir la propiedad SHACL al esquema brick (brick:Point)
g.add((BRICK.Point, SH.property, ESPOL["db_idShape"]))

# Declarar la propiedad personalizada de point_type, que usaremos para hacer consultas a MongoDB
g.add((ESPOL["point_type"], A, RDF.Property))
g.add((ESPOL["point_type"], RDFS.label, Literal("point_type")))  # human-readable label
g.add((ESPOL["point_type"], RDFS.comment, Literal("MongoDB sensor point type for linking sensor metadata.")))

# Declarar las propiedad como una clase PropertyShape para validación SHACL
g.add((ESPOL["point_typeShape"], A, SH.PropertyShape))
g.add((ESPOL["point_typeShape"], SH.maxCount, Literal(1, datatype=XSD.integer)))
g.add((ESPOL["point_typeShape"], SH.path, ESPOL["point_type"]))
g.add((ESPOL["point_typeShape"], SH.datatype, XSD.string))

# Añadir la propiedad SHACL al esquema brick (brick:Point)
g.add((BRICK.Point, SH.property, ESPOL["point_typeShape"]))

# Definir las direcciones con la Clase PostalAddress
g.add((ESPOL["espolPA"], A, REC["PostalAddress"]))
g.add((ESPOL["espolPA"], REC.addressLine1, Literal("Prosperina, Km 30.5 de la Vía Perimetral")))
g.add((ESPOL["espolPA"], REC.city, Literal("Guayaquil")))
g.add((ESPOL["espolPA"], REC.country, Literal("Ecuador")))
g.add((ESPOL["espolPA"], REC.postalCode, Literal("EC090112")))

g.add((ESPOL["fiecPA"], A, REC["PostalAddress"]))
g.add((ESPOL["fiecPA"], REC.addressLine1, Literal("V24J+4RX")))
g.add((ESPOL["fiecPA"], REC.city, Literal("Guayaquil")))
g.add((ESPOL["fiecPA"], REC.country, Literal("Ecuador")))
g.add((ESPOL["fiecPA"], REC.postalCode, Literal("EC090112")))

# Nodo 1: ESPOL - Campus, Organization (Collection, Agent)
g.add((ESPOL["ESPOL"], A, REC["Campus"]))
g.add((ESPOL["ESPOL"], A, REC["Organization"]))
g.add((ESPOL["ESPOL"], REC.hasPart, ESPOL["FIEC"])) # Organization Property to domain(Department)
g.add((ESPOL["ESPOL"], RDFS.label, Literal("Escuela Superior Politécnica del Litoral")))
g.add((ESPOL["ESPOL"], REC.includes, ESPOL["11C"])) # Campus property to domain(Architecture, Space)

# Nodo 2: FIEC - Department (Agent)
g.add((ESPOL["FIEC"], A, REC["Department"]))
g.add((ESPOL["FIEC"], REC.logo, Literal("https://www.fiec.espol.edu.ec/sites/fiec.espol.edu.ec/files/logoFIEC2022.jpg"))) # Department property
g.add((ESPOL["FIEC"], REC.isPartOf, ESPOL["ESPOL"])) # Department property to domain(Organization)
g.add((ESPOL["FIEC"], REC.owns, ESPOL["11C"])) # Department property to domain(Resource)

# Nodo 3: Edificio 11C - Building (Space)
g.add((ESPOL["11C"], A, REC["Building"]))
g.add((ESPOL["11C"], REC.address, ESPOL["fiecPA"])) # Building property
g.add((ESPOL["11C"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)
# g.add((ESPOL["11C"], REC.operator, Literal("Ph. D. Jorge Aragundi Rodríguez")))
g.add((ESPOL["11C"], REC.hasPart, ESPOL["11C-Piso1"])) # Space property to domain(Space)
g.add((ESPOL["11C"], REC.hasPart, ESPOL["11C-Piso2"])) # Space property to domain(Space)

# Nodo 4: Edificio 11C - Pisos - Level (Space)
g.add((ESPOL["11C-Piso1"], A, REC["Level"]))
g.add((ESPOL["11C-Piso2"], A, REC["Level"]))
g.add((ESPOL["11C-Piso1"], REC.levelNumber, Literal('1'))) # Level Property
g.add((ESPOL["11C-Piso2"], REC.levelNumber, Literal('2'))) # Level Property
g.add((ESPOL["11C-Piso1"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)
g.add((ESPOL["11C-Piso2"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)
g.add((ESPOL["11C-Piso1"], REC.isPartOf, ESPOL["11C"])) # Space property to domain(Space)
g.add((ESPOL["11C-Piso2"], REC.isPartOf, ESPOL["11C"])) # Space property to domain(Space)
g.add((ESPOL["11C-Piso1"], BRICK.hasTag, TAG["Floor"]))
g.add((ESPOL["11C-Piso2"], BRICK.hasTag, TAG["Floor"]))
g.add((ESPOL["11C-Piso1"], REC.hasPart, ESPOL["LabIoT"])) # Space property to domain(Space)
g.add((ESPOL["11C-Piso1"], REC.hasPart, ESPOL["JardinFrontal"])) # Space property to domain(Space)
g.add((ESPOL["11C-Piso1"], REC.hasPart, ESPOL["JardinTrasero"])) # Space property to domain(Space)
g.add((ESPOL["11C-Piso2"], REC.hasPart, ESPOL["LabRedesDeDatos"])) # Space property to domain(Space)
g.add((ESPOL["11C-Piso2"], REC.hasPart, ESPOL["LabSistemasEnLaNube"])) # Space property to domain(Space)

# Nodo 5: lab_telematica - Laboratory (Space)
g.add((ESPOL["LabIoT"], A, REC["Laboratory"]))
g.add((ESPOL["LabIoT"], REC.isPartOf, ESPOL["11C-Piso1"])) # Space property to domain(Space)
g.add((ESPOL["LabIoT"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)
# g.add((ESPOL["LabIoT"], BRICK.designer, ESPOL["FIEC"]))
# g.add((ESPOL["LabIoT"], BRICK.creator, ESPOL["FIEC"]))
# g.add((ESPOL["LabIoT"], BRICK.operator, Literal("Ing. Sandra Isabella Coello Suarez")))

# Nodo 6: Jardin frontal - OutdoorSpace
g.add((ESPOL["JardinFrontal"], A, REC["OutdoorSpace"]))
g.add((ESPOL["JardinFrontal"], REC.isPartOf, ESPOL["11C-Piso1"]))    # Cambie aqui al edificio 1 piso 1 porque el jardin esta en ese lugar especificamente
g.add((ESPOL["JardinFrontal"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)

# Nodo 7: Jardín Trasero - OutdoorSpace
g.add((ESPOL["JardinTrasero"], A, REC["OutdoorSpace"]))
g.add((ESPOL["JardinTrasero"], REC.isPartOf, ESPOL["11C-Piso1"]))     # Cambie aqui al edificio 1 piso 1 porque el jardin esta en ese lugar especificamente
g.add((ESPOL["JardinTrasero"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)

#nodo 8: Lab_RedesDeDatos
g.add((ESPOL["LabRedesDeDatos"], A, REC["Laboratory"]))
g.add((ESPOL["LabRedesDeDatos"], REC.isPartOf, ESPOL["11C-Piso2"]))
g.add((ESPOL["LabRedesDeDatos"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)
# g.add((ESPOL["LabRedesDeDatos"], BRICK.designer, ESPOL["FIEC"]))
# g.add((ESPOL["LabRedesDeDatos"], BRICK.creator, ESPOL["FIEC"]))
# g.add((ESPOL["LabRedesDeDatos"], BRICK.operator, Literal("Mgtr. NESTOR XAVIER ARREAGA ALVARADO")))

# Nodo 9: Lab_SistemasEnLaNube
g.add((ESPOL["LabSistemasEnLaNube"], A, REC["Laboratory"]))
g.add((ESPOL["LabSistemasEnLaNube"], REC.isPartOf, ESPOL["11C-Piso2"]))
g.add((ESPOL["LabSistemasEnLaNube"], REC.ownedBy, ESPOL["FIEC"])) # Owned by an Agent Class (Department)
# g.add((ESPOL["LabSistemasEnLaNube"], BRICK.designer, ESPOL["FIEC"]))
# g.add((ESPOL["LabSistemasEnLaNube"], BRICK.creator, ESPOL["FIEC"]))
# g.add((ESPOL["LabSistemasEnLaNube"], BRICK.operator, Literal("Mgtr. NELSON VICENTE VERA MENDEZ")))

# Nodo 10: Zonas del laboratorio Telematica
zonas_sensores_LabIoT = {
    "ZonaOficina": {
        "s31_01": {  # ID del sensor
            "db_id": "11C-LabIoT:s31_01", # ESPOL:db_id Literal("s31_01")
            "point": [
                {"id": "s31_01_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"}, 
                {"id": "s31_01_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_01_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_01_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},  # Sin unidad
                {"id": "s31_01_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_01_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
        "s31_02": {  # ID del sensor
            "db_id": "11C-LabIoT:s31_02", # ESPOL:db_id Literal("s31_02")
            "point": [
                {"id": "s31_02_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_02_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_02_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_02_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_02_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_02_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
        "s31_05": { # ID del sensor
            "db_id": "11C-LabIoT:s31_05", #ESPOL:db_id Literal("s31_05")
            "point": [
                {"id": "s31_05_ActivePower",   "class": "Active_Power_Sensor",   "unit":"w", "type":"power"},
                {"id": "s31_05_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_05_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_05_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_05_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_05_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        }    
    },
    
    "ZonaBaño": {   
        "S3IoT":{ # ID del sensor
            "db_id":"11C-LabIoT:airClimate3", #ESPOL:db_id Literal("airClimate3")
            "point": [ 
                {"id": "S3IoT_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S3IoT_Humedad",     "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        },
        "s31_06":{ # ID del sensor
            "db_id":"11C-LabIoT:s31_06", #ESPOL:db_id Literal("s31_06")
            "point": [
                {"id": "s31_06_ActivePower",   "class": "Active_Power_Sensor",   "unit":"w", "type":"power"},
                {"id": "s31_06_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_06_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_06_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_06_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_06_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        }    
    },
    
    "ZonaEntrada": {
        "airQuality1":{ #ID del sensor
            "db_id":"11C-LabIoT:airQ1", #ESPOL:db_id Literal("airQ1")
            "point": [
                {"id": "airQuality1_co2",      "class":"CO2_Sensor",          "unit":"PPM", "type":"co2_concentration"},
                {"id": "airQuality1_humidity", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"},
                {"id": "airQuality1_temp",     "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"}
            ]
        },
        "airQuality2":{ #ID del sensor
            "db_id":"11C-LabIoT:airQ2", #ESPOL:db_id Literal("airQ2")
            "point": [
                {"id": "airQuality2_co2",      "class":"CO2_Sensor",          "unit":"PPM", "type":"co2_concentration"},
                {"id": "airQuality2_humidity", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"},
                {"id": "airQuality2_temp",     "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"}
            ]
        }    
    },
    
    "ZonaLavadero": {
        "S2IoT":{ #ID del sensor
            "db_id":"11C-LabIoT:airClimate2", #ESPOL:db_id Literal("airClimate2")
            "point": [
                {"id": "S2IoT_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S2IoT_Humedad",     "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        },
        "S4IoT":{ #ID del sensor
            "db_id":"11C-LabIoT:airClimate4", #ESPOL:db_id Literal("airClimate4")
            "point": [
                {"id": "S4IoT_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S4IoT_Humedad", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        },    
        "s31_10":{ #ID del sensor
            "db_id":"11C-LabIoT:s31_10", #ESPOL:db_id Literal("s31_10")
            "point": [
                {"id": "s31_10_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_10_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_10_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_10_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_10_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_10_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
        "s31_11":{ #ID del sensor
            "db_id":"11C-LabIoT:s31_11", #ESPOL:db_id Literal("s31_11")
            "point": [
                {"id": "s31_11_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_11_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_11_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_11_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_11_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_11_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        }
    },
    
    "ZonaMesones": {
        "S1IoT":{ #ID del sensor
            "db_id":"11C-LabIoT:airClimate1", #ESPOL:db_id Literal("airClimate1")
            "point": [
                {"id": "S1IoT_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S1IoT_Humedad",     "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        },
        "airQuality3":{ #ID del sensor
            "db_id":"11C-LabIoT:airQ3", #ESPOL:db_id Literal("airQ3")
            "point": [
                {"id": "airQuality3_co2",      "class":"CO2_Sensor",          "unit":"PPM", "type":"co2-concentration"},
                {"id": "airQuality3_humidity", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"},
                {"id": "airQuality3_temp",     "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"}
            ]
        },
        "airQuality4":{ #ID del sensor
            "db_id":"11C-LabIoT:airQ4", #ESPOL:db_id Literal("airQ4")
            "point": [
                {"id": "airQuality4_co2",      "class":"CO2_Sensor",          "unit":"PPM", "type":"co2-concentration"},
                {"id": "airQuality4_humidity", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"},
                {"id": "airQuality4_temp",     "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"}
            ]
        },
        "s31_08":{ #ID del sensor
            "db_id":"11C-LabIoT:s31_08", #ESPOL:db_id Literal("s31_08")            
            "point": [
                {"id": "s31_08_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_08_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_08_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_08_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_08_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_08_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
        "s31_09":{ #ID del sensor
            "db_id":"11C-LabIoT:s31_09", #ESPOL:db_id Literal("s31_09")
            "point": [
                {"id": "s31_09_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_09_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_09_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_09_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_09_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_09_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
    },
    
    "ZonaPaneles": {
        "S5IoT":{ #ID del sensor
            "db_id":"11C-LabIoT:airClimate5", #ESPOL:db_id Literal("airClimate5")
            "point": [
                {"id": "S5IoT_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S5IoT_Humedad",     "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        },
        "airQuality5":{ #ID del sensor
            "db_id":"11C-LabIoT:airQ5", #ESPOL:db_id Literal("airQ5")
            "point": [
                {"id": "airQuality5_co2",      "class":"CO2_Sensor",          "unit":"PPM", "type":"co2-concentration"},
                {"id": "airQuality5_humidity", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"},
                {"id": "airQuality5_temp",     "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"}
            ]
        },
        "Shelly":{ #ID del sensor
            "db_id":"11C-LabIoT:shellyem3-349454756742", #ESPOL:db_id Literal("shellyem3-349454756742")
            "point": [
                {"id": "Shelly_voltaje_A",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageA"},
                {"id": "Shelly_voltaje_B",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageB"},
                {"id": "Shelly_voltaje_C",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageC"},
                {"id": "Shelly_energia_A",         "class": "Energy_Sensor",         "unit": "W", "type":"energyA"},
                {"id": "Shelly_energia_B",         "class": "Energy_Sensor",         "unit": "W", "type":"energyB"},
                {"id": "Shelly_energia_C",         "class": "Energy_Sensor",         "unit": "W", "type":"energyC"},
                {"id": "Shelly_factor_potencia_A", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfA"},
                {"id": "Shelly_factor_potencia_B", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfB"},
                {"id": "Shelly_factor_potencia_C", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfC"},
                {"id": "Shelly_potencia_A",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerA"},
                {"id": "Shelly_potencia_B",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerB"},
                {"id": "Shelly_potencia_C",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerC"},
                {"id": "Shelly_corriente_A",       "class": "Current_Sensor",        "unit": "A", "type":"currentA"},
                {"id": "Shelly_corriente_B",       "class": "Current_Sensor",        "unit": "A", "type":"currentB"},
                {"id": "Shelly_corriente_C",       "class": "Current_Sensor",        "unit": "A", "type":"currentC"}
            ]
        },
        "Shelly_Iz":{ #ID del sensor
            "db_id":"11C-LabIoT:shellyem3-485519DC84EC", #ESPOL:db_id Literal("shellyem3-485519DC84EC")
            "point": [
                {"id": "Shelly_Iz_voltaje_A",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageA"},
                {"id": "Shelly_Iz_voltaje_B",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageB"},
                {"id": "Shelly_Iz_voltaje_C",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageC"},
                {"id": "Shelly_Iz_energia_A",         "class": "Energy_Sensor",         "unit": "W", "type":"energyA"},
                {"id": "Shelly_Iz_energia_B",         "class": "Energy_Sensor",         "unit": "W", "type":"energyB"},
                {"id": "Shelly_Iz_energia_C",         "class": "Energy_Sensor",         "unit": "W", "type":"energyC"},
                {"id": "Shelly_Iz_factor_potencia_A", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfA"},
                {"id": "Shelly_Iz_factor_potencia_B", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfB"},
                {"id": "Shelly_Iz_factor_potencia_C", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfC"},
                {"id": "Shelly_Iz_potencia_A",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerA"},
                {"id": "Shelly_Iz_potencia_B",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerB"},
                {"id": "Shelly_Iz_potencia_C",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerC"},
                {"id": "Shelly_Iz_corriente_A",       "class": "Current_Sensor",        "unit": "A", "type":"currentA"},
                {"id": "Shelly_Iz_corriente_B",       "class": "Current_Sensor",        "unit": "A", "type":"currentB"},
                {"id": "Shelly_Iz_corriente_C",       "class": "Current_Sensor",        "unit": "A", "type":"currentC"}
            ]
        },
        "Shelly_Der":{ #ID del sensor
            "db_id":"11C-LabIoT:shellyem3-C45BBE5FD50D", #ESPOL:db_id Literal("shellyem3-C45BBE5FD50D")
            "point": [
                {"id": "Shelly_Der_voltaje_A",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageA"},
                {"id": "Shelly_Der_voltaje_B",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageB"},
                {"id": "Shelly_Der_voltaje_C",         "class": "Voltage_Sensor",        "unit": "V", "type":"voltageC"},
                {"id": "Shelly_Der_energia_A",         "class": "Energy_Sensor",         "unit": "W", "type":"energyA"},
                {"id": "Shelly_Der_energia_B",         "class": "Energy_Sensor",         "unit": "W", "type":"energyB"},
                {"id": "Shelly_Der_energia_C",         "class": "Energy_Sensor",         "unit": "W", "type":"energyC"},
                {"id": "Shelly_Der_factor_potencia_A", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfA"},
                {"id": "Shelly_Der_factor_potencia_B", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfB"},
                {"id": "Shelly_Der_factor_potencia_C", "class": "Power_Factor_Sensor",   "unit": None, "type":"pfC"},
                {"id": "Shelly_Der_potencia_A",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerA"},
                {"id": "Shelly_Der_potencia_B",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerB"},
                {"id": "Shelly_Der_potencia_C",        "class": "Active_Power_Sensor",   "unit": "W", "type":"powerC"},
                {"id": "Shelly_Der_corriente_A",       "class": "Current_Sensor",        "unit": "A", "type":"currentA"},
                {"id": "Shelly_Der_corriente_B",       "class": "Current_Sensor",        "unit": "A", "type":"currentB"},
                {"id": "Shelly_Der_corriente_C",       "class": "Current_Sensor",        "unit": "A", "type":"currentC"}
            ]
        },
        "s31_03":{ #ID del sensor
            "db_id":"11C-LabIoT:s31_03", #ESPOL:db_id Literal("s31_03")
            "point": [
                {"id": "s31_03_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_03_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_03_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_03_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_03_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_03_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
        "s31_07":{ #ID del sensor
            "db_id":"11C-LabIoT:s31_07", #ESPOL:db_id Literal("s31_07")
            "point":[
                {"id": "s31_07_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_07_ApparentPower", "class": "Power_Sensor",         "unit": "VA", "type":"apparentpower"},
                {"id": "s31_07_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_07_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_07_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
                {"id": "s31_07_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"}
            ]
        },
        "Accuenergy":{ #ID del sensor
            "db_id":"11C-LabIoT:Accuenergy", #ESPOL:db_id Literal("Accuenergy")
            "point": [
                {"id": "Accuenergy_voltaje_A",              "class": "Voltage_Sensor",        "unit": "V", "type":"voltageA"},
                {"id": "Accuenergy_voltaje_B",              "class": "Voltage_Sensor",        "unit": "V", "type":"voltageB"},
                {"id": "Accuenergy_voltaje_C",              "class": "Voltage_Sensor",        "unit": "V", "type":"voltageC"},
                {"id": "Accuenergy_potencia_aparente_A",    "class": "Power_Sensor",          "unit": "VA", "type":"apparentpowerA"},
                {"id": "Accuenergy_potencia_aparente_B",    "class": "Power_Sensor",          "unit": "VA", "type":"apparentpowerB"},
                {"id": "Accuenergy_potencia_aparente_C",    "class": "Power_Sensor",          "unit": "VA", "type":"apparentpowerC"},
                {"id": "Accuenergy_factor_potencia_A",      "class": "Power_Factor_Sensor",   "unit": None, "type":"pfA"},
                {"id": "Accuenergy_factor_potencia_B",      "class": "Power_Factor_Sensor",   "unit": None, "type":"pfB"},
                {"id": "Accuenergy_factor_potencia_C",      "class": "Power_Factor_Sensor",   "unit": None, "type":"pfC"},
                {"id": "Accuenergy_potencia_A",             "class": "Active_Power_Sensor",   "unit": "W", "type":"powerA"},
                {"id": "Accuenergy_potencia_B",             "class": "Active_Power_Sensor",   "unit": "W", "type":"powerB"},
                {"id": "Accuenergy_potencia_C",             "class": "Active_Power_Sensor",   "unit": "W", "type":"powerC"},
                {"id": "Accuenergy_corriente_A",            "class": "Current_Sensor",        "unit": "A", "type":"currentA"},
                {"id": "Accuenergy_corriente_B",            "class": "Current_Sensor",        "unit": "A", "type":"currentB"},
                {"id": "Accuenergy_corriente_C",            "class": "Current_Sensor",        "unit": "A", "type":"currentC"},
                {"id": "Accuenergy_potencia_reactiva_A",    "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepowerA"},
                {"id": "Accuenergy_potencia_reactiva_B",    "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepowerB"},
                {"id": "Accuenergy_potencia_reactiva_C",    "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepowerC"}
            ]
        }
    },
    
    "JardinFrontal": {
        "EM-LIoTST":{ #ID del sensor
            "db_id":"11C-LabIoT:EST_MET", #ESPOL:db_id Literal("EST_MET")
            "point": [
                {"id": "EM-LIoTST_Temperatura",      "class": "Temperature_Sensor",    "unit": "DEG_C", "type":"temperature"},
                {"id": "EM-LIoTST_Humedad_Relativa", "class": "Humidity_Sensor",       "unit": "PERCENT_RH", "type":"humidity"},
                {"id": "EM-LIoTST_PresBarometrica",  "class": "Pressure_Sensor",       "unit": "PA", "type":"pressure"},
                {"id": "EM-LIoTST_VelViento",        "class": "Wind_Speed_Sensor",     "unit": "M-PER-SEC", "type":"velocity"},
                {"id": "EM-LIoTST_Direccion_Viento", "class": "Wind_Direction_Sensor", "unit": "DEG", "type":"direction"},
                {"id": "EM-LIoTST_Precipitacion",    "class": "Rain_Level_Sensor",     "unit": "IN-PER-SEC", "type":"precipitation"}
            ]
        }
    }
}

# Nodo 11: Zonas del laboratorio Sistemas En La Nube
zonas_Sensores_LabSitemasNube = {
    "ZonaOficinaRacks": {
        "s31_19_Router":{ #ID del sensor
            "db_id":"11C-LabSN:s31_19", #ESPOL:db_id Literal("s31_19")
            "point": [
                {"id": "s31_19_Router_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_19_Router_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_19_Router_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_19_Router_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_19_Router_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_19_Router_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        },
        "s31_20_Server":{ #ID del sensor
            "db_id":"11C-LabSN:s31_20", #ESPOL:db_id Literal("s31_20")
            "point": [
                {"id": "s31_20_Server_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_20_Server_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_20_Server_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_20_Server_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_20_Server_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_20_Server_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        }
    },
    "ZonaVentana1": {
        "s31_13_Profesor":{  #ID del sensor
            "db_id":"11C-LabSN:s31_13", #ESPOL:db_id Literal("s31_13")
            "point": [
                {"id": "s31_13_Profesor_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_13_Profesor_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_13_Profesor_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_13_Profesor_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_13_Profesor_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_13_Profesor_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        },
        "s31_14":{  #ID del sensor
            "db_id":"11C-LabSN:s31_14", #ESPOL:db_id Literal("s31_14")
            "point": [
                {"id": "s31_14_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_14_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_14_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_14_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_14_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_14_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        }
    },
    "ZonaVentana2": {
        "s31_16":{  #ID del sensor
            "db_id":"11C-LabSN:s31_16", #ESPOL:db_id Literal("s31_16")
            "point": [
                {"id": "s31_16_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_16_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_16_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_16_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_16_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_16_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        }
    },
    "ZonaBreakers": {
        "s31_12_Proyector":{ #ID del sensor
            "db_id":"11C-LabSN:s31_12", #ESPOL:db_id Literal("s31_12")
            "point": [
                {"id": "s31_12_Proyector_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_12_Proyector_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_12_Proyector_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_12_Proyector_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_12_Proyector_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_12_Proyector_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        },
        "s31_15":{ #ID del sensor
            "db_id":"11C-LabSN:s31_15", #ESPOL:db_id Literal("s31_12")
            "point": [
                {"id": "s31_15_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_15_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_15_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_15_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_15_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_15_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        }
    },
    "ZonaAire": {
        "s31_17":{ #ID del sensor
            "db_id":"11C-LabSN:s31_17", #ESPOL:db_id Literal("s31_17")
            "point": [
                {"id": "s31_17_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_17_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_17_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_17_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_17_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_17_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        },
        "s31_18":{ #ID del sensor
            "db_id":"11C-LabSN:s31_18", #ESPOL:db_id Literal("s31_18")
            "point": [
                {"id": "s31_18_ActivePower",   "class": "Active_Power_Sensor",   "unit": "W", "type":"power"},
                {"id": "s31_18_ApparentPower", "class": "Power_Sensor",          "unit": "VA", "type":"apparentpower"},
                {"id": "s31_18_ReactivePower", "class": "Reactive_Power_Sensor", "unit": "VAR", "type":"reactivepower"},
                {"id": "s31_18_Factor",        "class": "Power_Factor_Sensor",   "unit": None, "type":"factor"},
                {"id": "s31_18_Voltage",       "class": "Voltage_Sensor",        "unit": "V", "type":"voltage"},
                {"id": "s31_18_Current",       "class": "Current_Sensor",        "unit": "A", "type":"current"},
            ]
        }
    },
}

# Nodo 12: Zonas del laboratorio Redes de datos
zonas_sensores_RedesDatos={
    "ZonaGrupo1":{
        "S1RD":{ #ID del sensor
            "db_id":"11C-LabRDD:airClimate1", #ESPOL:db_id Literal("airClimate1")
            "point": [
                {"id": "S1RD_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S1RD_Humedad",     "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        }
    },
    "ZonaGrupo_2_4":{
        "S2RD":{ #ID del sensor
            "db_id":"11C-LabRDD:airClimate2", #ESPOL:db_id Literal("airClimate2")
            "point": [
                {"id": "S2RD_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S2RD_Humedad",     "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        },
        "S4RD":{ #ID del sensor
            "db_id":"11C-LabRDD:airClimate4", #ESPOL:db_id Literal("airClimate4")
            "point": [
                {"id": "S4RD_Temperatura", "class": "Temperature_Sensor", "unit": "DEG_C", "type":"temp"},
                {"id": "S4RD_Humedad", "class": "Humidity_Sensor",    "unit": "PERCENT_RH", "type":"humidity"}
            ]
        }
    }
}

# Crear zonas y sensores

# Función para crear zonas y sensores del laboratorio LabIoT
def crear_zonas_sensores_LabIoT():
    for zona, sensores in zonas_sensores_LabIoT.items():
        # 1) Crear la zona
        g.add((ESPOL[zona], A, REC["Zone"]))
        # 2) Enlazar la zona al espacio correcto
        target = "11C-Piso1" if zona in ["JardinFrontal", "JardinTrasero"] else "LabIoT"
        g.add((ESPOL[target], REC.hasPart, ESPOL[zona]))
        g.add((ESPOL[zona], REC.isPartOf, ESPOL[target]))

        # 3) Recorrer cada sensor (ahora meta es un dict con db_id y points)
        for sensor_padre, meta in sensores.items():
            sensor_uri = ESPOL[sensor_padre]
            # 3a) Tipo Sensor y db_id
            g.add((sensor_uri, A, BRICK.Equipment))
            g.add((sensor_uri, ESPOL.db_id, Literal(meta["db_id"])))
            g.add((sensor_uri, BRICK.hasLocation, ESPOL[zona]))

            # 3b) Recorrer cada punto y asignar tipo y unidad
            for punto in meta["point"]:
                punto_uri = ESPOL[punto["id"]]
                # tipo de punto (p.ej. Active_Power_Sensor)
                g.add((punto_uri, A, getattr(BRICK, punto["class"])))
                # relación sensor → punto
                g.add((sensor_uri, BRICK.hasPoint, punto_uri))
                g.add((punto_uri, BRICK.isPointOf, sensor_uri))
                g.add((punto_uri, ESPOL.point_type, Literal(punto["type"])))
                # unidad de medida, si existe
                if punto["unit"]:
                    g.add((punto_uri, BRICK.hasUnit, getattr(UNIT, punto["unit"])))

# Función para crear zonas y sensores del laboratorio de sistemas en la Nube
def crear_zonas_sensores_LabSistemasNube():
    for zona, sensores in zonas_Sensores_LabSitemasNube.items():
        # 1) Crear la zona
        g.add((ESPOL[zona], A, REC["Zone"]))
        # 2) Enlazar la zona al laboratorio Sistemas en la Nube
        g.add((ESPOL["LabSistemasEnLaNube"], REC.hasPart, ESPOL[zona]))
        g.add((ESPOL[zona], REC.isPartOf, ESPOL["LabSistemasEnLaNube"]))

        # 3) Recorrer cada sensor (ahora meta es un dict con db_id y point)
        for sensor_padre, meta in sensores.items():
            sensor_uri = ESPOL[sensor_padre]
            # 3a) Tipo de equipo y db_id
            g.add((sensor_uri, A, BRICK.Equipment))
            g.add((sensor_uri, ESPOL.db_id, Literal(meta["db_id"])))
            g.add((sensor_uri, BRICK.hasLocation, ESPOL[zona]))

            # 3b) Recorrer cada punto y asignar tipo y unidad
            for punto in meta["point"]:
                punto_uri = ESPOL[punto["id"]]
                # tipo de punto (p.ej. Active_Power_Sensor)
                g.add((punto_uri, A, getattr(BRICK, punto["class"])))
                # relación sensor → punto
                g.add((sensor_uri, BRICK.hasPoint, punto_uri))
                g.add((punto_uri, BRICK.isPointOf, sensor_uri))
                g.add((punto_uri, ESPOL.point_type, Literal(punto["type"])))
                # unidad de medida, si existe
                if punto["unit"]:
                    g.add((punto_uri, BRICK.hasUnit, getattr(UNIT, punto["unit"])))

# Función para crear zonas y sensores del laboratorio de sistemas en la Nube
def crear_zonas_sensores_LabRedesDatos():
    for zona, sensores in zonas_sensores_RedesDatos.items():
        # 1) Crear la zona
        g.add((ESPOL[zona], A, REC.Zone))
        # 2) Enlazar la zona al laboratorio Redes de Datos
        g.add((ESPOL["LabRedesDeDatos"], REC.hasPart, ESPOL[zona]))
        g.add((ESPOL[zona], REC.isPartOf, ESPOL["LabRedesDeDatos"]))

        # 3) Recorrer cada sensor (meta tiene db_id y lista de puntos)
        for sensor_padre, meta in sensores.items():
            sensor_uri = ESPOL[sensor_padre]
            # 3a) Definir como Sensor y asignar db_id y ubicación
            g.add((sensor_uri, A, BRICK.Equipment))
            g.add((sensor_uri, ESPOL.db_id, Literal(meta["db_id"])))
            g.add((sensor_uri, BRICK.hasLocation, ESPOL[zona]))

            # 3b) Crear cada punto, tipo y unidad
            for punto in meta["point"]:
                punto_uri = ESPOL[punto["id"]]
                # tipo de punto (e.g. Temperature_Sensor)
                g.add((punto_uri, A, getattr(BRICK, punto["class"])))
                # relación sensor → punto
                g.add((sensor_uri, BRICK.hasPoint, punto_uri))
                g.add((punto_uri, BRICK.isPointOf, sensor_uri))
                g.add((punto_uri, ESPOL.point_type, Literal(punto["type"])))
                # unidad de medida (si está definida)
                if punto["unit"]:
                    g.add((punto_uri, BRICK.hasUnit, getattr(UNIT, punto["unit"])))


# Ejecutar creación\crear_zonas_y_sensores()
crear_zonas_sensores_LabIoT()
crear_zonas_sensores_LabSistemasNube()
crear_zonas_sensores_LabRedesDatos()

# Guardar TTL
g.serialize("./Ontology/brickESPOLschema.ttl", format="ttl")
print("Archivo guardado como 'brickESPOLschema.ttl'")