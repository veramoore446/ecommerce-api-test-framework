import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/api/login"


@pytest.mark.parametrize(
    "title, username, password, expected_code, expected_msg, check_token",
    [
        (
            "正确账号密码登录成功",
            "standard_user",
            "secret_sauce",
            0,
            "success",
            True,
        ),
        (
            "错误密码登录失败",
            "standard_user",
            "wrong_password",
            1001,
            "username or password error",
            False,
        ),
        (
            "用户名为空",
            "",
            "secret_sauce",
            1002,
            "username is required",
            False,
        ),
        (
            "密码为空",
            "standard_user",
            "",
            1003,
            "password is required",
            False,
        ),
        (
            "用户不存在",
            "not_exist_user",
            "secret_sauce",
            1001,
            "username or password error",
            False,
        ),
        (
            "用户被锁定",
            "locked_out_user",
            "secret_sauce",
            1004,
            "user is locked",
            False,
        ),
    ],
    ids=[
        "login_success",
        "wrong_password",
        "empty_username",
        "empty_password",
        "user_not_exist",
        "user_locked",
    ],
)
def test_login(title, username, password, expected_code, expected_msg, check_token):
    payload = {"username": username, "password": password}
    response = requests.post(LOGIN_URL, json=payload)

    assert response.status_code == 200, f"HTTP 状态码期望 200，实际 {response.status_code}"

    body = response.json()
    assert body["code"] == expected_code, f"业务 code 期望 {expected_code}，实际 {body['code']}"
    assert body["message"] == expected_msg, f"message 期望 {expected_msg}，实际 {body['message']}"

    if check_token:
        assert body["data"] is not None, "登录成功时 data 不应为空"
        assert "token" in body["data"], "登录成功时应返回 token"
        assert body["data"]["token"].startswith("mock-token-"), f"token 格式异常: {body['data']['token']}"
    else:
        assert body["data"] is None, f"登录失败时 data 应为 null，实际 {body['data']}"