import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import allure
import pytest
from app.models import (
    init_db,
    get_user,
    save_token,
    get_token_user,
    delete_token,
    list_products,
    get_product,
    get_cart,
    add_to_cart,
    remove_from_cart,
    clear_cart,
    create_order,
    add_order_item,
    get_order,
    list_orders,
    get_db,
)

# ============================================================
# 模块级初始化：确保数据库表结构和种子数据就绪
# ============================================================
init_db()


# ============================================================
# 用户表测试
# ============================================================
@allure.feature("数据库测试")
class TestUserDB:
    @allure.story("用户查询")
    @allure.title("获取已存在的用户信息")
    def test_get_existing_user(self):
        user = get_user("standard_user")
        assert user is not None
        assert user["username"] == "standard_user"
        assert user["password"] == "secret_sauce"
        assert user["locked"] is False

    @allure.story("用户查询")
    @allure.title("获取不存在的用户应返回None")
    def test_get_non_existing_user(self):
        user = get_user("ghost_user")
        assert user is None

    @allure.story("用户查询")
    @allure.title("验证locked_out_user账户被锁定")
    def test_locked_user_status(self):
        user = get_user("locked_out_user")
        assert user is not None
        assert user["username"] == "locked_out_user"
        assert user["locked"] is True

    @allure.story("用户查询")
    @allure.title("验证order_test_user账户未锁定")
    def test_order_test_user_not_locked(self):
        user = get_user("order_test_user")
        assert user is not None
        assert user["locked"] is False

    @allure.story("用户查询")
    @allure.title("验证cart_test_user账户未锁定")
    def test_cart_test_user_not_locked(self):
        user = get_user("cart_test_user")
        assert user is not None
        assert user["locked"] is False

    @allure.story("用户查询")
    @allure.title("验证用户密码字段正确性")
    def test_user_password_field(self):
        user = get_user("standard_user")
        assert user is not None
        assert isinstance(user["password"], str)
        assert len(user["password"]) > 0


# ============================================================
# Token 管理测试
# ============================================================
@allure.feature("数据库测试")
class TestTokenDB:
    @allure.story("Token存储")
    @allure.title("保存Token并验证可查询")
    def test_save_and_get_token(self):
        test_token = "test_token_save_abc123"
        save_token(test_token, "standard_user")
        username = get_token_user(test_token)
        assert username == "standard_user"

    @allure.story("Token存储")
    @allure.title("保存Token应支持覆盖更新")
    def test_save_token_overwrite(self):
        test_token = "test_token_overwrite_xyz"
        save_token(test_token, "standard_user")
        save_token(test_token, "order_test_user")
        username = get_token_user(test_token)
        assert username == "order_test_user"

    @allure.story("Token查询")
    @allure.title("查询不存在的Token应返回None")
    def test_get_non_existing_token(self):
        username = get_token_user("nonexistent_token_999")
        assert username is None

    @allure.story("Token删除")
    @allure.title("删除Token后查询应返回None")
    def test_delete_token(self):
        test_token = "test_token_del_456"
        save_token(test_token, "cart_test_user")
        # 确认保存成功
        assert get_token_user(test_token) == "cart_test_user"
        # 删除
        delete_token(test_token)
        # 确认已删除
        assert get_token_user(test_token) is None

    @allure.story("Token删除")
    @allure.title("删除不存在的Token不应抛出异常")
    def test_delete_non_existing_token(self):
        # 删除一个从未保存的 token，不应报错
        delete_token("token_never_exists_000")
        assert get_token_user("token_never_exists_000") is None

    @allure.story("Token存储")
    @allure.title("为不同用户保存独立Token互不干扰")
    def test_multiple_tokens_independent(self):
        token_a = "multi_token_user_a"
        token_b = "multi_token_user_b"
        save_token(token_a, "standard_user")
        save_token(token_b, "locked_out_user")
        assert get_token_user(token_a) == "standard_user"
        assert get_token_user(token_b) == "locked_out_user"


# ============================================================
# 商品查询测试
# ============================================================
@allure.feature("数据库测试")
class TestProductDB:
    @allure.story("商品列表")
    @allure.title("列出全部商品应返回6条记录")
    def test_list_all_products(self):
        products = list_products()
        assert isinstance(products, list)
        assert len(products) == 6

    @allure.story("商品列表")
    @allure.title("商品列表每条记录应包含必要字段")
    def test_list_products_fields(self):
        products = list_products()
        required_keys = {"id", "name", "price", "stock"}
        for product in products:
            assert set(product.keys()) == required_keys

    @allure.story("商品查询")
    @allure.title("根据ID获取单个商品")
    def test_get_product_by_id(self):
        product = get_product(1)
        assert product is not None
        assert product["id"] == 1
        assert product["name"] == "Sauce Labs Backpack"
        assert product["price"] == 29.99
        assert product["stock"] == 10

    @allure.story("商品查询")
    @allure.title("根据ID获取库存为0的商品")
    def test_get_out_of_stock_product(self):
        product = get_product(5)
        assert product is not None
        assert product["name"] == "Sauce Labs Onesie"
        assert product["stock"] == 0

    @allure.story("商品查询")
    @allure.title("获取不存在的商品应返回None")
    def test_get_non_existing_product(self):
        product = get_product(9999)
        assert product is None

    @allure.story("商品列表")
    @allure.title("验证种子数据中商品价格均为正数")
    def test_products_price_positive(self):
        products = list_products()
        for product in products:
            assert product["price"] > 0

    @allure.story("商品列表")
    @allure.title("验证种子数据中商品库存均为非负整数")
    def test_products_stock_non_negative(self):
        products = list_products()
        for product in products:
            assert isinstance(product["stock"], int)
            assert product["stock"] >= 0


# ============================================================
# 购物车操作测试
# ============================================================
@allure.feature("数据库测试")
class TestCartDB:
    @allure.story("添加购物车")
    @allure.title("添加商品到购物车")
    def test_add_item_to_cart(self):
        add_to_cart("cart_test_user", 1, "Sauce Labs Backpack", 29.99, 2)
        cart = get_cart("cart_test_user")
        item = next((i for i in cart if i["product_id"] == 1), None)
        assert item is not None
        assert item["name"] == "Sauce Labs Backpack"
        assert item["price"] == 29.99
        assert item["quantity"] == 2

    @allure.story("添加购物车")
    @allure.title("添加相同商品应累加数量而非重复插入")
    def test_add_duplicate_increments_quantity(self):
        add_to_cart("cart_test_user", 3, "Sauce Labs Bolt T-Shirt", 15.99, 1)
        add_to_cart("cart_test_user", 3, "Sauce Labs Bolt T-Shirt", 15.99, 2)
        cart = get_cart("cart_test_user")
        matching = [i for i in cart if i["product_id"] == 3]
        assert len(matching) == 1
        assert matching[0]["quantity"] == 3

    @allure.story("查看购物车")
    @allure.title("查询购物车应返回所有已添加商品")
    def test_get_cart_contents(self):
        add_to_cart("cart_test_user", 2, "Sauce Labs Bike Light", 9.99, 1)
        add_to_cart("cart_test_user", 4, "Sauce Labs Fleece Jacket", 49.99, 1)
        cart = get_cart("cart_test_user")
        product_ids = [i["product_id"] for i in cart]
        assert 2 in product_ids
        assert 4 in product_ids

    @allure.story("删除购物车商品")
    @allure.title("从购物车中移除商品")
    def test_remove_item_from_cart(self):
        add_to_cart("cart_test_user", 6, "Test.allTheThings() T-Shirt", 15.99, 1)
        removed = remove_from_cart("cart_test_user", 6)
        assert removed is True
        cart = get_cart("cart_test_user")
        product_ids = [i["product_id"] for i in cart]
        assert 6 not in product_ids

    @allure.story("删除购物车商品")
    @allure.title("移除购物车中不存在的商品应返回False")
    def test_remove_non_existing_cart_item(self):
        # 确保该商品不在购物车中（conftest已清理）
        removed = remove_from_cart("cart_test_user", 9999)
        assert removed is False

    @allure.story("清空购物车")
    @allure.title("清空购物车后应无任何商品")
    def test_clear_cart(self):
        add_to_cart("cart_test_user", 1, "Sauce Labs Backpack", 29.99, 1)
        add_to_cart("cart_test_user", 2, "Sauce Labs Bike Light", 9.99, 1)
        clear_cart("cart_test_user")
        cart = get_cart("cart_test_user")
        assert cart == []

    @allure.story("清空购物车")
    @allure.title("清空空购物车不应报错")
    def test_clear_empty_cart(self):
        # conftest 已清空，再次清空不应报错
        clear_cart("cart_test_user")
        cart = get_cart("cart_test_user")
        assert cart == []

    @allure.story("添加购物车")
    @allure.title("不同用户的购物车互不干扰")
    def test_cart_isolation_between_users(self):
        add_to_cart("cart_test_user", 1, "Sauce Labs Backpack", 29.99, 1)
        add_to_cart("order_test_user", 2, "Sauce Labs Bike Light", 9.99, 1)
        cart_a = get_cart("cart_test_user")
        cart_b = get_cart("order_test_user")
        ids_a = [i["product_id"] for i in cart_a]
        ids_b = [i["product_id"] for i in cart_b]
        assert 1 in ids_a
        assert 1 not in ids_b
        assert 2 in ids_b
        assert 2 not in ids_a


# ============================================================
# 订单操作测试
# ============================================================
@allure.feature("数据库测试")
class TestOrderDB:
    @allure.story("创建订单")
    @allure.title("创建订单应返回有效的order_id")
    def test_create_order(self):
        order_id = create_order("order_test_user", 59.98)
        assert isinstance(order_id, int)
        assert order_id > 0

    @allure.story("创建订单")
    @allure.title("创建订单时默认状态应为created")
    def test_create_order_default_status(self):
        order_id = create_order("order_test_user", 29.99)
        order = get_order(order_id, "order_test_user")
        assert order is not None
        assert order["status"] == "created"

    @allure.story("添加订单项")
    @allure.title("为订单添加商品明细")
    def test_add_order_item(self):
        order_id = create_order("order_test_user", 29.99)
        add_order_item(order_id, 1, "Sauce Labs Backpack", 29.99, 1)
        order = get_order(order_id, "order_test_user")
        assert len(order["items"]) == 1
        item = order["items"][0]
        assert item["product_id"] == 1
        assert item["name"] == "Sauce Labs Backpack"
        assert item["price"] == 29.99
        assert item["quantity"] == 1

    @allure.story("添加订单项")
    @allure.title("为同一订单添加多个商品明细")
    def test_add_multiple_order_items(self):
        order_id = create_order("order_test_user", 65.97)
        add_order_item(order_id, 1, "Sauce Labs Backpack", 29.99, 1)
        add_order_item(order_id, 2, "Sauce Labs Bike Light", 9.99, 1)
        add_order_item(order_id, 4, "Sauce Labs Fleece Jacket", 49.99, 1)
        # 注意：这里的 total_price 是创建时传入的，不一定等于明细之和
        order = get_order(order_id, "order_test_user")
        assert len(order["items"]) == 3

    @allure.story("查询订单")
    @allure.title("根据ID和用户名获取订单详情")
    def test_get_order(self):
        order_id = create_order("order_test_user", 9.99)
        add_order_item(order_id, 2, "Sauce Labs Bike Light", 9.99, 1)
        order = get_order(order_id, "order_test_user")
        assert order is not None
        assert order["order_id"] == order_id
        assert order["username"] == "order_test_user"
        assert order["total_price"] == 9.99
        assert order["status"] == "created"
        assert "created_at" in order
        assert len(order["items"]) == 1

    @allure.story("查询订单")
    @allure.title("使用错误用户名获取订单应返回None")
    def test_get_order_with_wrong_user(self):
        order_id = create_order("order_test_user", 15.99)
        order = get_order(order_id, "standard_user")
        assert order is None

    @allure.story("查询订单")
    @allure.title("获取不存在的订单应返回None")
    def test_get_non_existing_order(self):
        order = get_order(999999, "order_test_user")
        assert order is None

    @allure.story("订单列表")
    @allure.title("列出用户全部订单")
    def test_list_orders(self):
        create_order("order_test_user", 10.00)
        create_order("order_test_user", 20.00)
        orders = list_orders("order_test_user")
        assert isinstance(orders, list)
        assert len(orders) >= 2
        # 验证每条订单包含必要字段
        required_keys = {"order_id", "username", "total_price", "status", "created_at"}
        for order in orders:
            assert set(order.keys()) == required_keys

    @allure.story("订单列表")
    @allure.title("订单列表应按order_id降序排列")
    def test_list_orders_descending(self):
        id_1 = create_order("order_test_user", 5.00)
        id_2 = create_order("order_test_user", 10.00)
        orders = list_orders("order_test_user")
        order_ids = [o["order_id"] for o in orders]
        # 降序排列意味着较大的 id 出现在前面
        if id_2 in order_ids and id_1 in order_ids:
            assert order_ids.index(id_2) < order_ids.index(id_1)

    @allure.story("订单列表")
    @allure.title("不同用户的订单列表互不干扰")
    def test_list_orders_isolation(self):
        # 使用 get_db 手动确认 cart_test_user 的订单已被 conftest 清理
        # 然后创建各自独立的订单
        order_id_a = create_order("order_test_user", 1.00)
        order_id_b = create_order("cart_test_user", 2.00)
        orders_a = list_orders("order_test_user")
        orders_b = list_orders("cart_test_user")
        # 验证各自列表中包含自己的订单
        assert any(o["order_id"] == order_id_a for o in orders_a)
        assert any(o["order_id"] == order_id_b for o in orders_b)
        # 验证 order_test_user 的列表中不包含 cart_test_user 的订单
        a_ids = {o["order_id"] for o in orders_a}
        b_ids = {o["order_id"] for o in orders_b}
        assert order_id_b not in a_ids
        assert order_id_a not in b_ids


# ============================================================
# 数据完整性测试
# ============================================================
@allure.feature("数据库测试")
class TestDataIntegrity:
    @allure.story("购物车总价计算")
    @allure.title("验证购物车商品总价计算正确")
    def test_cart_total_price_calculation(self):
        clear_cart("cart_test_user")
        add_to_cart("cart_test_user", 1, "Sauce Labs Backpack", 29.99, 2)
        add_to_cart("cart_test_user", 2, "Sauce Labs Bike Light", 9.99, 3)
        cart = get_cart("cart_test_user")
        total = sum(item["price"] * item["quantity"] for item in cart)
        # 29.99 * 2 + 9.99 * 3 = 59.98 + 29.97 = 89.95
        assert total == pytest.approx(89.95, abs=0.01)

    @allure.story("订单明细数量")
    @allure.title("验证订单包含正确数量的明细项")
    def test_order_item_count(self):
        order_id = create_order("order_test_user", 105.96)
        add_order_item(order_id, 1, "Sauce Labs Backpack", 29.99, 2)
        add_order_item(order_id, 4, "Sauce Labs Fleece Jacket", 49.99, 1)
        order = get_order(order_id, "order_test_user")
        assert len(order["items"]) == 2
        # 验证明细数量字段
        quantities = [item["quantity"] for item in order["items"]]
        assert sum(quantities) == 3

    @allure.story("数据一致性")
    @allure.title("验证商品数据与数据库种子数据一致")
    def test_product_seed_data_consistency(self):
        products = list_products()
        expected = {
            1: ("Sauce Labs Backpack", 29.99),
            2: ("Sauce Labs Bike Light", 9.99),
            3: ("Sauce Labs Bolt T-Shirt", 15.99),
            4: ("Sauce Labs Fleece Jacket", 49.99),
            5: ("Sauce Labs Onesie", 7.99),
            6: ("Test.allTheThings() T-Shirt", 15.99),
        }
        for product in products:
            pid = product["id"]
            assert pid in expected, f"未预期的商品ID: {pid}"
            assert product["name"] == expected[pid][0]
            assert product["price"] == expected[pid][1]

    @allure.story("数据一致性")
    @allure.title("验证用户种子数据条目完整")
    def test_user_seed_data_completeness(self):
        expected_users = ["standard_user", "locked_out_user", "order_test_user", "cart_test_user"]
        for username in expected_users:
            user = get_user(username)
            assert user is not None, f"种子用户 {username} 不存在"
            assert user["password"] == "secret_sauce", f"用户 {username} 密码不正确"

    @allure.story("购物车唯一约束")
    @allure.title("购物车中同一用户同一商品只能有一条记录")
    def test_cart_unique_constraint(self):
        clear_cart("cart_test_user")
        add_to_cart("cart_test_user", 1, "Sauce Labs Backpack", 29.99, 1)
        add_to_cart("cart_test_user", 1, "Sauce Labs Backpack", 29.99, 1)
        cart = get_cart("cart_test_user")
        matching = [i for i in cart if i["product_id"] == 1]
        assert len(matching) == 1
        assert matching[0]["quantity"] == 2
