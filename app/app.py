from flask import Flask, jsonify, request
from models import (
    init_db,
    get_user,
    save_token,
    get_token_user,
    delete_token,
    list_products,
    get_product,
    get_cart,
    add_to_cart,
    remove_from_cart,
    clear_cart,
    create_order,
    add_order_item,
    get_order,
    list_orders,
)

app = Flask(__name__)
init_db()


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


def _get_token_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    return get_token_user(token)


@app.get("/api/health")
def health_check():
    return success({
        "status": "running",
        "service": "ecommerce-api-test-framework",
        "db": "sqlite",
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

    user = get_user(username)
    if user is None or user["password"] != password:
        return fail(1001, "username or password error")
    if user["locked"]:
        return fail(1004, "user is locked")

    token = f"mock-token-{username}"
    save_token(token, username)
    return success({
        "token": token,
        "username": username,
    })


@app.get("/api/products")
def list_products_api():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword", "", type=str)

    if page < 1:
        return fail(2001, "page must be >= 1")
    if size < 1 or size > 100:
        return fail(2002, "size must be between 1 and 100")

    filtered = list_products()
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
def get_product_api(product_id):
    product = get_product(product_id)
    if product is None:
        return fail(3001, "product not found")
    return success(product)


@app.post("/api/cart")
def add_to_cart_api():
    user = _get_token_user()
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

    product = get_product(product_id)
    if product is None:
        return fail(3001, "product not found")

    if product["stock"] <= 0:
        return fail(3003, "product is out of stock")

    if quantity < 1:
        return fail(3004, "quantity must be >= 1")

    add_to_cart(user, product_id, product["name"], product["price"], quantity)
    return success({"cart": get_cart(user)})


@app.get("/api/cart")
def get_cart_api():
    user = _get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")
    cart = get_cart(user)
    total_price = round(sum(item["price"] * item["quantity"] for item in cart), 2)
    return success({
        "cart": cart,
        "total_price": total_price,
    })


@app.delete("/api/cart/<int:product_id>")
def remove_from_cart_api(product_id):
    user = _get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")

    if not remove_from_cart(user, product_id):
        return fail(3005, "product not in cart")

    cart = get_cart(user)
    total_price = round(sum(item["price"] * item["quantity"] for item in cart), 2)
    return success({
        "cart": cart,
        "total_price": total_price,
    })


@app.post("/api/orders")
def create_order_api():
    user = _get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")

    cart = get_cart(user)
    if not cart:
        return fail(5001, "cart is empty")

    total_price = round(sum(item["price"] * item["quantity"] for item in cart), 2)
    order_id = create_order(user, total_price)

    for item in cart:
        add_order_item(
            order_id,
            item["product_id"],
            item["name"],
            item["price"],
            item["quantity"],
        )

    clear_cart(user)

    return success({
        "order_id": order_id,
        "username": user,
        "items": cart,
        "total_price": total_price,
        "status": "created",
    })


@app.get("/api/orders")
def list_orders_api():
    user = _get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")
    orders = list_orders(user)
    return success({"orders": orders, "total": len(orders)})


@app.get("/api/orders/<int:order_id>")
def get_order_api(order_id):
    user = _get_token_user()
    if not user:
        return fail(4001, "unauthorized: token is missing or invalid")
    order = get_order(order_id, user)
    if order is None:
        return fail(5002, "order not found")
    return success(order)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
