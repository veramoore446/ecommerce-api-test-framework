import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import allure
import pytest
from common.request_util import RequestUtil

BASE_URL = "http://127.0.0.1:5000"
CART_USER = "cart_test_user"
CART_PASS = "secret_sauce"


def get_logged_in_api():
    api = RequestUtil(BASE_URL)
    api.login(CART_USER, CART_PASS)
    return api


@allure.feature("购物车模块")
class TestCartAuth:
    @allure.story("鉴权")
    @allure.title("未登录查看购物车应被拒绝")
    def test_get_cart_without_token(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/cart")
        body = resp.json()
        assert body["code"] == 4001
        assert body["data"] is None

    @allure.story("鉴权")
    @allure.title("未登录加入购物车应被拒绝")
    def test_add_cart_without_token(self):
        api = RequestUtil(BASE_URL)
        resp = api.post("/api/cart", json={"product_id": 1, "quantity": 1})
        body = resp.json()
        assert body["code"] == 4001

    @allure.story("鉴权")
    @allure.title("错误 token 查看购物车应被拒绝")
    def test_get_cart_with_wrong_token(self):
        api = RequestUtil(BASE_URL)
        api.token = "wrong-token"
        resp = api.get("/api/cart")
        body = resp.json()
        assert body["code"] == 4001


@allure.feature("购物车模块")
class TestCart:
    @allure.story("加入购物车")
    @allure.title("登录后加入商品到购物车")
    def test_add_to_cart_success(self):
        api = get_logged_in_api()
        resp = api.post("/api/cart", json={"product_id": 1, "quantity": 2})
        body = resp.json()
        assert body["code"] == 0
        cart = body["data"]["cart"]
        item = next((i for i in cart if i["product_id"] == 1), None)
        assert item is not None
        assert item["quantity"] == 2

    @allure.story("加入购物车")
    @allure.title("加入不存在的商品应失败")
    def test_add_nonexistent_product(self):
        api = get_logged_in_api()
        resp = api.post("/api/cart", json={"product_id": 999, "quantity": 1})
        body = resp.json()
        assert body["code"] == 3001

    @allure.story("加入购物车")
    @allure.title("加入库存为 0 的商品应失败")
    def test_add_out_of_stock_product(self):
        api = get_logged_in_api()
        resp = api.post("/api/cart", json={"product_id": 5, "quantity": 1})
        body = resp.json()
        assert body["code"] == 3003

    @allure.story("查看购物车")
    @allure.title("查看购物车应返回已添加商品")
    def test_get_cart(self):
        api = get_logged_in_api()
        resp = api.get("/api/cart")
        body = resp.json()
        assert body["code"] == 0
        assert "cart" in body["data"]
        assert "total_price" in body["data"]
        assert isinstance(body["data"]["total_price"], (int, float))

    @allure.story("删除购物车商品")
    @allure.title("删除购物车中的商品")
    def test_remove_from_cart(self):
        api = get_logged_in_api()
        api.post("/api/cart", json={"product_id": 2, "quantity": 1})
        resp = api.delete("/api/cart/2")
        body = resp.json()
        assert body["code"] == 0
        item_ids = [i["product_id"] for i in body["data"]["cart"]]
        assert 2 not in item_ids