import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import allure
import pytest
from common.request_util import RequestUtil

BASE_URL = "http://127.0.0.1:5000"
ORDER_USER = "order_test_user"
ORDER_PASS = "secret_sauce"


def setup_cart(api):
    api.post("/api/cart", json={"product_id": 1, "quantity": 2})
    api.post("/api/cart", json={"product_id": 2, "quantity": 1})


@allure.feature("订单模块")
class TestOrderAuth:
    @allure.story("鉴权")
    @allure.title("未登录提交订单应被拒绝")
    def test_create_order_without_token(self):
        api = RequestUtil(BASE_URL)
        resp = api.post("/api/orders")
        body = resp.json()
        assert body["code"] == 4001

    @allure.story("鉴权")
    @allure.title("未登录查询订单列表应被拒绝")
    def test_list_orders_without_token(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/orders")
        body = resp.json()
        assert body["code"] == 4001


@allure.feature("订单模块")
class TestOrder:
    @allure.story("创建订单")
    @allure.title("购物车有商品时提交订单成功")
    def test_create_order_success(self):
        api = RequestUtil(BASE_URL)
        api.login(ORDER_USER, ORDER_PASS)
        setup_cart(api)
        resp = api.post("/api/orders")
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["order_id"] > 0
        assert body["data"]["status"] == "created"
        assert body["data"]["total_price"] == 69.97
        assert len(body["data"]["items"]) == 2

    @allure.story("创建订单")
    @allure.title("购物车为空时提交订单应失败")
    def test_create_order_empty_cart(self):
        api = RequestUtil(BASE_URL)
        api.login(ORDER_USER, ORDER_PASS)
        resp = api.post("/api/orders")
        body = resp.json()
        assert body["code"] == 5001
        assert body["data"] is None

    @allure.story("查询订单列表")
    @allure.title("查询订单列表应返回已创建的订单")
    def test_list_orders(self):
        api = RequestUtil(BASE_URL)
        api.login(ORDER_USER, ORDER_PASS)
        setup_cart(api)
        api.post("/api/orders")
        resp = api.get("/api/orders")
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] >= 1
        assert len(body["data"]["orders"]) >= 1

    @allure.story("查询订单详情")
    @allure.title("查询存在的订单应返回订单信息")
    def test_get_order_exists(self):
        api = RequestUtil(BASE_URL)
        api.login(ORDER_USER, ORDER_PASS)
        setup_cart(api)
        create_resp = api.post("/api/orders")
        order_id = create_resp.json()["data"]["order_id"]
        resp = api.get(f"/api/orders/{order_id}")
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["order_id"] == order_id

    @allure.story("查询订单详情")
    @allure.title("查询不存在的订单应失败")
    def test_get_order_not_exists(self):
        api = RequestUtil(BASE_URL)
        api.login(ORDER_USER, ORDER_PASS)
        resp = api.get("/api/orders/99999")
        body = resp.json()
        assert body["code"] == 5002