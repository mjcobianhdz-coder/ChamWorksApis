from flask import Flask, jsonify
from pymongo import MongoClient
#from bson.objectid import ObjectId

app = Flask(__name__)
chambitas = MongoClient("mongodb+srv://chambitas_app:V1cto3N0Reprueb4s@empleos0.6zi2k1h.mongodb.net/?appName=Empleos0")

db = chambitas["Chambitas"]
coleccion = db["trabajos"]
#coleccion2 = db["usuarios"]


# OBTENER TRABAJOS CON FECHAS DISPONIBLES

@app.route("/trabajos/disponibles", methods=["GET"])
def obtener_trabajos_disponibles():
    lista = []
    resultados = coleccion.find({"fechas_disponibles": {"$exists": True, "$not": {"$size": 0}}})
# Filtra trabajos donde el array fechas_disponibles no esté vacío ($ne = not equal)

    for trabajo in resultados:
        lista.append({
            "id": str(trabajo["_id"]),
            "nombre_trabajo": trabajo["nombre_trabajo"],
            "descripcion": trabajo["descripcion"],
            "turno": trabajo["turno"],
            "categoria": trabajo["categoria"],
            "empresa": trabajo["empresa"],
            "fechas_disponibles": trabajo.get("fechas_disponibles", []),
            "empleador_id": str(trabajo.get("empleador_id", ""))
        })
    return jsonify(lista)

app.run(
    host="0.0.0.0",
    port=5009,
    debug=True
)