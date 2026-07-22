import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            locked INTEGER DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            UNIQUE(username, product_id)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'created',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL
        )
        """
    )

    _seed_data(c)
    conn.commit()
    conn.close()


def _seed_data(c):
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ("standard_user", "secret_sauce", 0),
            ("locked_out_user", "secret_sauce", 1),
            ("order_test_user", "secret_sauce", 0),
            ("cart_test_user", "secret_sauce", 0),
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?)", users)

    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
            (1, "Sauce Labs Backpack", 29.99, 10),
            (2, "Sauce Labs Bike Light", 9.99, 5),
            (3, "Sauce Labs Bolt T-Shirt", 15.99, 20),
            (4, "Sauce Labs Fleece Jacket", 49.99, 3),
            (5, "Sauce Labs Onesie", 7.99, 0),
            (6, "Test.allTheThings() T-Shirt", 15.99, 50),
        ]
        c.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)


def get_user(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "username": row["username"],
            "password": row["password"],
            "locked": bool(row["locked"]),
        }
    return None


def save_token(token, username):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tokens VALUES (?, ?)", (token, username))
    conn.commit()
    conn.close()


def get_token_user(token):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username FROM tokens WHERE token = ?", (token,))
    row = c.fetchone()
    conn.close()
    return row["username"] if row else None


def delete_token(token):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def list_products():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r["id"], "name": r["name"], "price": r["price"], "stock": r["stock"]}
        for r in rows
    ]


def get_product(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "name": row["name"],
            "price": row["price"],
            "stock": row["stock"],
        }
    return None


def get_cart(username):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT product_id, name, price, quantity FROM carts WHERE username = ?",
        (username,),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"product_id": r["product_id"], "name": r["name"], "price": r["price"], "quantity": r["quantity"]}
        for r in rows
    ]


def add_to_cart(username, product_id, name, price, quantity):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT quantity FROM carts WHERE username = ? AND product_id = ?",
        (username, product_id),
    )
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE carts SET quantity = quantity + ? WHERE username = ? AND product_id = ?",
            (quantity, username, product_id),
        )
    else:
        c.execute(
            "INSERT INTO carts (username, product_id, name, price, quantity) VALUES (?, ?, ?, ?, ?)",
            (username, product_id, name, price, quantity),
        )
    conn.commit()
    conn.close()


def remove_from_cart(username, product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "DELETE FROM carts WHERE username = ? AND product_id = ?",
        (username, product_id),
    )
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


def clear_cart(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM carts WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def create_order(username, total_price):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (username, total_price, status) VALUES (?, ?, 'created')",
        (username, total_price),
    )
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id


def add_order_item(order_id, product_id, name, price, quantity):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO order_items (order_id, product_id, name, price, quantity) VALUES (?, ?, ?, ?, ?)",
        (order_id, product_id, name, price, quantity),
    )
    conn.commit()
    conn.close()


def get_order(order_id, username):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM orders WHERE order_id = ? AND username = ?",
        (order_id, username),
    )
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    order = {
        "order_id": row["order_id"],
        "username": row["username"],
        "total_price": row["total_price"],
        "status": row["status"],
        "created_at": row["created_at"],
        "items": [],
    }
    c.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    items = c.fetchall()
    conn.close()
    order["items"] = [
        {
            "product_id": i["product_id"],
            "name": i["name"],
            "price": i["price"],
            "quantity": i["quantity"],
        }
        for i in items
    ]
    return order


def list_orders(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE username = ? ORDER BY order_id DESC", (username,))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "order_id": r["order_id"],
            "username": r["username"],
            "total_price": r["total_price"],
            "status": r["status"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
