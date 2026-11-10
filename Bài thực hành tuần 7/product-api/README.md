# Lab 01: Product API CRUD (Flask + SQLAlchemy 2.x + Marshmallow)

## Khởi chạy ứng dụng

```bash
python -m pip install -e .
python -m flask --app wsgi db upgrade
python -m flask --app wsgi run --debug
```

---

## Kiểm tra các Endpoint bằng cURL

### 1. POST tạo sản phẩm mới (201 Created)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"sku":"SP001","name":"Keyboard","description":"Mechanical keyboard","price_cents":350000,"qty_in_stock":10}'
```

Response:

```json
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 133
Connection: close

{
  "archived": false,
  "description": "Mechanical keyboard",
  "id": 1,
  "name": "Keyboard",
  "price_cents": 350000,
  "qty_in_stock": 10,
  "sku": "SP001"
}
```

---

### 2. GET danh sách sản phẩm có phân trang (200 OK)

```bash
curl -i "http://127.0.0.1:5000/api/v1/products?page=1&size=20"
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 174
Connection: close

{
  "items": [
    {
      "archived": false,
      "description": "Mechanical keyboard",
      "id": 1,
      "name": "Keyboard",
      "price_cents": 350000,
      "qty_in_stock": 10,
      "sku": "SP001"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 1
}
```

---

### 3. GET chi tiết sản phẩm theo ID (200 OK)

```bash
curl -i http://127.0.0.1:5000/api/v1/products/1
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 133
Connection: close

{
  "archived": false,
  "description": "Mechanical keyboard",
  "id": 1,
  "name": "Keyboard",
  "price_cents": 350000,
  "qty_in_stock": 10,
  "sku": "SP001"
}
```

---

### 4. POST Reserve đặt trước sản phẩm (200 OK)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/products/1/reserve \
  -H "Content-Type: application/json" \
  -d '{"qty":2}'
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 132
Connection: close

{
  "archived": false,
  "description": "Mechanical keyboard",
  "id": 1,
  "name": "Keyboard",
  "price_cents": 350000,
  "qty_in_stock": 8,
  "sku": "SP001"
}
```

---

### 5. POST Reserve vượt tồn kho (409 Conflict)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/products/1/reserve \
  -H "Content-Type: application/json" \
  -d '{"qty":50}'
```

Response:

```json
HTTP/1.1 409 CONFLICT
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 48
Connection: close

{
  "detail": "only 8 left",
  "error": "out_of_stock"
}
```

---

### 6. PATCH cập nhật một phần sản phẩm (200 OK)

```bash
curl -i -X PATCH http://127.0.0.1:5000/api/v1/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"New Keyboard Name","price_cents":400000}'
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 141
Connection: close

{
  "archived": false,
  "description": "Mechanical keyboard",
  "id": 1,
  "name": "New Keyboard Name",
  "price_cents": 400000,
  "qty_in_stock": 8,
  "sku": "SP001"
}
```

---

### 7. DELETE xóa mềm sản phẩm — Soft Delete (204 No Content)

```bash
curl -i -X DELETE http://127.0.0.1:5000/api/v1/products/1
```

Response:

```json
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: text/html; charset=utf-8
Connection: close
```

---

### 8. GET lại sau khi xóa mềm (404 Not Found & Danh sách rỗng)

```bash
curl -i http://127.0.0.1:5000/api/v1/products/1
```

Response:

```json
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 51
Connection: close

{
  "detail": "product not found",
  "error": "not_found"
}
```

```bash
curl -i "http://127.0.0.1:5000/api/v1/products"
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 42
Connection: close

{
  "items": [],
  "page": 1,
  "size": 20,
  "total": 0
}
```

---

### 9. POST trùng SKU (409 Conflict)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"sku":"SP001","name":"Another Keyboard","price_cents":300000,"qty_in_stock":5}'
```

Response:

```json
HTTP/1.1 409 CONFLICT
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 51
Connection: close

{
  "detail": "sku already exists",
  "error": "conflict"
}
```

---

### 10. GET ID không tồn tại (404 Not Found)

```bash
curl -i http://127.0.0.1:5000/api/v1/products/9999
```

Response:

```json
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 51
Connection: close

{
  "detail": "product not found",
  "error": "not_found"
}
```

---

### 11. POST dữ liệu không hợp lệ (422 Unprocessable Entity)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"sku":"A","name":"","price_cents":-100}'
```

Response:

```json
HTTP/1.1 422 UNPROCESSABLE ENTITY
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Sat, 07 Nov 2026 06:06:28 GMT
Content-Type: application/json
Content-Length: 182
Connection: close

{
  "detail": {
    "name": [
      "Length must be between 1 and 255."
    ],
    "price_cents": [
      "Must be greater than or equal to 0."
    ],
    "sku": [
      "Length must be between 3 and 32."
    ]
  },
  "error": "validation_error"
}
```

---

## Order & OrderItem API (`/api/v1/orders`)

### 1. Tạo Order chứa nhiều Product (201 Created)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":2},{"product_id":2,"quantity":3}]}'
```

Response:

```json
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Tue, 10 Nov 2026 09:58:47 GMT
Content-Type: application/json
Content-Length: 225
Connection: close

{
  "created_at": "2026-11-10T09:58:47",
  "id": 1,
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price_cents": 350000
    },
    {
      "id": 2,
      "order_id": 1,
      "product_id": 2,
      "quantity": 3,
      "unit_price_cents": 150000
    }
  ],
  "status": "pending"
}
```

---

### 2. Lấy chi tiết Order và danh sách OrderItem (200 OK)

```bash
curl -i http://127.0.0.1:5000/api/v1/orders/1
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Tue, 10 Nov 2026 09:58:48 GMT
Content-Type: application/json
Content-Length: 225
Connection: close

{
  "created_at": "2026-11-10T09:58:47",
  "id": 1,
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price_cents": 350000
    },
    {
      "id": 2,
      "order_id": 1,
      "product_id": 2,
      "quantity": 3,
      "unit_price_cents": 150000
    }
  ],
  "status": "pending"
}
```

---

### 3. Lấy danh sách Order có phân trang (200 OK)

```bash
curl -i "http://127.0.0.1:5000/api/v1/orders?page=1&size=20"
```

Response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Tue, 10 Nov 2026 09:58:48 GMT
Content-Type: application/json
Content-Length: 266
Connection: close

{
  "items": [
    {
      "created_at": "2026-11-10T09:58:47",
      "id": 1,
      "items": [
        {
          "id": 1,
          "order_id": 1,
          "product_id": 1,
          "quantity": 2,
          "unit_price_cents": 350000
        },
        {
          "id": 2,
          "order_id": 1,
          "product_id": 2,
          "quantity": 3,
          "unit_price_cents": 150000
        }
      ],
      "status": "pending"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 1
}
```

---

### 4. Truy cập Order không tồn tại (404 Not Found)

```bash
curl -i http://127.0.0.1:5000/api/v1/orders/9999
```

Response:

```json
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Tue, 10 Nov 2026 09:58:48 GMT
Content-Type: application/json
Content-Length: 49
Connection: close

{
  "detail": "order not found",
  "error": "not_found"
}
```

---

### 5. Gửi quantity không hợp lệ (422 Unprocessable Entity)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":0}]}'
```

Response:

```json
HTTP/1.1 422 UNPROCESSABLE ENTITY
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Tue, 10 Nov 2026 09:58:48 GMT
Content-Type: application/json
Content-Length: 107
Connection: close

{
  "detail": {
    "items": {
      "0": {
        "quantity": [
          "Must be greater than or equal to 1."
        ]
      }
    }
  },
  "error": "validation_error"
}
```

---

### 6. Gửi product_id không tồn tại (404 Not Found)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":1},{"product_id":9999,"quantity":2}]}'
```

Response:

```json
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.9 Python/3.13.9
Date: Tue, 10 Nov 2026 09:58:48 GMT
Content-Type: application/json
Content-Length: 56
Connection: close

{
  "detail": "product 9999 not found",
  "error": "not_found"
}
```

---

## Triển khai với Docker & Docker Compose

### 1. Build và khởi chạy hệ thống (PostgreSQL 16 + Flask API qua Gunicorn)

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f api
```

Khi container `api` khởi chạy:
1. Chờ `db` (`postgres:16-alpine`) vượt qua `healthcheck` (`pg_isready -U app -d appdb`).
2. Tự động chạy `flask --app wsgi db upgrade` để áp dụng toàn bộ migration (`products`, `orders`, `order_items`).
3. Khởi chạy WSGI server `gunicorn --bind 0.0.0.0:5000 'product_api.factory:create_app()'` dưới quyền user không phải root (`app`).

### 2. Kiểm tra hoạt động và lưu trữ bền vững (Named Volume `pgdata`)

```bash
# Kiểm tra API
curl -i http://127.0.0.1:5000/api/v1/products
curl -i -X POST http://127.0.0.1:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"sku":"SP-DOCKER","name":"Docker Product","price_cents":200000,"qty_in_stock":15}'
curl -i http://127.0.0.1:5000/api/v1/orders

# Kiểm tra dữ liệu vẫn giữ nguyên sau khi khởi động lại container (nhờ named volume pgdata)
docker compose down
docker compose up -d
curl -i http://127.0.0.1:5000/api/v1/products
```
