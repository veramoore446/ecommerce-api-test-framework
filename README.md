# 电商接口自动化测试框架

基于 Python + Flask + SQLite + Pytest + Requests + Allure 搭建的电商系统接口自动化测试框架，覆盖登录、商品、购物车、订单四大核心业务模块。

## 技术栈

| 类别 | 技术 |
|---|---|
| 被测系统 | Python + Flask + SQLite |
| 接口管理 | Apifox |
| 自动化测试 | Python + Pytest + Requests |
| 数据驱动 | YAML |
| 测试报告 | Allure |
| 日志系统 | Python logging |
| 版本管理 | Git + GitHub |
| CI/CD | GitHub Actions |

## 项目结构

```
ecommerce-api-test-framework/
├── app/                    # 被测系统（Flask + SQLite）
│   ├── app.py              # Flask 应用主入口
│   └── models.py           # SQLite 数据库模型
├── common/                 # 公共模块
│   ├── request_util.py     # 请求封装工具类
│   ├── data_loader.py      # YAML 数据加载工具
│   └── logger.py           # 日志工具
├── data/                   # 测试数据（YAML）
│   ├── login_cases.yaml    # 登录测试数据
│   ├── cart_cases.yaml     # 购物车测试数据
│   └── users.yaml          # 测试账号配置
├── tests/                  # 测试用例
│   ├── test_login.py       # 登录模块
│   ├── test_product.py     # 商品模块
│   ├── test_cart.py        # 购物车模块
│   └── test_order.py       # 订单模块
├── .github/workflows/      # GitHub Actions CI 配置
├── docs/                   # 文档
│   └── 接口文档.md
├── logs/                   # 日志文件（自动生成）
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
python app/app.py
```

服务默认运行在 `http://127.0.0.1:5000`。

### 3. 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行并生成覆盖率报告
pytest tests/ -v --cov=app --cov=common --cov-report=term

# 运行并生成 Allure 报告
pytest tests/ --alluredir=allure-results --clean-alluredir
allure generate allure-results -o allure-report --clean
```

### 4. 查看报告

生成报告后，用浏览器打开 `allure-report/index.html`。

## 项目升级亮点

### SQLite 数据库

之前使用内存字典存储数据，服务重启数据丢失。升级后使用 SQLite 数据库，数据持久化存储，支持 SQL 查询，更接近真实项目。

### YAML 数据驱动

测试数据从代码中抽离，放在 YAML 文件中管理。新增测试场景只需修改 YAML 文件，无需改动代码，实现测试逻辑与数据分离。

### 日志系统

使用 Python logging 模块记录每次请求和响应，测试失败时可快速定位问题。日志按日期分文件，支持 DEBUG/INFO/ERROR 多级输出。

### GitHub Actions CI/CD

每次 push 代码自动触发测试流水线：安装依赖 → 启动服务 → 运行测试 → 生成覆盖率报告 → 上传报告。保证代码质量，防止有问题的代码合并。

### 测试覆盖率

使用 pytest-cov 统计测试覆盖率，量化测试完整性，帮助发现未覆盖的代码路径。

## 接口清单

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 健康检查 | GET | /api/health | 检查服务状态 |
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
- **参数化测试** — 登录接口使用 YAML 数据驱动覆盖多种错误场景

## 面试话术参考

> 我独立完成了一个电商接口自动化测试框架，技术栈是 Flask + SQLite + Pytest + Requests + Allure。
>
> 项目经历了三次升级：最初用内存字典存数据，后来换成 SQLite 数据库实现数据持久化；测试数据从硬编码改成 YAML 文件驱动，实现数据和代码分离；接入了 GitHub Actions CI/CD，每次提交自动跑测试并生成覆盖率报告。
>
> 过程中遇到测试数据污染的问题，通过给每个模块分配独立测试用户解决，理解了测试隔离的重要性。
