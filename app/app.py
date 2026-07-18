from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = {
    "standard_user": {
        "password": "secret_sauce",
        "locked": False,
    },
    "locked_out_user": {
        "password": "secret_sauce",
        "locked": True,
    },
}


def success(data=None):
    return jsonify({
        "code": 0,
        "message": "success",
        "data": data or {},
    }), 200


def fail(code, message):
    return jsonify({
        "code": code,
        "message": message,
        "data": None,
    }), 200


@app.get("/api/health")
def health_check():
    return success({
        "status": "running",
        "service": "ecommerce-api-test-framework",
    })


@app.post("/api/login")
def login():
    if not request.is_json:
        return fail(1005, "invalid content type")

    body = request.get_json(silent=True)
    if body is None:
        return fail(1006, "invalid json body")

    username = body.get("username")
    password = body.get("password")

    if not username:
        return fail(1002, "username is required")

    if not password:
        return fail(1003, "password is required")

    user = USERS.get(username)
    if user is None or user["password"] != password:
        return fail(1001, "username or password error")

    if user["locked"]:
        return fail(1004, "user is locked")

    token = f"mock-token-{username}"
    return success({
        "token": token,
        "username": username,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
