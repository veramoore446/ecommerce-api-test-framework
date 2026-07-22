"""
Ecommerce API Locust Performance Test
=======================================
This file defines multiple user behaviors for load testing an ecommerce API.

Target API: http://127.0.0.1:5000

User Behaviors:
- LoginBehavior:     Simulates user login (weight 1)
- BrowseBehavior:    Simulates product browsing (weight 3)
- CartBehavior:      Simulates cart operations (weight 2)
- CheckoutBehavior:  Simulates checkout flow (weight 1)
"""

import logging
import random

from locust import HttpUser, task, between

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────────
LOGIN_CREDENTIALS = {"username": "standard_user", "password": "secret_sauce"}
JSON_HEADERS = {"Content-Type": "application/json"}


# ── Login Helper ───────────────────────────────────────────────────────────────
def perform_login(client):
    """Send a login request and return the token on success, or None on failure."""
    try:
        with client.post(
            "/api/login",
            json=LOGIN_CREDENTIALS,
            headers=JSON_HEADERS,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    body = response.json()
                    token = body.get("token") or body.get("access_token")
                    if token:
                        logger.info("Login successful, token obtained.")
                        return token
                    logger.warning("Login succeeded but no token found in response.")
                    return None
                except ValueError:
                    logger.warning("Login response is not valid JSON.")
                    return None
            else:
                response.failure(f"Login failed with status {response.status_code}")
                return None
    except Exception as e:
        logger.error("Exception during login: %s", e)
        return None


# ── 1. LoginBehavior ────────────────────────────────────────────────────────────
class LoginBehavior(HttpUser):
    """
    Simulates a user logging in.

    Weight: 1 — this is the least frequent standalone action since most
    other behaviours already perform login as part of their on_start.
    """

    host = "http://127.0.0.1:5000"
    wait_time = between(1, 3)

    token = None

    @task(1)
    def login(self):
        """POST /api/login with username and password."""
        try:
            with self.client.post(
                "/api/login",
                json=LOGIN_CREDENTIALS,
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    try:
                        body = response.json()
                        token = body.get("token") or body.get("access_token")
                        if token:
                            self.token = token
                            self.client.headers["Authorization"] = f"Bearer {token}"
                            logger.info("LoginBehavior: login successful.")
                        else:
                            response.failure("No token in login response body.")
                    except ValueError:
                        response.failure("Login response is not valid JSON.")
                else:
                    response.failure(
                        f"Login failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("LoginBehavior.login exception: %s", e)


# ── 2. BrowseBehavior ────────────────────────────────────────────────────────────
class BrowseBehavior(HttpUser):
    """
    Simulates a logged-in user browsing the product catalog.

    Tasks:
    - browse_products  (weight 3): GET /api/products?page=1&size=10
    - view_product     (weight 2): GET /api/products/{random_id}
    - view_cart        (weight 1): GET /api/cart
    """

    host = "http://127.0.0.1:5000"
    wait_time = between(1, 3)

    token = None

    def on_start(self):
        """Log in before starting any browsing tasks."""
        token = perform_login(self.client)
        if token:
            self.token = token
            self.client.headers["Authorization"] = f"Bearer {token}"
        else:
            logger.warning(
                "BrowseBehavior: login failed in on_start, continuing without token."
            )

    @task(3)
    def browse_products(self):
        """GET /api/products?page=1&size=10 — list first page of products."""
        try:
            with self.client.get(
                "/api/products?page=1&size=10",
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    logger.info("BrowseBehavior: browsed product list successfully.")
                else:
                    response.failure(
                        f"Browse products failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("BrowseBehavior.browse_products exception: %s", e)

    @task(2)
    def view_product(self):
        """GET /api/products/{random_id} — view a random product's detail."""
        product_id = random.randint(1, 50)
        try:
            with self.client.get(
                f"/api/products/{product_id}",
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    logger.info(
                        "BrowseBehavior: viewed product %d successfully.", product_id
                    )
                elif response.status_code == 404:
                    logger.debug(
                        "BrowseBehavior: product %d not found (404).", product_id
                    )
                else:
                    response.failure(
                        f"View product failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("BrowseBehavior.view_product exception: %s", e)

    @task(1)
    def view_cart(self):
        """GET /api/cart — view the current shopping cart."""
        try:
            with self.client.get(
                "/api/cart",
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    logger.info("BrowseBehavior: viewed cart successfully.")
                else:
                    response.failure(
                        f"View cart failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("BrowseBehavior.view_cart exception: %s", e)


# ── 3. CartBehavior ─────────────────────────────────────────────────────────────
class CartBehavior(HttpUser):
    """
    Simulates a logged-in user performing cart operations.

    Tasks:
    - add_to_cart    (weight 2): POST   /api/cart  {product_id, quantity}
    - view_cart      (weight 1): GET    /api/cart
    - remove_from_cart(weight 1): DELETE /api/cart/1
    """

    host = "http://127.0.0.1:5000"
    wait_time = between(1, 3)

    token = None
    _cart_has_item = False

    def on_start(self):
        """Log in before starting any cart tasks."""
        token = perform_login(self.client)
        if token:
            self.token = token
            self.client.headers["Authorization"] = f"Bearer {token}"
        else:
            logger.warning(
                "CartBehavior: login failed in on_start, continuing without token."
            )
        self._cart_has_item = False

    @task(2)
    def add_to_cart(self):
        """POST /api/cart — add product_id=1, quantity=1 to the cart."""
        try:
            with self.client.post(
                "/api/cart",
                json={"product_id": 1, "quantity": 1},
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code in (200, 201):
                    self._cart_has_item = True
                    logger.info("CartBehavior: added item to cart successfully.")
                else:
                    response.failure(
                        f"Add to cart failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("CartBehavior.add_to_cart exception: %s", e)

    @task(1)
    def view_cart(self):
        """GET /api/cart — view the current shopping cart."""
        try:
            with self.client.get(
                "/api/cart",
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    logger.info("CartBehavior: viewed cart successfully.")
                else:
                    response.failure(
                        f"View cart failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("CartBehavior.view_cart exception: %s", e)

    @task(1)
    def remove_from_cart(self):
        """DELETE /api/cart/1 — remove item 1 from the cart."""
        try:
            with self.client.delete(
                "/api/cart/1",
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code in (200, 204):
                    logger.info("CartBehavior: removed item from cart successfully.")
                    # Clear cart state after remove completes the add+remove cycle
                    self._cart_has_item = False
                else:
                    response.failure(
                        f"Remove from cart failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("CartBehavior.remove_from_cart exception: %s", e)


# ── 4. CheckoutBehavior ─────────────────────────────────────────────────────────
class CheckoutBehavior(HttpUser):
    """
    Simulates a logged-in user going through the checkout flow.

    Tasks:
    - add_to_cart (in on_start): ensures items exist in the cart
    - create_order (weight 1):  POST /api/orders
    - view_orders (weight 1):    GET  /api/orders
    """

    host = "http://127.0.0.1:5000"
    wait_time = between(1, 3)

    token = None

    def on_start(self):
        """Log in and add products to cart before placing orders."""
        token = perform_login(self.client)
        if token:
            self.token = token
            self.client.headers["Authorization"] = f"Bearer {token}"
        else:
            logger.warning(
                "CheckoutBehavior: login failed in on_start, continuing without token."
            )

        # Pre-populate the cart so that order creation has items to process
        try:
            self.client.post(
                "/api/cart",
                json={"product_id": 1, "quantity": 1},
                headers=JSON_HEADERS,
            )
            logger.info("CheckoutBehavior: pre-added item to cart in on_start.")
        except Exception as e:
            logger.error("CheckoutBehavior.on_start cart pre-add exception: %s", e)

    @task(1)
    def create_order(self):
        """POST /api/orders — submit a new order."""
        try:
            with self.client.post(
                "/api/orders",
                json={},
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code in (200, 201):
                    logger.info("CheckoutBehavior: order created successfully.")
                else:
                    response.failure(
                        f"Create order failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("CheckoutBehavior.create_order exception: %s", e)

    @task(1)
    def view_orders(self):
        """GET /api/orders — list the user's orders."""
        try:
            with self.client.get(
                "/api/orders",
                headers=JSON_HEADERS,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    logger.info("CheckoutBehavior: viewed order list successfully.")
                else:
                    response.failure(
                        f"View orders failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error("CheckoutBehavior.view_orders exception: %s", e)


# ── 5. WebsiteUser ───────────────────────────────────────────────────────────────
class WebsiteUser(HttpUser):
    """
    Aggregated user that randomly picks one of the defined behaviours based
    on their relative weights, simulating a realistic traffic distribution
    across the ecommerce API.

    Task weights:
    - BrowseBehavior:    3  (most users are browsing)
    - CartBehavior:     2  (moderate cart activity)
    - CheckoutBehavior: 1  (fewer checkouts)
    - LoginBehavior:    1  (standalone login attempts)
    """

    host = "http://127.0.0.1:5000"
    wait_time = between(1, 3)

    tasks = {
        BrowseBehavior: 3,
        CartBehavior: 2,
        CheckoutBehavior: 1,
        LoginBehavior: 1,
    }
