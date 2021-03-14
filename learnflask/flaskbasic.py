from flask import Flask, json, jsonify, request

app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify({"about": "Hello world"})


@app.route("/multi/<int:num>/<int:by>", methods=["GET"])
def get_multiply(num, by):
    return jsonify({"result": num * by})


@app.route("/replay", methods=["POST"])
def replay():
    return jsonify(request.get_json())


# export FLASK_APP=flaskblog.py
# export FLASK_ENV=development