from sqlalchemy.orm import selectinload

from product_api.extensions import db
from product_api.models import Order, OrderItem


def _seed_products(client, count: int) -> list[dict]:
    products = []
    for i in range(1, count + 1):
        resp = client.post(
            "/api/v1/products",
            json={
                "sku": f"SKU-{i:03d}",
                "name": f"Product {i}",
                "price_cents": i * 10000,
                "qty_in_stock": 50,
            },
        )
        assert resp.status_code == 201
        products.append(resp.get_json())
    return products


def test_post_create_order_with_multiple_products(app, client):
    products = _seed_products(client, 3)

    resp = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"product_id": products[0]["id"], "quantity": 2},
                {"product_id": products[1]["id"], "quantity": 5},
            ]
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == 1
    assert data["status"] == "pending"
    assert len(data["items"]) == 2
    assert data["items"][0]["product_id"] == products[0]["id"]
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["unit_price_cents"] == 10000
    assert data["items"][0]["product"]["sku"] == "SKU-001"
    assert data["items"][1]["product_id"] == products[1]["id"]
    assert data["items"][1]["quantity"] == 5
    assert data["items"][1]["unit_price_cents"] == 20000

    with app.app_context():
        saved_order = db.session.get(Order, data["id"])
        assert saved_order is not None
        assert len(saved_order.items) == 2


def test_post_create_order_validation_and_missing_product_atomic(app, client):
    products = _seed_products(client, 1)

    bad_qty_resp = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": products[0]["id"], "quantity": 0}]},
    )
    assert bad_qty_resp.status_code == 422
    assert bad_qty_resp.get_json()["error"] == "validation_error"

    missing_prod_resp = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"product_id": products[0]["id"], "quantity": 2},
                {"product_id": 9999, "quantity": 1},
            ]
        },
    )
    assert missing_prod_resp.status_code == 404
    assert missing_prod_resp.get_json()["error"] == "not_found"

    with app.app_context():
        order_count = db.session.scalar(db.select(db.func.count()).select_from(Order))
        item_count = db.session.scalar(db.select(db.func.count()).select_from(OrderItem))
        assert order_count == 0
        assert item_count == 0


def test_get_order_detail_eager_loading_prevents_n_plus_1(app, client, query_counter):
    products = _seed_products(client, 20)

    small_order = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"product_id": p["id"], "quantity": 1} for p in products[:2]
            ]
        },
    ).get_json()

    large_order = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"product_id": p["id"], "quantity": 2} for p in products[:20]
            ]
        },
    ).get_json()

    with app.app_context():
        db.session.remove()
        with query_counter() as small_counter:
            res_small = client.get(f"/api/v1/orders/{small_order['id']}")

        db.session.remove()
        with query_counter() as large_counter:
            res_large = client.get(f"/api/v1/orders/{large_order['id']}")

    assert res_small.status_code == 200
    assert res_large.status_code == 200
    assert len(res_small.get_json()["items"]) == 2
    assert len(res_large.get_json()["items"]) == 20

    assert small_counter.count == large_counter.count
    assert large_counter.count <= 4


def test_list_orders_eager_loading_constant_query_count(app, client, query_counter):
    products = _seed_products(client, 6)

    for _ in range(2):
        client.post(
            "/api/v1/orders",
            json={"items": [{"product_id": p["id"], "quantity": 1} for p in products[:3]]},
        )

    with app.app_context():
        db.session.remove()
        with query_counter() as counter_2_orders:
            res_2 = client.get("/api/v1/orders")

    for _ in range(10):
        client.post(
            "/api/v1/orders",
            json={"items": [{"product_id": p["id"], "quantity": 2} for p in products]},
        )

    with app.app_context():
        db.session.remove()
        with query_counter() as counter_12_orders:
            res_12 = client.get("/api/v1/orders")

    assert res_2.status_code == 200
    assert res_12.status_code == 200
    assert res_2.get_json()["total"] == 2
    assert res_12.get_json()["total"] == 12

    assert counter_2_orders.count == counter_12_orders.count
    assert counter_12_orders.count <= 5


def test_demonstrate_lazy_vs_eager_loading_query_count(app, client, query_counter):
    products = _seed_products(client, 10)
    for i in range(10):
        client.post(
            "/api/v1/orders",
            json={"items": [{"product_id": products[i]["id"], "quantity": 1}]},
        )

    with app.app_context():
        db.session.remove()
        with query_counter() as lazy_counter:
            orders_lazy = db.session.execute(db.select(Order)).scalars().all()
            for o in orders_lazy:
                for item in o.items:
                    _ = item.product.sku

        db.session.remove()
        with query_counter() as eager_counter:
            stmt = db.select(Order).options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
            orders_eager = db.session.execute(stmt).scalars().all()
            for o in orders_eager:
                for item in o.items:
                    _ = item.product.sku

    assert eager_counter.count == 3
    assert lazy_counter.count > eager_counter.count
    assert lazy_counter.count >= 21
