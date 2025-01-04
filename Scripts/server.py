from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/dummyAuth", methods=["GET"])
def dummyAuth():
    if request.method == "GET":
        session_token = request.headers.get("Authorization")
        if not session_token:
            return "Missing token", 400
        if session_token == "TEST_TOKEN_1235":
            return "Authenticated", 200
        else:
            return "Unauthorized: Invalid token", 401


if __name__ == "__main__":
    app.run(debug=True)
