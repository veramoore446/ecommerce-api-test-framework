import os
import yaml

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_yaml(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_login_cases():
    data = load_yaml("login_cases.yaml")
    cases = []
    for case in data.get("normal", []):
        case["category"] = "normal"
        cases.append(case)
    for case in data.get("error", []):
        case["category"] = "error"
        cases.append(case)
    return cases


def get_test_account(name):
    data = load_yaml("users.yaml")
    return data["test_accounts"][name]
