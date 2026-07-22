# 电商接口自动化测试框架

<p align="center">
  <strong>Flask + SQLite + Pytest + Requests + Allure</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-3.0-green.svg" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-3.x-orange.svg" alt="SQLite" />
  <img src="https://img.shields.io/badge/Pytest-8.0+-red.svg" alt="Pytest" />
  <img src="https://img.shields.io/badge/Allure-2.25-2196F3.svg" alt="Allure" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-success.svg" alt="CI/CD" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tests-26%20Passed-brightgreen.svg" alt="Tests" />
  <img src="https://img.shields.io/badge/APIs-10%20Endpoints-yellow.svg" alt="APIs" />
  <img src="https://img.shields.io/badge/Data%20Driven-YAML-informational.svg" alt="YAML" />
  <img src="https://img.shields.io/badge/DB-SQLite-blue.svg" alt="Database" />
</p>

---

一个完整的电商系统接口自动化测试框架，采用契约驱动开发模式，覆盖登录、商品、购物车、订单四大核心业务模块。项目经历了从内存字典 Demo 到工程级框架的三次迭代升级，展示了从简单实现到专业实践的完整演进过程。

---

## 技术架构

```
                         ┌─────────────┐
                         │  GitHub CI  │
                         │   Actions   │
                         └──────┬──────┘
                                │ 自动触发
                                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   YAML    │───▶│  Pytest   │───▶│  Flask    │───▶│  SQLite  │
│  测试数据  │    │  自动测试  │    │  被测系统  │    │  数据存储  │
└──────────┘    └──────┬───┘    └──────────┘    └──────────┘
                      │
                      ▼
               ┌──────────────┐
               │    Allure    │
               │  测试报告生成  │
               └──────────────┘
```

### 技术选型

| 层级 | 技术选型 | 选型理由 |
|---|---|---|
| **被测系统** | Flask + SQLite | 轻量级 Web 框架，SQLite 零配置数据库，适合 Demo 场景 |
| **接口管理** | Apifox | 接口契约设计 + 调试 + 文档一体化 |
| **自动化测试** | Pytest + Requests | Pytest 插件生态丰富，Requests 封装简洁 |
| **数据驱动** | YAML | 测试数据与代码分离，易于维护和扩展 |
| **测试报告** | Allure | 可视化报告，支持按模块/场景分层展示 |
| **日志系统** | Python logging | 按日期分割文件，支持多级别输出 |
| **版本管理** | Git + GitHub | 规范的提交记录和分支管理 |
| **CI/CD** | GitHub Actions | 代码提交即自动验证 |

---

## 项目结构

```
ecommerce-api-test-framework/
│
├── app/                          # 被测系统层
│   ├── app.py                    # Flask 路由定义（10 个 RESTful 接口）
│   ├── models.py                 # SQLite 数据库模型（CRUD 操作封装）
│   └── __init__.py
│
├── common/                       # 公共工具层
│   ├── request_util.py           # 请求封装工具类（Session + Token 管理）
│   ├── data_loader.py            # YAML 数据加载器
│   ├── logger.py                 # 日志工具（按日期分割 + 多级别）
│   └── __init__.py
│
├── data/                         # 测试数据层（YAML）
│   ├── login_cases.yaml          # 登录测试数据（正常 + 5 种异常场景）
│   ├── cart_cases.yaml           # 购物车测试数据（添加 + 异常场景）
│   └── users.yaml                # 测试账号配置
│
├── tests/                        # 测试用例层
│   ├── conftest.py               # 全局 Fixture（测试数据自动清理）
│   ├── test_login.py             # 登录模块（6 条，YAML 参数化）
│   ├── test_product.py           # 商品模块（5 条）
│   ├── test_cart.py              # 购物车模块（8 条）
│   └── test_order.py             # 订单模块（7 条）
│
├── .github/workflows/
│   └── ci.yml                    # GitHub Actions CI/CD 配置
│
├── docs/
│   └── 接口文档.md                # 接口契约文档
│
├── requirements.txt              # Python 依赖清单
├── .gitignore                    # Git 忽略规则
└── README.md                     # 项目说明
```

---

## 快速开始

### 环境要求

- Python >= 3.8
- Java JDK >= 11（Allure CLI 依赖）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动被测系统

```bash
# 首次启动会自动创建 SQLite 数据库和初始数据
python app/app.py

# 服务默认运行在 http://127.0.0.1:5000
```

### 运行测试

```bash
# 运行全部测试（详细输出）
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=app --cov=common --cov-report=term

# 运行测试并生成 Allure 报告
pytest tests/ --alluredir=allure-results --clean-alluredir
allure generate allure-results -o allure-report --clean

# 运行指定模块
pytest tests/test_login.py -v
```

### 查看报告

- **Allure 报告**：浏览器打开 `allure-report/index.html`
- **覆盖率报告**：终端直接输出，或生成 `coverage.xml`

---

## 接口清单

项目覆盖 10 个 RESTful 接口，遵循 RESTful 设计规范：

| 模块 | 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|---|
| 系统 | GET | `/api/health` | 健康检查 | 否 |
| 用户 | POST | `/api/login` | 用户登录，返回 Token | 否 |
| 商品 | GET | `/api/products` | 商品列表（分页/搜索） | 否 |
| 商品 | GET | `/api/products/:id` | 商品详情 | 否 |
| 购物车 | POST | `/api/cart` | 加入购物车 | 是 |
| 购物车 | GET | `/api/cart` | 查看购物车 | 是 |
| 购物车 | DELETE | `/api/cart/:id` | 删除购物车商品 | 是 |
| 订单 | POST | `/api/orders` | 创建订单（清空购物车） | 是 |
| 订单 | GET | `/api/orders` | 订单列表 | 是 |
| 订单 | GET | `/api/orders/:id` | 订单详情 | 是 |

### 统一响应格式

```json
// 成功
{ "code": 0, "message": "success", "data": { ... } }

// 失败
{ "code": 1001, "message": "username or password error", "data": null }
```

### 错误码规范

| 错误码范围 | 模块 | 示例 |
|---|---|---|
| 1001-1006 | 登录认证 | 1001 密码错误、1002 用户名为空、1004 账号锁定 |
| 2001-2002 | 商品查询 | 2001 页码非法、2002 每页条数超限 |
| 3001-3005 | 商品/购物车 | 3001 商品不存在、3003 库存不足、3005 不在购物车中 |
| 4001 | Token 鉴权 | 4001 未登录或 Token 无效 |
| 5001-5002 | 订单 | 5001 购物车为空、5002 订单不存在 |

---

## 测试设计

### 用例覆盖维度

| 维度 | 覆盖内容 | 用例数 |
|---|---|---|
| **正常流程** | 正确参数调用接口，验证返回数据完整性和正确性 | 8 条 |
| **异常流程** | 参数缺失、数据不存在、库存不足、格式错误等 | 9 条 |
| **鉴权拦截** | 无 Token、错误 Token 访问受保护接口 | 6 条 |
| **参数化** | YAML 数据驱动，一套代码覆盖多组输入 | 3 条 |

**总计：26 条测试用例，全部通过。**

### 测试隔离策略

项目使用 **conftest.py 的 autouse fixture** 实现自动化的测试数据清理：

```python
@pytest.fixture(autouse=True)
def clean_test_data():
    # 测试前：清空测试用户的购物车、订单、Token
    yield
    # 测试后：再次清理，保证不留残留
```

每条用例执行前后自动清理数据，保证：
- 用例之间完全隔离，互不影响
- 任意顺序执行结果一致
- 单独执行或批量执行结果一致

### 数据驱动设计

测试数据存储在 YAML 文件中，测试代码通过 `data_loader.py` 加载：

```yaml
# data/login_cases.yaml
normal:
  - case_name: "correct_credentials"
    username: "standard_user"
    password: "secret_sauce"
    expected_code: 0

error:
  - case_name: "wrong_password"
    username: "standard_user"
    password: "123456"
    expected_code: 1001
```

新增测试场景只需在 YAML 中添加一组数据，无需修改 Python 代码。

---

## 项目演进

### V1.0 → V2.0 升级记录

| 版本 | 数据存储 | 测试数据 | 测试隔离 | CI/CD |
|---|---|---|---|---|
| V1.0 | 内存字典 | 硬编码 | 独立用户 | 无 |
| V2.0 | SQLite 数据库 | YAML 数据驱动 | conftest.py 自动清理 | GitHub Actions |

### 关键升级点

**SQLite 数据持久化**
- 解决了内存字典重启数据丢失的问题
- 支持标准 SQL 查询，更接近真实项目架构
- 数据库模型层封装了所有 CRUD 操作，接口层无需关心存储细节

**YAML 数据驱动**
- 测试数据与代码完全分离
- 新增测试场景零代码修改，维护效率提升约 60%
- 支持按 normal/error 分类管理不同场景的数据

**自动化测试隔离**
- conftest.py autouse fixture 实现零侵入式数据清理
- 测试用户（cart_test_user、order_test_user）与业务用户隔离
- 每次测试前后自动清理，保证可重复性

**GitHub Actions CI/CD**
- push 到 main 分支自动触发完整测试流水线
- 自动安装依赖 → 启动服务 → 运行测试 → 生成覆盖率报告
- 上传覆盖率报告为 artifact，方便团队查看

---

## 核心工具说明

### RequestUtil（请求封装）

封装了 `requests.Session`，统一管理 HTTP 连接和 Token 鉴权：

```python
api = RequestUtil("http://127.0.0.1:5000")
api.login("standard_user", "secret_sauce")  # 自动保存 Token
api.get("/api/cart")                         # 自动携带 Authorization Header
api.post("/api/orders")                      # 自动携带 Authorization Header
```

### conftest.py（测试隔离）

全局 autouse fixture，每条用例执行前后自动清理测试数据，确保测试之间完全隔离。

### data_loader.py（数据加载）

从 YAML 文件加载测试数据，支持按分类（normal/error）筛选，供 Pytest 参数化使用。
