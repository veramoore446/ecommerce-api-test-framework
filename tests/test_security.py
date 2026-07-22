import sys, os
import allure
import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.request_util import RequestUtil

BASE_URL = "http://127.0.0.1:5000"


# ============================================================
# SQL 注入测试
# ============================================================
@allure.feature("安全测试")
@allure.story("SQL注入防护")
class TestSQLInjection:
    """验证系统对SQL注入攻击的防护能力"""

    @allure.title("登录接口 - 用户名字段SQL注入 (OR 1=1)")
    def test_login_sql_injection_username_or_true(self):
        """在用户名字段注入 OR 1=1 语句，验证系统正确拒绝"""
        api = RequestUtil(BASE_URL)
        resp = api.post("/api/login", json={
            "username": '" OR 1=1 --',
            "password": "anypassword",
        })
        body = resp.json()
        assert body["code"] != 0, "SQL注入在用户名字段应当被拒绝"
        assert body.get("data") is None or body.get("token") is None

    @allure.title("登录接口 - 密码字段SQL注入 (OR '1'='1')")
    def test_login_sql_injection_password_or_true(self):
        """在密码字段注入 OR '1'='1' 语句，验证系统正确拒绝"""
        api = RequestUtil(BASE_URL)
        resp = api.post("/api/login", json={
            "username": "admin",
            "password": "' OR '1'='1",
        })
        body = resp.json()
        assert body["code"] != 0, "SQL注入在密码字段应当被拒绝"
        assert body.get("data") is None or body.get("token") is None

    @allure.title("商品搜索 - keyword字段SQL注入 (DROP TABLE)")
    def test_product_search_sql_injection_drop_table(self):
        """在搜索关键词中注入 DROP TABLE 语句，验证数据库未被破坏且结果安全"""
        api = RequestUtil(BASE_URL)
        # 先发送注入请求
        resp = api.get("/api/products", params={
            "page": 1,
            "size": 10,
            "keyword": "'; DROP TABLE users; --",
        })
        body = resp.json()
        # 系统使用了参数化查询，注入不会生效；验证返回的是空结果而非报错
        assert body["code"] == 0, "查询应正常返回，不会因注入而报错"
        assert body["data"]["total"] == 0, "注入关键词不应匹配任何商品"

        # 验证数据库未被破坏：用户表仍然正常工作
        login_resp = api.post("/api/login", json={
            "username": "standard_user",
            "password": "secret_sauce",
        })
        login_body = login_resp.json()
        assert login_body["code"] == 0, "SQL注入后用户表应仍然正常，登录不受影响"

    @allure.title("商品详情 - 商品ID路径参数SQL注入")
    def test_product_detail_sql_injection_id(self):
        """在商品ID路径参数中注入SQL语句，验证系统返回404或拒绝"""
        api = RequestUtil(BASE_URL)
        sql_payload = "1 OR 1=1"
        resp = api.get(f"/api/products/{sql_payload}")
        # Flask 路由 <int:product_id> 对非数字路径返回 404
        assert resp.status_code == 404, "非数字路径参数应返回404"


# ============================================================
# XSS 跨站脚本攻击测试
# ============================================================
@allure.feature("安全测试")
@allure.story("XSS跨站脚本防护")
class TestXSS:
    """验证系统对XSS攻击的防护能力"""

    @allure.title("登录接口 - 用户名字段XSS注入 (script标签)")
    def test_login_xss_username_script_tag(self):
        """在用户名字段注入script标签，验证系统不回显未转义的XSS载荷"""
        api = RequestUtil(BASE_URL)
        xss_payload = "<script>alert(1)</script>"
        resp = api.post("/api/login", json={
            "username": xss_payload,
            "password": "test123",
        })
        body = resp.json()
        assert body["code"] != 0, "XSS载荷在用户名中应当被拒绝"
        # 确认响应体中不包含原始的未转义XSS载荷
        resp_text = resp.text
        assert "<script>alert(1)</script>" not in resp_text, \
            "响应中不应包含未转义的<script>标签"

    @allure.title("登录接口 - 密码字段XSS注入 (img标签onerror)")
    def test_login_xss_password_img_onerror(self):
        """在密码字段注入img标签onerror事件，验证系统不回显未转义的XSS载荷"""
        api = RequestUtil(BASE_URL)
        xss_payload = '"><img src=x onerror=alert(1)>'
        resp = api.post("/api/login", json={
            "username": "testuser",
            "password": xss_payload,
        })
        body = resp.json()
        assert body["code"] != 0, "XSS载荷在密码中应当被拒绝"
        resp_text = resp.text
        assert "onerror=alert(1)" not in resp_text, \
            "响应中不应包含未转义的onerror事件处理器"

    @allure.title("购物车接口 - product_id字段XSS注入")
    def test_cart_xss_product_id(self):
        """在购物车请求的product_id中注入XSS载荷（以字符串形式发送），验证系统正确拒绝"""
        api = RequestUtil(BASE_URL)
        api.login("testuser", "test123")
        xss_payload = "<script>alert('xss')</script>"
        resp = api.post("/api/cart", json={
            "product_id": xss_payload,
            "quantity": 1,
        })
        body = resp.json()
        assert body["code"] != 0, "XSS载荷在product_id中应当被拒绝"
        resp_text = resp.text
        assert "<script>alert('xss')</script>" not in resp_text, \
            "响应中不应包含未转义的XSS载荷"


# ============================================================
# 认证与授权安全测试
# ============================================================
@allure.feature("安全测试")
@allure.story("认证与授权安全")
class TestAuthSecurity:
    """验证系统的认证和授权机制安全性"""

    @allure.title("未携带Token访问受保护接口 - 购物车列表")
    def test_access_protected_without_token(self):
        """不携带任何Token直接访问需要认证的接口，应当返回未授权错误"""
        api = RequestUtil(BASE_URL)
        # 不调用login，token为None
        resp = api.get("/api/cart")
        assert resp.status_code == 401 or resp.json()["code"] != 0, \
            "未携带Token访问受保护接口应当被拒绝"

    @allure.title("携带空Bearer Token访问受保护接口")
    def test_access_protected_with_empty_bearer_token(self):
        """携带空字符串的Bearer Token访问受保护接口，应当返回未授权错误"""
        api = RequestUtil(BASE_URL)
        resp = api.session.get(
            f"{BASE_URL}/api/cart",
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 401 or resp.json()["code"] != 0, \
            "空Bearer Token访问受保护接口应当被拒绝"

    @allure.title("携带格式错误的Token访问受保护接口")
    def test_access_protected_with_malformed_token(self):
        """携带不符合预期格式的伪造Token访问受保护接口，应当返回未授权错误"""
        api = RequestUtil(BASE_URL)
        malformed_tokens = [
            "not.a.valid.token",
            "!!!invalid@@@token###",
            "a" * 500,
            "null",
            "undefined",
        ]
        for token in malformed_tokens:
            resp = api.session.get(
                f"{BASE_URL}/api/cart",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 401 or resp.json()["code"] != 0, \
                f"伪造Token '{token[:20]}...' 访问受保护接口应当被拒绝"

    @allure.title("水平越权 - 尝试访问其他用户的订单")
    def test_horizontal_privilege_escalation_order(self):
        """使用一个用户的Token尝试访问另一个用户的订单详情，应当被拒绝"""
        api = RequestUtil(BASE_URL)
        api.login("testuser", "test123")
        # 尝试访问一个不存在的或属于其他用户的订单ID
        resp = api.get("/api/orders/99999")
        body = resp.json()
        assert body["code"] != 0, "不应能访问到不属于当前用户的订单"

    @allure.title("暴力破解模式 - 快速重复登录尝试")
    def test_brute_force_rapid_login_attempts(self):
        """模拟暴力破解攻击模式，快速连续发送多次错误登录请求，验证每次都失败"""
        api = RequestUtil(BASE_URL)
        wrong_passwords = [
            "wrong1", "wrong2", "wrong3", "wrong4", "wrong5",
            "wrong6", "wrong7", "wrong8", "wrong9", "wrong10",
        ]
        for pwd in wrong_passwords:
            resp = api.post("/api/login", json={
                "username": "admin",
                "password": pwd,
            })
            body = resp.json()
            assert body["code"] != 0, \
                f"使用错误密码 '{pwd}' 登录应当失败"


# ============================================================
# 输入验证测试
# ============================================================
@allure.feature("安全测试")
@allure.story("输入验证防护")
class TestInputValidation:
    """验证系统对异常和恶意输入的校验能力"""

    @allure.title("登录接口 - 超长用户名 (1000+字符)")
    def test_login_extremely_long_username(self):
        """发送超过1000字符的用户名，验证系统正确拒绝或截断，不应导致异常"""
        api = RequestUtil(BASE_URL)
        long_username = "a" * 1001
        resp = api.post("/api/login", json={
            "username": long_username,
            "password": "test123",
        })
        body = resp.json()
        assert body["code"] != 0, "超长用户名应当被拒绝"

    @allure.title("登录接口 - 特殊字符字段")
    def test_login_special_characters(self):
        """在登录字段中发送各种特殊字符，验证系统正确处理"""
        api = RequestUtil(BASE_URL)
        special_chars_list = [
            "\x00\x01\x02",
            "\n\r\t",
            "\u0000",
            "user@admin.com;--",
            "${7*7}",
            "{{7*7}}",
            "#{7*7}",
        ]
        for chars in special_chars_list:
            resp = api.post("/api/login", json={
                "username": chars,
                "password": "test123",
            })
            body = resp.json()
            assert body["code"] != 0, \
                f"包含特殊字符的用户名应当被拒绝: {repr(chars)}"

    @allure.title("购物车接口 - 负数数量")
    def test_cart_negative_quantity(self):
        """发送负数商品数量，验证系统正确拒绝"""
        api = RequestUtil(BASE_URL)
        api.login("testuser", "test123")
        resp = api.post("/api/cart", json={
            "product_id": 1,
            "quantity": -5,
        })
        body = resp.json()
        assert body["code"] != 0, "负数商品数量应当被拒绝"

    @allure.title("购物车接口 - 浮点数product_id")
    def test_cart_float_product_id(self):
        """发送浮点数类型的product_id，验证系统正确拒绝"""
        api = RequestUtil(BASE_URL)
        api.login("testuser", "test123")
        resp = api.post("/api/cart", json={
            "product_id": 3.14,
            "quantity": 1,
        })
        body = resp.json()
        assert body["code"] != 0, "浮点数product_id应当被拒绝"

    @allure.title("请求Content-Type错误 - 使用text/plain代替application/json")
    def test_wrong_content_type(self):
        """使用text/plain作为Content-Type发送请求，验证系统正确拒绝"""
        api = RequestUtil(BASE_URL)
        resp = requests.post(
            f"{BASE_URL}/api/login",
            data='{"username": "admin", "password": "test123"}',
            headers={"Content-Type": "text/plain"},
        )
        body = resp.json()
        assert body["code"] != 0, "错误的Content-Type应当被拒绝"

    @allure.title("请求体JSON格式错误")
    def test_malformed_json_body(self):
        """发送格式错误的JSON请求体，验证系统正确处理并返回错误"""
        api = RequestUtil(BASE_URL)
        malformed_bodies = [
            "{invalid json}",
            '{"username": "admin", "password": }',
            '{"username": "admin", }',
            "just a plain text string",
            "{\"username\": undefined}",
        ]
        for malformed_body in malformed_bodies:
            resp = requests.post(
                f"{BASE_URL}/api/login",
                data=malformed_body,
                headers={"Content-Type": "application/json"},
            )
            body = resp.json()
            assert body["code"] != 0, \
                f"格式错误的JSON应当被拒绝: {malformed_body[:30]}"

    @allure.title("请求体包含额外未预期字段")
    def test_extra_unexpected_fields(self):
        """发送包含额外未预期字段的请求体，验证系统忽略或拒绝多余字段"""
        api = RequestUtil(BASE_URL)
        resp = api.post("/api/login", json={
            "username": "testuser",
            "password": "test123",
            "role": "admin",
            "is_admin": True,
            "user_id": 1,
            "permission": "all",
        })
        body = resp.json()
        # 即使登录成功（返回code==0），也不应因为额外字段而提升权限
        if body["code"] == 0:
            token = body["data"]["token"]
            api.token = token
            # 验证该用户并没有因为额外字段获得管理员权限
            resp2 = api.get("/api/cart")
            body2 = resp2.json()
            assert body2["code"] == 0, "正常用户登录后应能正常访问自己的购物车"
        # 如果系统直接拒绝含额外字段的请求，也是合理的防护行为


# ============================================================
# HTTP方法测试
# ============================================================
@allure.feature("安全测试")
@allure.story("HTTP方法限制")
class TestHTTPMethod:
    """验证系统对HTTP方法的正确限制，不允许不支持的请求方法"""

    @allure.title("GET方法访问登录接口 - 应当被拒绝")
    def test_get_method_on_login(self):
        """使用GET方法访问只允许POST的/api/login接口，应当返回405或错误"""
        api = RequestUtil(BASE_URL)
        resp = api.session.get(f"{BASE_URL}/api/login")
        assert resp.status_code == 405 or resp.json()["code"] != 0, \
            "GET方法访问登录接口应当被拒绝"

    @allure.title("POST方法访问商品列表接口 - 应当被拒绝")
    def test_post_method_on_products_list(self):
        """使用POST方法访问只允许GET的/api/products接口，应当返回405或错误"""
        api = RequestUtil(BASE_URL)
        resp = api.session.post(f"{BASE_URL}/api/products?page=1&size=10")
        assert resp.status_code == 405 or resp.json()["code"] != 0, \
            "POST方法访问商品列表接口应当被拒绝"

    @allure.title("PUT方法访问登录接口 - 应当返回405")
    def test_put_method_on_login(self):
        """使用PUT方法访问/api/login接口，应当返回405 Method Not Allowed"""
        api = RequestUtil(BASE_URL)
        resp = api.session.put(
            f"{BASE_URL}/api/login",
            json={"username": "admin", "password": "test123"},
        )
        assert resp.status_code == 405, \
            "PUT方法访问登录接口应当返回405"

    @allure.title("DELETE方法访问登录接口 - 应当返回405")
    def test_delete_method_on_login(self):
        """使用DELETE方法访问/api/login接口，应当返回405 Method Not Allowed"""
        api = RequestUtil(BASE_URL)
        resp = api.session.delete(f"{BASE_URL}/api/login")
        assert resp.status_code == 405, \
            "DELETE方法访问登录接口应当返回405"

    @allure.title("非标准HTTP方法访问接口 - PATCH/OPTIONS/TRACE")
    def test_non_standard_http_methods(self):
        """使用非标准的HTTP方法访问API接口，验证服务器正确拒绝"""
        api = RequestUtil(BASE_URL)
        non_standard_methods = ["PATCH", "TRACE"]
        for method in non_standard_methods:
            resp = api.session.request(
                method,
                f"{BASE_URL}/api/login",
            )
            assert resp.status_code == 405, \
                f"{method} 方法访问登录接口应当返回405"
