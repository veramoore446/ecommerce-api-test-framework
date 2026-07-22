# Performance Testing (Locust)

本目录包含基于 [Locust](https://locust.io/) 的电商 API 性能测试脚本，用于对运行在 `http://127.0.0.1:5000` 的后端服务进行负载测试。

## 前置条件

- Python 3.8+
- 安装 Locust：`pip install locust`
- 确保 API 服务已启动并运行在 `http://127.0.0.1:5000`

## 快速启动

### Web UI 模式（推荐，可视化控制台）

```bash
locust -f performance/locustfile.py
```

启动后浏览器访问 `http://localhost:8089`，在页面上设置并发用户数和每秒孵化速率，点击 **Start swarming** 即可开始测试。

### 无头模式（Headless，适合 CI/CD 场景）

```bash
locust -f performance/locustfile.py --headless -u 10 -r 2 -t 30s --html=performance/report.html
```

参数说明：

| 参数 | 说明 |
|------|------|
| `--headless` | 无头模式，不启动 Web UI，直接运行 |
| `-u 10` | 模拟 10 个并发用户 |
| `-r 2` | 每秒孵化 2 个用户 |
| `-t 30s` | 测试持续 30 秒 |
| `--html=performance/report.html` | 测试结束后自动生成 HTML 报告 |

### 其他常用参数

```bash
# CSV 格式输出（适合后续分析）
locust -f performance/locustfile.py --headless -u 20 -r 5 -t 60s --csv=performance/results

# 指定自定义 host（覆盖脚本中默认值）
locust -f performance/locustfile.py --host=http://your-server:5000

# 指定日志级别
locust -f performance/locustfile.py --loglevel=DEBUG
```

## 用户行为说明

`locustfile.py` 定义了 5 种用户行为类：

### 1. LoginBehavior（登录行为）

模拟用户登录操作。

- **接口**：`POST /api/login`
- **说明**：使用 `standard_user / secret_sauce` 凭据进行登录，成功后将 Token 存储到 `self.token` 并设置到请求头 `Authorization: Bearer <token>`。
- **WebsiteUser 权重**：1

### 2. BrowseBehavior（浏览行为）

模拟已登录用户浏览商品。

- `on_start`：自动执行登录获取 Token
- `browse_products`（权重 3）：`GET /api/products?page=1&size=10`，获取商品列表第一页
- `view_product`（权重 2）：`GET /api/products/{random_id}`，随机查看一个商品详情
- `view_cart`（权重 1）：`GET /api/cart`，查看购物车
- **WebsiteUser 权重**：3（最高权重，模拟大部分用户以浏览为主）

### 3. CartBehavior（购物车行为）

模拟已登录用户的购物车操作。

- `on_start`：自动执行登录获取 Token，重置购物车状态
- `add_to_cart`（权重 2）：`POST /api/cart`，添加商品（product_id=1, quantity=1）到购物车
- `view_cart`（权重 1）：`GET /api/cart`，查看购物车
- `remove_from_cart`（权重 1）：`DELETE /api/cart/1`，从购物车中删除商品，并清除购物车状态
- **WebsiteUser 权重**：2

### 4. CheckoutBehavior（结算行为）

模拟已登录用户的下单结算流程。

- `on_start`：自动执行登录，并向购物车中预添加一个商品
- `create_order`（权重 1）：`POST /api/orders`，提交订单
- `view_orders`（权重 1）：`GET /api/orders`，查看订单列表
- **WebsiteUser 权重**：1

### 5. WebsiteUser（聚合用户）

这是 Locust 的主入口类，按权重随机分配上述 4 种行为：

| 行为 | 权重 | 说明 |
|------|------|------|
| BrowseBehavior | 3 | 浏览商品（最常见） |
| CartBehavior | 2 | 购物车操作 |
| CheckoutBehavior | 1 | 结算下单 |
| LoginBehavior | 1 | 独立登录 |

所有用户在请求之间会等待 1~3 秒（`between(1, 3)`），模拟真实用户的思考时间。

## 如何阅读报告

### HTML 报告

使用 `--html` 参数生成的报告包含以下关键指标：

- **Requests**：总请求数、失败数、失败率
- **Median Response Time**：中位数响应时间（ms），反映典型用户体验
- **Average Response Time**：平均响应时间（ms）
- **Min / Max Response Time**：最小/最大响应时间（ms）
- **Requests/sec (RPS)**：每秒处理的请求数，衡量系统吞吐量
- **Percentiles (p50, p95, p99)**：响应时间百分位数，关注 p95 和 p99 能发现长尾延迟
- **Failure count**：失败请求数，失败率应接近 0

### 关注要点

1. **p95 / p99 响应时间**：如果远高于中位数，说明存在部分慢请求，需要排查
2. **失败率**：任何非零失败率都值得关注，可能是服务端过载或接口异常
3. **RPS 趋势**：随着用户增加，RPS 应线性增长；如果增长停滞，说明系统达到瓶颈
4. **错误类型**：报告会列出具体的错误响应码（如 500、502），有助于定位问题
