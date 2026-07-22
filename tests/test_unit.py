"""
单元测试 - Flask 应用层测试
使用 pytest + unittest.mock 模拟数据库层, 仅测试 Flask 路由逻辑
"""

import sys
import os
import pytest
import allure
from unittest.mock import patch

# 将项目根目录和 app 目录加入 sys.path, 以便 models 模块可以被正确导入
_project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _project_root)
sys.path.insert(0, os.path.join(_project_root, "app"))

# 在导入 app.app 之前 mock init_db, 避免真正连接数据库
with patch("models.init_db"):
    from app.app import app


@allure.feature("单元测试")
@allure.story("健康检查")
class TestHealthCheck:

    @allure.title("健康检查返回运行状态")
    def test_health_returns_running_status(self):
        with app.test_client() as client:
            resp = client.get("/api/health")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["code"] == 0
            assert data["data"]["status"] == "running"


@allure.feature("单元测试")
@allure.story("登录接口")
class TestLoginUnit:

    @allure.title("登录成功")
    @patch("app.app.save_token")
    @patch("app.app.get_user")
    def test_login_success(self, mock_get_user, mock_save_token):
        mock_get_user.return_value = {
            "username": "testuser",
            "password": "secret_sauce",
            "locked": False,
        }
        mock_save_token.return_value = None

        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                json={"username": "testuser", "password": "secret_sauce"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert "token" in data["data"]
            assert data["data"]["token"] == f"mock-token-testuser"

    @allure.title("登录-用户名为空")
    def test_login_empty_username(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                json={"username": "", "password": "secret_sauce"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 1002

    @allure.title("登录-密码为空")
    def test_login_empty_password(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                json={"username": "testuser", "password": ""},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 1003

    @allure.title("登录-密码错误")
    @patch("app.app.get_user")
    def test_login_wrong_password(self, mock_get_user):
        mock_get_user.return_value = {
            "username": "testuser",
            "password": "secret_sauce",
            "locked": False,
        }

        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                json={"username": "testuser", "password": "wrong_password"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 1001

    @allure.title("登录-用户被锁定")
    @patch("app.app.get_user")
    def test_login_locked_user(self, mock_get_user):
        mock_get_user.return_value = {
            "username": "locked_user",
            "password": "secret_sauce",
            "locked": True,
        }

        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                json={"username": "locked_user", "password": "secret_sauce"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 1004

    @allure.title("登录-用户不存在")
    @patch("app.app.get_user")
    def test_login_nonexistent_user(self, mock_get_user):
        mock_get_user.return_value = None

        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                json={"username": "nobody", "password": "secret_sauce"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 1001

    @allure.title("登录-Content-Type 错误")
    def test_login_invalid_content_type(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                data="username=testuser&password=secret_sauce",
                content_type="application/x-www-form-urlencoded",
            )
            data = resp.get_json()
            assert data["code"] == 1005

    @allure.title("登录-JSON 格式错误")
    def test_login_invalid_json(self):
        with app.test_client() as client:
            resp = client.post(
                "/api/login",
                data="{invalid json}",
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 1006


@allure.feature("单元测试")
@allure.story("商品接口")
class TestProductUnit:

    @allure.title("获取商品列表-默认分页")
    @patch("app.app.list_products")
    def test_list_products_default(self, mock_list_products):
        mock_list_products.return_value = [
            {"id": 1, "name": "Product A", "price": 10.0, "stock": 5},
            {"id": 2, "name": "Product B", "price": 20.0, "stock": 3},
        ]

        with app.test_client() as client:
            resp = client.get("/api/products")
            data = resp.get_json()
            assert data["code"] == 0
            assert len(data["data"]["list"]) == 2
            assert data["data"]["total"] == 2
            assert data["data"]["page"] == 1
            assert data["data"]["size"] == 10

    @allure.title("获取商品列表-关键字搜索")
    @patch("app.app.list_products")
    def test_list_products_with_keyword(self, mock_list_products):
        mock_list_products.return_value = [
            {"id": 1, "name": "Sauce Labs Backpack", "price": 29.99, "stock": 10},
            {"id": 2, "name": "Sauce Labs Bike Light", "price": 9.99, "stock": 5},
            {"id": 3, "name": "Test.allTheThings() T-Shirt", "price": 15.99, "stock": 50},
        ]

        with app.test_client() as client:
            resp = client.get("/api/products?keyword=sauce")
            data = resp.get_json()
            assert data["code"] == 0
            assert len(data["data"]["list"]) == 2
            assert data["data"]["total"] == 2

    @allure.title("获取商品列表-page 参数非法")
    def test_list_products_invalid_page(self):
        with app.test_client() as client:
            resp = client.get("/api/products?page=0")
            data = resp.get_json()
            assert data["code"] == 2001

    @allure.title("获取商品列表-size 参数非法")
    def test_list_products_invalid_size(self):
        with app.test_client() as client:
            resp = client.get("/api/products?size=200")
            data = resp.get_json()
            assert data["code"] == 2002

    @allure.title("获取单个商品-成功")
    @patch("app.app.get_product")
    def test_get_product_success(self, mock_get_product):
        mock_get_product.return_value = {
            "id": 1,
            "name": "Sauce Labs Backpack",
            "price": 29.99,
            "stock": 10,
        }

        with app.test_client() as client:
            resp = client.get("/api/products/1")
            data = resp.get_json()
            assert data["code"] == 0
            assert data["data"]["id"] == 1
            assert data["data"]["name"] == "Sauce Labs Backpack"

    @allure.title("获取单个商品-不存在")
    @patch("app.app.get_product")
    def test_get_product_not_found(self, mock_get_product):
        mock_get_product.return_value = None

        with app.test_client() as client:
            resp = client.get("/api/products/999")
            data = resp.get_json()
            assert data["code"] == 3001


@allure.feature("单元测试")
@allure.story("购物车接口")
class TestCartUnit:

    @allure.title("添加商品到购物车-成功")
    @patch("app.app.get_cart")
    @patch("app.app.add_to_cart")
    @patch("app.app.get_product")
    @patch("app.app._get_token_user")
    def test_add_to_cart_success(self, mock_token_user, mock_get_product,
                                  mock_add_to_cart, mock_get_cart):
        mock_token_user.return_value = "testuser"
        mock_get_product.return_value = {
            "id": 1,
            "name": "Sauce Labs Backpack",
            "price": 29.99,
            "stock": 10,
        }
        mock_add_to_cart.return_value = None
        mock_get_cart.return_value = [
            {"product_id": 1, "name": "Sauce Labs Backpack", "price": 29.99, "quantity": 2}
        ]

        with app.test_client() as client:
            resp = client.post(
                "/api/cart",
                json={"product_id": 1, "quantity": 2},
                headers={"Authorization": "Bearer mock-token-testuser"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert len(data["data"]["cart"]) == 1

    @allure.title("添加商品到购物车-未授权")
    @patch("app.app._get_token_user")
    def test_add_to_cart_unauthorized(self, mock_token_user):
        mock_token_user.return_value = None

        with app.test_client() as client:
            resp = client.post(
                "/api/cart",
                json={"product_id": 1, "quantity": 1},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 4001

    @allure.title("添加商品到购物车-商品不存在")
    @patch("app.app.get_product")
    @patch("app.app._get_token_user")
    def test_add_to_cart_product_not_found(self, mock_token_user, mock_get_product):
        mock_token_user.return_value = "testuser"
        mock_get_product.return_value = None

        with app.test_client() as client:
            resp = client.post(
                "/api/cart",
                json={"product_id": 999, "quantity": 1},
                headers={"Authorization": "Bearer mock-token-testuser"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 3001

    @allure.title("添加商品到购物车-库存不足")
    @patch("app.app.get_product")
    @patch("app.app._get_token_user")
    def test_add_to_cart_out_of_stock(self, mock_token_user, mock_get_product):
        mock_token_user.return_value = "testuser"
        mock_get_product.return_value = {
            "id": 5,
            "name": "Sauce Labs Onesie",
            "price": 7.99,
            "stock": 0,
        }

        with app.test_client() as client:
            resp = client.post(
                "/api/cart",
                json={"product_id": 5, "quantity": 1},
                headers={"Authorization": "Bearer mock-token-testuser"},
                content_type="application/json",
            )
            data = resp.get_json()
            assert data["code"] == 3003

    @allure.title("查看购物车-未授权")
    @patch("app.app._get_token_user")
    def test_get_cart_unauthorized(self, mock_token_user):
        mock_token_user.return_value = None

        with app.test_client() as client:
            resp = client.get("/api/cart")
            data = resp.get_json()
            assert data["code"] == 4001

    @allure.title("查看购物车-成功")
    @patch("app.app.get_cart")
    @patch("app.app._get_token_user")
    def test_get_cart_success(self, mock_token_user, mock_get_cart):
        mock_token_user.return_value = "testuser"
        mock_get_cart.return_value = [
            {"product_id": 1, "name": "Sauce Labs Backpack", "price": 29.99, "quantity": 2},
            {"product_id": 2, "name": "Sauce Labs Bike Light", "price": 9.99, "quantity": 1},
        ]

        with app.test_client() as client:
            resp = client.get(
                "/api/cart",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert len(data["data"]["cart"]) == 2
            assert data["data"]["total_price"] == 69.97

    @allure.title("从购物车移除商品-成功")
    @patch("app.app.get_cart")
    @patch("app.app.remove_from_cart")
    @patch("app.app._get_token_user")
    def test_remove_from_cart_success(self, mock_token_user, mock_remove_from_cart,
                                       mock_get_cart):
        mock_token_user.return_value = "testuser"
        mock_remove_from_cart.return_value = True
        mock_get_cart.return_value = [
            {"product_id": 2, "name": "Sauce Labs Bike Light", "price": 9.99, "quantity": 1},
        ]

        with app.test_client() as client:
            resp = client.delete(
                "/api/cart/1",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert len(data["data"]["cart"]) == 1

    @allure.title("从购物车移除商品-商品不在购物车中")
    @patch("app.app.remove_from_cart")
    @patch("app.app._get_token_user")
    def test_remove_from_cart_not_in_cart(self, mock_token_user, mock_remove_from_cart):
        mock_token_user.return_value = "testuser"
        mock_remove_from_cart.return_value = False

        with app.test_client() as client:
            resp = client.delete(
                "/api/cart/999",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 3005


@allure.feature("单元测试")
@allure.story("订单接口")
class TestOrderUnit:

    @allure.title("创建订单-成功")
    @patch("app.app.clear_cart")
    @patch("app.app.add_order_item")
    @patch("app.app.create_order")
    @patch("app.app.get_cart")
    @patch("app.app._get_token_user")
    def test_create_order_success(self, mock_token_user, mock_get_cart,
                                   mock_create_order, mock_add_order_item,
                                   mock_clear_cart):
        mock_token_user.return_value = "testuser"
        mock_get_cart.return_value = [
            {"product_id": 1, "name": "Sauce Labs Backpack", "price": 29.99, "quantity": 2},
        ]
        mock_create_order.return_value = 1
        mock_add_order_item.return_value = None
        mock_clear_cart.return_value = None

        with app.test_client() as client:
            resp = client.post(
                "/api/orders",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert data["data"]["order_id"] == 1
            assert data["data"]["status"] == "created"

    @allure.title("创建订单-购物车为空")
    @patch("app.app.get_cart")
    @patch("app.app._get_token_user")
    def test_create_order_empty_cart(self, mock_token_user, mock_get_cart):
        mock_token_user.return_value = "testuser"
        mock_get_cart.return_value = []

        with app.test_client() as client:
            resp = client.post(
                "/api/orders",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 5001

    @allure.title("创建订单-未授权")
    @patch("app.app._get_token_user")
    def test_create_order_unauthorized(self, mock_token_user):
        mock_token_user.return_value = None

        with app.test_client() as client:
            resp = client.post("/api/orders")
            data = resp.get_json()
            assert data["code"] == 4001

    @allure.title("获取订单列表-成功")
    @patch("app.app.list_orders")
    @patch("app.app._get_token_user")
    def test_list_orders_success(self, mock_token_user, mock_list_orders):
        mock_token_user.return_value = "testuser"
        mock_list_orders.return_value = [
            {
                "order_id": 1,
                "username": "testuser",
                "total_price": 59.98,
                "status": "created",
                "created_at": "2025-01-01 00:00:00",
            },
            {
                "order_id": 2,
                "username": "testuser",
                "total_price": 29.99,
                "status": "created",
                "created_at": "2025-01-02 00:00:00",
            },
        ]

        with app.test_client() as client:
            resp = client.get(
                "/api/orders",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert len(data["data"]["orders"]) == 2
            assert data["data"]["total"] == 2

    @allure.title("获取单个订单-成功")
    @patch("app.app.get_order")
    @patch("app.app._get_token_user")
    def test_get_order_success(self, mock_token_user, mock_get_order):
        mock_token_user.return_value = "testuser"
        mock_get_order.return_value = {
            "order_id": 1,
            "username": "testuser",
            "total_price": 59.98,
            "status": "created",
            "created_at": "2025-01-01 00:00:00",
            "items": [
                {"product_id": 1, "name": "Sauce Labs Backpack", "price": 29.99, "quantity": 2}
            ],
        }

        with app.test_client() as client:
            resp = client.get(
                "/api/orders/1",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 0
            assert data["data"]["order_id"] == 1

    @allure.title("获取单个订单-订单不存在")
    @patch("app.app.get_order")
    @patch("app.app._get_token_user")
    def test_get_order_not_found(self, mock_token_user, mock_get_order):
        mock_token_user.return_value = "testuser"
        mock_get_order.return_value = None

        with app.test_client() as client:
            resp = client.get(
                "/api/orders/999",
                headers={"Authorization": "Bearer mock-token-testuser"},
            )
            data = resp.get_json()
            assert data["code"] == 5002
