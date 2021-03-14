from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class Hello(Resource):
    def get(self):
        return {"about": "Hello World"}


class Multi(Resource):
    def get(self, num, by):
        return {"result": num * by}


class Replay(Resource):
    def post(self):
        return request.get_json()


api.add_resource(Hello, "/")
api.add_resource(Multi, "/multi/<int:num>/<int:by>")
api.add_resource(Replay, "/replay")

if __name__ == "__main__":
    app.run(debug=True)