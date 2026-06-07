from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)

# Conexión a MongoDB Atlas
chambitas = MongoClient(
    "mongodb+srv://chambitas_app:V1cto3N0Reprueb4s@empleos0.6zi2k1h.mongodb.net/?appName=Empleos0"
)

db = chambitas["Chambitas"]

# Colecciones
usuarios = db["usuarios"]
trabajos = db["trabajos"]
citas = db["citas"]



# CREAR CITA
# El usuario manda: descripcion, correo, usuario_id, trabajo_id, fecha_disponible
# Se liga automáticamente: empleador_id desde el documento de trabajo

@app.route("/citas", methods=["POST"])
def crear_cita():
    data = request.get_json()

    # Campos que ingresa el usuario
    if not data or "descripcion" not in data or "correo" not in data or \
       "usuario_id" not in data or "trabajo_id" not in data or "fecha_disponible" not in data:
        return jsonify({"message": "Faltan campos requeridos"}), 400

    # Convertir IDs a ObjectId
    try:
        usuario_id = ObjectId(data["usuario_id"])
        trabajo_id = ObjectId(data["trabajo_id"])
    except InvalidId:
        return jsonify({"message": "ID inválido"}), 400

    descripcion     = data["descripcion"]
    correo          = data["correo"]
    fecha_disponible = data["fecha_disponible"]

    # Verificar que el trabajo exista
    trabajo = trabajos.find_one({"_id": trabajo_id})
    if not trabajo:
        return jsonify({"message": "Trabajo no encontrado"}), 404

    # Verificar que la fecha esté disponible en el trabajo
    if fecha_disponible not in trabajo.get("fechas_disponibles", []):
        return jsonify({"message": "Horario no disponible"}), 400

    # Ligar empleador_id automáticamente desde el documento de trabajo
    empleador_id = trabajo.get("empleador_id")

    # Crear documento de cita
    nueva_cita = {
        "descripcion":      descripcion,
        "correo":           correo,
        "usuario_id":       usuario_id,
        "trabajo_id":       trabajo_id,
        "fecha_disponible": fecha_disponible,
        "empleador_id":     empleador_id       # ligado automáticamente
    }

    resultado = citas.insert_one(nueva_cita)

    # Eliminar la fecha usada del array de fechas_disponibles en el trabajo
    trabajos.update_one(
        {"_id": trabajo_id},
        {"$pull": {"fechas_disponibles": fecha_disponible}}
    )

    return jsonify({
        "message": "Cita creada correctamente",
        "id_cita": str(resultado.inserted_id)
    }), 201



# OBTENER CITAS POR ID_USUARIO

@app.route("/citas/usuario/<id_usuario>", methods=["GET"])
def obtener_citas_por_usuario(id_usuario):

    try:
        usuario_oid = ObjectId(id_usuario)
    except InvalidId:
        return jsonify({"message": "ID de usuario inválido"}), 400

    lista_citas = []

    for cita in citas.find({"usuario_id": usuario_oid}):
        lista_citas.append({
            "id":               str(cita["_id"]),
            "descripcion":      cita["descripcion"],
            "correo":           cita["correo"],
            "usuario_id":       str(cita["usuario_id"]),
            "trabajo_id":       str(cita["trabajo_id"]),
            "fecha_disponible": cita["fecha_disponible"],
            "empleador_id":     str(cita["empleador_id"])
        })

    return jsonify(lista_citas)



# OBTENER CITAS POR ID_EMPLEADOR

@app.route("/citas/empleador/<id_empleador>", methods=["GET"])
def obtener_citas_por_empleador(id_empleador):

    try:
        empleador_oid = ObjectId(id_empleador)
    except InvalidId:
        return jsonify({"message": "ID de empleador inválido"}), 400

    lista_citas = []

    for cita in citas.find({"empleador_id": empleador_oid}):
        lista_citas.append({
            "id":               str(cita["_id"]),
            "descripcion":      cita["descripcion"],
            "correo":           cita["correo"],
            "usuario_id":       str(cita["usuario_id"]),
            "trabajo_id":       str(cita["trabajo_id"]),
            "fecha_disponible": cita["fecha_disponible"],
            "empleador_id":     str(cita["empleador_id"])
        })

    return jsonify(lista_citas)



# MAIN

print(app.url_map)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009, debug=True, use_reloader=False)
