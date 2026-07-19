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

PRODUCTS = [
    {"id": 1, "name": "Sauce Labs Backpack", "price": 29.99, "stock": 10},
    {"id": 2, "name": "Sauce Labs Bike Light", "price": 9.99, "stock": 5},
    {"id": 3, "name": "Sauce Labs Bolt T-Shirt", "price": 15.99, "stock": 20},
    {"id": 4, "name": "Sauce Labs Fleece Jacket", "price": 49.99, "stock": 3},
    {"id": 5, "name": "Sauce Labs Onesie", "price": 7.99, "stock": 0},
    {"id": 6, "name": "Test.allTheThings() T-Shirt", "price": 15.99, "stock": 50},
]

TOKENS = {}

CARTS = {}


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


def get_token_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    return TOKENS.get(token)


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
    TOKENS[token] = username
    return success({
        "token": token,
        "username": username,
    })


@app.get("/api/products")
def list_products():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "", type=str)

    if page < 1:
        return fail(2001, "page must be >= 1")
    if size < 1 or size > 100:
        return fail(2002, "size must be between 1 and 100")

    filtered = PRODUCTS
    if keyword:
        filtered = [p for p in filtered if keyword.lower() in p["name"].lower()]

    start = (page - 1) * size
    end = start + size
    page_items = filtered[start:end]

    return success({
        "list": page_items,
        "total": len(filtered),
        "page": page,
        "size": size,
    })


@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if product is None:
        return fail(3001, "product not found")
    return success(product)


@app.post("/api/cart")
def add_to_cart():
    user = get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")

    if not request.is_json:
        return fail(1005, "invalid content type")

    body = request.get_json(silent=True)
    if body is None:
        return fail(1006, "invalid json body")

    product_id = body.get("product_id")
    quantity = body.get("quantity", 1)

    if product_id is None:
        return fail(3002, "product_id is required")

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if product is None:
        return fail(3001, "product not found")

    if product["stock"] <= 0:
        return fail(3003, "product is out of stock")

    if quantity < 1:
        return fail(3004, "quantity must be >= 1")

    cart = CARTS.setdefault(user, [])
    existing = next((item for item in cart if item["product_id"] == product_id), None)
    if existing:
        existing["quantity"] += quantity
    else:
        cart.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
        })

    return success({"cart": cart})


@app.get("/api/cart")
def get_cart():
    user = get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")
    cart = CARTS.get(user, [])
    total_price = sum(item["price"] * item["quantity"] for item in cart)
    return success({
        "cart": cart,
        "total_price": round(total_price, 2),
    })


@app.delete("/api/cart/<int:product_id>")
def remove_from_cart(product_id):
    user = get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")

    cart = CARTS.get(user, [])
    new_cart = [item for item in cart if item["product_id"] != product_id]
    if len(new_cart) == len(cart):
        return fail(3005, "product not in cart")

    CARTS[user] = new_cart
    total_price = sum(item["price"] * item["quantity"] for item in new_cart)
    return success({
        "cart": new_cart,
        "total_price": round(total_price, 2),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)