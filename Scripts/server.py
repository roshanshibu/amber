from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/dummyAuth", methods=["GET"])
def dummyAuth():
    if request.method == "GET":
        username = request.args.get("username")
        password = request.args.get("password")
        if not username or not password:
            return "Missing username or password", 400
        if username == "testAdmin" and password == "testPassword":
            return "Authenticated", 200
        else:
            return "Unauthorized: Invalid username or password", 401


if __name__ == "__main__":
    app.run(debug=True)
