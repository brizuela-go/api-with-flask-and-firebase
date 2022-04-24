import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
from flask import Flask, abort, jsonify, request

app = Flask(__name__)

# Configuraciones para firebase
cred = credentials.Certificate("back_end_firebase\serviceAccountKey.json")
fire = firebase_admin.initialize_app(cred)

# Conexión a firestore DB
db = firestore.client()

# Crear referencia a la colección
tasks_ref = db.collection("tasks")


@app.route("/")
def hello_world():
    return "Hello, World!"


uri = "/api/tasks/"


@app.route(uri, methods=["GET"])
def get_tasks():
    docs = tasks_ref.get()
    return jsonify({"tasks": task.to_dict() for task in docs})


@app.route(uri + "<string:id>", methods=["GET"])
def get_task(id):
    task = tasks_ref.document(id).get()
    return (
        jsonify({"task": task.to_dict()})
        if task
        else jsonify({"status": "ID Inexistente"})
    )


@app.route(uri, methods=["POST"])
def create_task():
    if not request.json:
        abort(404)
    new_task = {
        "name": request.json["name"],
        "check": False,
        "date": datetime.datetime.now(),
    }
    tasks_ref.document().set(new_task)
    docs = tasks_ref.stream()
    return jsonify({"tasks": task.to_dict() for task in docs}), 201


@app.route(uri + "<string:task_id>", methods=["PUT"])
def update_task(task_id):
    this_task = tasks_ref.document(task_id)

    if not this_task:
        abort(404)

    if "name" in request.json and type(request.json.get("name")) is not str:
        abort(400)

    if "check" in request.json and type(request.json.get("check")) is not bool:
        abort(400)

    this_task.update(
        {
            "name": request.json.get("name", this_task),
            "check": request.json.get("check", this_task),
            "modificado": datetime.datetime.now(),
        }
    )

    return jsonify({"task": this_task.get().to_dict()}), 201


@app.route(uri + "<string:task_id>", methods=["DELETE"])
def delete_task(task_id):
    res = tasks_ref.document(task_id)

    if not res:
        abort(404)

    res.delete()
    return jsonify({"result": True})


if __name__ == "__main__":
    app.run(debug=True)
