import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import allure
import pytest
from common.request_util import RequestUtil

BASE_URL = "http://127.0.0.1:5000"


@allure.feature("商品模块")
class TestProduct:
    @allure.story("商品列表")
    @allure.title("正常查询商品列表")
    def test_list_products_default(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/products")
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]["list"]) == 6
        assert body["data"]["total"] == 6

    @allure.story("商品列表")
    @allure.title("分页查询 page=1 size=2")
    def test_list_products_with_pagination(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/products", params={"page": 1, "size": 2})
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]["list"]) == 2
        assert body["data"]["total"] == 6
        assert body["data"]["page"] == 1

    @allure.story("商品列表")
    @allure.title("关键词搜索商品")
    def test_list_products_with_keyword(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/products", params={"keyword": "Bike"})
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert "Bike" in body["data"]["list"][0]["name"]

    @allure.story("商品详情")
    @allure.title("查询存在的商品")
    def test_get_product_exists(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/products/1")
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["id"] == 1
        assert body["data"]["name"] == "Sauce Labs Backpack"

    @allure.story("商品详情")
    @allure.title("查询不存在的商品")
    def test_get_product_not_exists(self):
        api = RequestUtil(BASE_URL)
        resp = api.get("/api/products/999")
        body = resp.json()
        assert body["code"] == 3001
        assert body["data"] is None