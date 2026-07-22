import pytest
from app.models import clear_cart, get_db
import os

TEST_USERS = ["cart_test_user", "order_test_user"]


@pytest.fixture(autouse=True)
def clean_test_data():
    for user in TEST_USERS:
        clear_cart(user)
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE username IN (?, ?)", TEST_USERS)
    c.execute("DELETE FROM tokens")
    conn.commit()
    conn.close()
    yield
    for user in TEST_USERS:
        clear_cart(user)