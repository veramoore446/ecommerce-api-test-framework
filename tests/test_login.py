import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import allure
import pytest
from common.request_util import RequestUtil
from common.data_loader import get_login_cases

BASE_URL = "http://127.0.0.1:5000"


@allure.feature("登录模块")
class TestLogin:
    @allure.story("登录功能")
    @allure.title("登录参数化测试")
    @pytest.mark.parametrize("case", get_login_cases(), ids=lambda c: c["case_name"])
    def test_login(self, case):
        api = RequestUtil(BASE_URL)
        resp = api.post("/api/login", json={
            "username": case["username"],
            "password": case["password"],
        })
        body = resp.json()
        assert body["code"] == case["expected_code"]
        if case["category"] == "normal":
            assert body["data"]["token"] is not None
            assert body["data"]["username"] == case["username"]
        else:
            assert body["data"] is None
