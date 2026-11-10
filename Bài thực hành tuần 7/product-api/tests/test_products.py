def test_create_and_get_product(client):
    resp = client.post(
        "/api/v1/products",
        json={
            "sku": "SP-TEST-01",
            "name": "Mechanical Keyboard",
            "description": "RGB Keyboard",
            "price_cents": 350000,
            "qty_in_stock": 10,
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == 1
    assert data["sku"] == "SP-TEST-01"
    assert data["price_cents"] == 350000
    assert data["qty_in_stock"] == 10
    assert data["archived"] is False

    get_resp = client.get(f"/api/v1/products/{data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["sku"] == "SP-TEST-01"


def test_create_product_duplicate_sku_returns_409(client):
    payload = {
        "sku": "SP-DUP-01",
        "name": "Mouse",
        "price_cents": 150000,
        "qty_in_stock": 5,
    }
    first = client.post("/api/v1/products", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/products", json=payload)
    assert second.status_code == 409
    assert second.get_json()["error"] == "conflict"


def test_reserve_patch_and_soft_delete_product(client):
    created = client.post(
        "/api/v1/products",
        json={"sku": "SP-RES-01", "name": "Monitor", "price_cents": 2000000, "qty_in_stock": 5},
    ).get_json()
    pid = created["id"]

    res_ok = client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 2})
    assert res_ok.status_code == 200
    assert res_ok.get_json()["qty_in_stock"] == 3

    res_fail = client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 10})
    assert res_fail.status_code == 409
    assert res_fail.get_json()["error"] == "out_of_stock"

    patched = client.patch(f"/api/v1/products/{pid}", json={"price_cents": 1800000})
    assert patched.status_code == 200
    assert patched.get_json()["price_cents"] == 1800000

    deleted = client.delete(f"/api/v1/products/{pid}")
    assert deleted.status_code == 204

    not_found = client.get(f"/api/v1/products/{pid}")
    assert not_found.status_code == 404
