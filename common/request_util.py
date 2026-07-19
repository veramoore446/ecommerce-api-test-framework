import requests


class RequestUtil:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        resp = self.session.post(
            f"{self.base_url}/api/login",
            json={"username": username, "password": password},
        )
        body = resp.json()
        if body["code"] == 0:
            self.token = body["data"]["token"]
        return resp

    def get(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return self.session.get(f"{self.base_url}{path}", headers=headers, **kwargs)

    def post(self, path, json=None, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return self.session.post(f"{self.base_url}{path}", json=json, headers=headers, **kwargs)

    def delete(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return self.session.delete(f"{self.base_url}{path}", headers=headers, **kwargs)