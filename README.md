# 电商接口自动化测试框架

基于 Python + Pytest + Requests + Allure 搭建的电商系统接口自动化测试框架，覆盖登录、商品、购物车、订单四大核心业务模块，共 26 条测试用例。

## 技术栈

| 类别 | 技术 |
|---|---|
| 被测系统 | Python + Flask |
| 接口管理 | Apifox |
| 自动化测试 | Python + Pytest + Requests |
| 测试报告 | Allure |
| 版本管理 | Git + GitHub |

## 项目结构

```
ecommerce-api-test-framework/
├── app/                    # 被测系统（Flask Demo）
│   └── app.py
├── common/                 # 公共模块
│   └── request_util.py     # 请求封装工具类
├── tests/                  # 测试用例
│   ├── test_login.py       # 登录模块（6 条）
│   ├── test_product.py     # 商品模块（5 条）
│   ├── test_cart.py        # 购物车模块（8 条）
│   └── test_order.py       # 订单模块（7 条）
├── docs/                   # 文档
│   └── 接口文档.md
├── .gitignore
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动被测系统

```bash
cd app
python app.py
```

服务默认运行在 `http://127.0.0.1:5000`。

### 3. 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行并生成 Allure 报告
pytest tests/ --alluredir=allure-results --clean-alluredir
allure generate allure-results -o allure-report --clean
```

### 4. 查看报告

生成报告后，用浏览器打开 `allure-report/index.html`，或者使用 Allure 自带的本地服务：

```bash
allure open allure-report
```

## 接口清单

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 登录 | POST | /api/login | 用户登录，返回 token |
| 商品 | GET | /api/products | 商品列表（支持分页和搜索） |
| 商品 | GET | /api/products/:id | 商品详情 |
| 购物车 | POST | /api/cart | 加入购物车 |
| 购物车 | GET | /api/cart | 查看购物车 |
| 购物车 | DELETE | /api/cart/:id | 删除购物车商品 |
| 订单 | POST | /api/orders | 创建订单 |
| 订单 | GET | /api/orders | 订单列表 |
| 订单 | GET | /api/orders/:id | 订单详情 |

## 测试用例设计

测试覆盖以下场景：

- **正常流程** — 各接口的正确调用和响应验证
- **异常流程** — 参数缺失、数据不存在、库存不足等
- **鉴权测试** — 未登录访问、错误 token 访问
- **参数化测试** — 登录接口使用 pytest.mark.parametrize 覆盖多种错误场景

## 项目亮点

- **请求封装** — 封装 RequestUtil 工具类，统一管理 Session 和 Token，避免重复代码
- **测试隔离** — 每个模块使用独立测试账号，避免内存数据污染
- **Allure 报告** — 使用 @allure.feature、@allure.story、@allure.title 注解，报告结构清晰
- **接口契约驱动** — 先在 Apifox 中完成接口文档设计，再进行开发和测试