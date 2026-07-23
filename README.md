<h1 align="center">
  <img src="https://img.shields.io/badge/电商测试框架-5大测试类型%20|%20121条用例-2196F3?style=for-the-badge&labelColor=1a1a2e" alt="电商测试框架" />
</h1>

<p align="center">
  <strong>Flask + SQLite + Pytest + Requests + Allure + Locust</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-3.0-000?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-3.x-003B57?logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Pytest-8.0+-0A9EDC?logo=pytest&logoColor=white" alt="Pytest" />
  <img src="https://img.shields.io/badge/Allure-2.25-0EA5E9?logoColor=white" alt="Allure" />
  <img src="https://img.shields.io/badge/Locust-2.46-0066CC?logoColor=white" alt="Locust" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tests-121%20Passed-brightgreen?logo=checkmarx&logoColor=white" alt="Tests" />
  <img src="https://img.shields.io/badge/APIs-10%20Endpoints-orange" alt="APIs" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white" alt="CI/CD" />
  <img src="https://img.shields.io/badge/Coverage-Pytest--cov-success" alt="Coverage" />
</p>

<br>

> 一个覆盖 **API 测试 / 数据库测试 / 单元测试 / 安全测试 / 性能测试** 五大测试类型的电商测试框架。经历 V1.0 → V2.0 → V3.0 三次迭代，从内存字典 Demo 成长为工程级多类型测试平台。

<br>

---

<br>

## 项目亮点

- **121 条自动化测试用例** — 覆盖 5 大测试类型，全部通过
- **Pytest + YAML 数据驱动** — 测试数据与代码分离，新增场景零代码改动
- **SQLite 数据持久化** — 支持标准 SQL，更接近真实项目架构
- **Mock 隔离单元测试** — unittest.mock 模拟数据库层，只测路由逻辑
- **安全漏洞检测** — SQL 注入、XSS、越权访问、输入校验全面覆盖
- **Locust 负载压测** — 4 种用户行为，模拟真实并发场景
- **GitHub Actions CI/CD** — Push 即触发，自动验证全部测试
- **Allure 可视化报告** — 按模块/场景分层，测试结论一目了然

<br>

---

<br>

## 五大测试类型

```
        API 测试          数据库测试         单元测试          安全测试           性能测试
        26 条用例         42 条用例          29 条用例          22 条用例          Locust 压测
      Requests + YAML    SQLite CRUD      Flask + Mock      SQL注入/XSS        4种用户行为
      接口契约验证       数据完整性        路由逻辑隔离      鉴权/输入校验       并发 & 吞吐量
      参数化/鉴权拦截    边界条件检查      错误处理验证      HTTP方法验证        响应时间分析
```

<br>

---

<br>

## 技术架构

```
                         GitHub Actions
                              │
                              ▼ 自动触发
    ┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐
    │  YAML     │───▶│   Pytest      │───▶│  Flask    │───▶│  SQLite  │
    │ 测试数据  │    │ 121条用例     │    │ 被测系统  │    │ 数据存储  │
    └──────────┘    └──────┬───────┘    └──────────┘    └──────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐  ┌──────────┐  ┌──────────┐
         │ Allure │  │ Coverage │  │  Locust  │
         │ 报告   │  │ 覆盖率   │  │ 性能报告 │
         └────────┘  └──────────┘  └──────────┘
```

<br>

---

<br>

## 项目结构

```
ecommerce-api-test-framework/
│
├── app/                          # 被测系统层
│   ├── app.py                    # Flask 路由（10 个 RESTful 接口）
│   └── models.py                 # SQLite 数据库模型（CRUD 封装）
│
├── common/                       # 公共工具层
│   ├── request_util.py           # 请求封装（Session + Token 管理）
│   ├── data_loader.py            # YAML 数据加载器
│   └── logger.py                 # 日志工具（按日期分割）
│
├── data/                         # 测试数据层（YAML）
│   ├── login_cases.yaml          # 登录测试数据
│   ├── cart_cases.yaml           # 购物车测试数据
│   └── users.yaml                # 测试账号配置
│
├── tests/                        # 测试用例层（121 条）
│   ├── conftest.py               # 全局 Fixture（数据自动清理）
│   ├── test_login.py             # 登录模块（6 条，YAML 参数化）
│   ├── test_product.py           # 商品模块（5 条）
│   ├── test_cart.py              # 购物车模块（8 条）
│   ├── test_order.py             # 订单模块（7 条）
│   ├── test_database.py          # 数据库 CRUD 测试（42 条）
│   ├── test_security.py          # 安全测试（22 条）
│   └── test_unit.py              # 单元测试（29 条，Mock）
│
├── performance/                  # 性能测试层
│   ├── locustfile.py             # Locust 负载测试
│   └── README.md                 # 性能测试文档
│
├── .github/workflows/
│   └── ci.yml                    # GitHub Actions CI/CD
│
├── docs/
│   └── 接口文档.md                # 接口契约文档
│
├── requirements.txt              # Python 依赖
└── README.md                     # 项目说明
```

<br>

---

<br>

## 快速开始

### 环境要求

- Python >= 3.8
- Java JDK >= 11（Allure CLI 依赖）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 首次启动自动创建 SQLite 数据库和初始数据
python app/app.py
# 服务运行在 http://127.0.0.1:5000
```

### 运行全部测试

```bash
# 运行全部 121 条用例（详细输出）
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ -v --cov=app --cov=common --cov-report=term

# 生成 Allure 报告
pytest tests/ --alluredir=allure-results --clean-alluredir
allure generate allure-results -o allure-report --clean
```

### 运行性能测试

```bash
# Web UI 模式
locust -f performance/locustfile.py --host http://127.0.0.1:5000

# 无头模式（直接出结果）
locust -f performance/locustfile.py --headless -u 100 -r 10 -t 30s --host http://127.0.0.1:5000
```

<br>

---

<br>

## 接口清单

| 模块 | 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|---|
| 系统 | GET | `/api/health` | 健康检查 | 否 |
| 用户 | POST | `/api/login` | 用户登录 | 否 |
| 商品 | GET | `/api/products` | 商品列表（分页/搜索） | 否 |
| 商品 | GET | `/api/products/:id` | 商品详情 | 否 |
| 购物车 | POST | `/api/cart` | 加入购物车 | 是 |
| 购物车 | GET | `/api/cart` | 查看购物车 | 是 |
| 购物车 | DELETE | `/api/cart/:id` | 删除购物车商品 | 是 |
| 订单 | POST | `/api/orders` | 创建订单 | 是 |
| 订单 | GET | `/api/orders` | 订单列表 | 是 |
| 订单 | GET | `/api/orders/:id` | 订单详情 | 是 |

**统一响应格式**

```json
// 成功
{ "code": 0, "message": "success", "data": { ... } }

// 失败
{ "code": 1001, "message": "username or password error", "data": null }
```

<br>

---

<br>

## 测试设计

### 用例分布

| 测试类型 | 文件 | 用例数 | 测试方法 |
|---|---|---|---|
| **API 测试** | test_login / test_product / test_cart / test_order | 26 | Requests + YAML 数据驱动 |
| **数据库测试** | test_database.py | 42 | 直接操作 SQLite 验证 CRUD |
| **单元测试** | test_unit.py | 29 | unittest.mock 隔离 Flask 路由 |
| **安全测试** | test_security.py | 22 | 注入 / XSS / 鉴权 / 校验 |
| **性能测试** | locustfile.py | - | Locust 负载压测 |

**自动化测试总计：121 条，全部通过。**

### 覆盖维度

- 正常流程 / 异常流程 / 鉴权拦截
- 数据库 CRUD / 数据完整性 / 边界条件
- 路由逻辑隔离 / Mock 验证 / 错误处理
- SQL 注入防护 / XSS 防护 / 越权检测
- 输入校验 / HTTP 方法验证
- YAML 数据驱动参数化

### 测试隔离

使用 `conftest.py` 的 `autouse` fixture，每条用例前后自动清理测试数据，保证用例之间完全隔离。

```python
@pytest.fixture(autouse=True)
def clean_test_data():
    # 测试前：清空测试用户的购物车、订单、Token
    yield
    # 测试后：再次清理，不留残留
```

<br>

---

<br>

## 项目演进

| 版本 | 数据存储 | 测试数据 | 测试类型 | 用例数 |
|---|---|---|---|---|
| **V1.0** | 内存字典 | 硬编码 | API 测试 | 26 |
| **V2.0** | SQLite | YAML 驱动 | API 测试 | 26 |
| **V3.0** | SQLite | YAML 驱动 | API + DB + Unit + Security + Performance | 121 |

### V1.0 → V2.0 升级

- **SQLite 持久化**：解决内存数据丢失问题，支持标准 SQL
- **YAML 数据驱动**：测试数据与代码分离，维护效率提升约 60%
- **conftest.py 自动清理**：零侵入式测试隔离
- **GitHub Actions CI/CD**：Push 即自动验证

### V2.0 → V3.0 升级

- **多类型测试扩展**：从单一 API 测试扩展为 5 大测试类型
- **数据库测试（42 条）**：验证 SQLite CRUD 和数据完整性
- **单元测试（29 条）**：Mock 隔离 Flask 路由逻辑
- **安全测试（22 条）**：SQL 注入、XSS、鉴权安全、输入校验、HTTP 方法
- **性能测试（Locust）**：4 种用户行为的负载压测

<br>

---

<br>

## 核心工具说明

**RequestUtil** — 封装 `requests.Session`，统一管理 HTTP 连接和 Token 鉴权，自动携带 `Authorization` Header。

**conftest.py** — 全局 autouse fixture，每条用例执行前后自动清理数据，确保测试完全隔离。

**data_loader.py** — 从 YAML 加载测试数据，支持按 normal/error 分类筛选。

**Locust** — 基于 Locust 框架的负载测试，4 种用户行为模拟真实访问模式。

<br>

---

<p align="center">
  <sub>Made with Pytest + Flask + SQLite</sub>
</p>
