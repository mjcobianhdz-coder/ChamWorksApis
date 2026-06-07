from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Conexión a MongoDB Atlas
chambitas = MongoClient(
    "mongodb+srv://chambitas_app:V1cto3N0Reprueb4s@empleos0.6zi2k1h.mongodb.net/?appName=Empleos0"
)

db = chambitas["Chambitas"]

# Colecciones
usuarios = db["usuarios"]
trabajos = db["trabajos"]

# ==========================================
# LOGIN USUARIO
# ==========================================
@app.route("/usuarios/login", methods=["POST"])
def login_usuario():
    datos = request.get_json()
    correo = datos.get("correo")
    password = datos.get("password")
    tipo = datos.get("tipo")

    usuario = usuarios.find_one({
        "correo": correo,
        "password": password
    })

    if usuario:
        if usuario["tipo"] == tipo:
            return jsonify({
                "mensaje": "inicia sesion",
                "tipo": usuario["tipo"],
                "usuario_id": str(usuario["_id"]),   # devolvemos el id
                "correo": usuario["correo"]
            }), 200
        else:
            return jsonify({"mensaje": "tipo incorrecto"}), 403
    else:
        return jsonify({"mensaje": "incorrecto"}), 401

# ==========================================
# REGISTRAR USUARIO
# ==========================================
@app.route("/usuarios", methods=["POST"])
def registrar_usuario():
    data = request.get_json()
    usuario = {
        "nombre": data["nombre"],
        "password": data["password"],
        "correo": data["correo"],
        "tipo": data["tipo"]
    }
    usuarios.insert_one(usuario)
    return jsonify({"message": "Usuario registrado correctamente"}), 201

# ==========================================
# PUBLICAR TRABAJO (con empleador_id)
# ==========================================
@app.route("/trabajos", methods=["POST"])
def publicar_trabajo():
    data = request.get_json()
    trabajo = {
        "nombre_trabajo": data["nombre_trabajo"],
        "descripcion": data["descripcion"],
        "turno": data["turno"],
        "categoria": data["categoria"],
        "empresa": data["empresa"],
        "fechas_disponibles": data.get("fechas_disponibles", []),
        "empleador_id": ObjectId(data["empleador_id"])   # nuevo campo
    }
    trabajos.insert_one(trabajo)
    return jsonify({"message": "Trabajo publicado correctamente"}), 201

# ==========================================
# MOSTRAR TODOS LOS TRABAJOS
# ==========================================
@app.route("/trabajos", methods=["GET"])
def obtener_trabajos():
    lista = []
    for trabajo in trabajos.find():
        lista.append({
            "id": str(trabajo["_id"]),
            "nombre_trabajo": trabajo["nombre_trabajo"],
            "descripcion": trabajo["descripcion"],
            "turno": trabajo["turno"],
            "categoria": trabajo["categoria"],
            "empresa": trabajo["empresa"],
            "fechas_disponibles": trabajo.get("fechas_disponibles", []),
            "empleador_id": str(trabajo.get("empleador_id", ""))  # <-- aquí el cambio
        })
    return jsonify(lista)


# ==========================================
# OBTENER TRABAJOS POR CATEGORIA
# ==========================================
@app.route("/trabajos/categoria/<categoria>", methods=["GET"])
def obtener_trabajos_por_categoria(categoria):
    lista = []
    resultados = trabajos.find({"categoria": {"$regex": f"^{categoria}$", "$options": "i"}})
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

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
