# Lab_01:

## Http basic auth:

### 1. ko có mk tk (401-unauthorized)


```Bash
curl -i http://localhost:5000/api/orders
```

Response:

```json
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:08:47 GMT
Content-Type: application/json
Content-Length: 124
WWW-Authenticate: Basic realm="orders"
Connection: close

{
  "error": "unauthorized",
  "message": "Thông tin xác thực HTTP Basic Auth không hợp lệ hoặc bị thiếu."
}
```
---

### 2. Sai mk, tk (401 unauthorized)

```bash
curl -i -u an@vnu.edu.vn:wrongpassword http://localhost:5000/api/orders
```

response:

```json
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:12:56 GMT
Content-Type: application/json
Content-Length: 124
WWW-Authenticate: Basic realm="orders"
Connection: close

{
  "error": "unauthorized",
  "message": "Thông tin xác thực HTTP Basic Auth không hợp lệ hoặc bị thiếu."
}
```
---

### 3. Login an@vnu.edu.vn (200-Ok)

```bash
curl -i -u "an@vnu.edu.vn:correct horse battery staple" http://localhost:5000/api/orders
```

response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:15:36 GMT
Content-Type: application/json
Content-Length: 268
Connection: close

{
  "orders": [
    {
      "order_id": "ORD-001",
      "status": "completed",
      "total_vnd": 450000
    },
    {
      "order_id": "ORD-002",
      "status": "processing",
      "total_vnd": 320000
    }
  ],
  "principal": "an@vnu.edu.vn",
  "total_items": 2
}
```
---

### 4. login ben@vnu.edu.vn (200-ok)

```bash
curl -i -u ben@vnu.edu.vn:secret123 http://localhost:5000/api/orders
```

response

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:16:46 GMT
Content-Type: application/json
Content-Length: 169
Connection: close

{
  "orders": [
    {
      "order_id": "ORD-003",
      "status": "shipped",
      "total_vnd": 180000
    }
  ],
  "principal": "ben@vnu.edu.vn",
  "total_items": 1
}
```
# lab_02: 
## API Key authentication & verification:
### 1. Ko gửi header X-Api-Key (401 unauthorized)

```bash
curl -i http://localhost:5000/api/reports
```

response:

```json
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:22:34 GMT
Content-Type: application/json
Content-Length: 75
Connection: close

{
  "error": "missing_api_key",
  "message": "Header X-Api-Key bi thieu"
}
```
---

### 2. Gửi key ko tồn tại or sai giá trị (401 unauthorized):
```bash
curl -i http://localhost:5000/api/reports -H "X-Api-Key: ădnasidnj"
```

response:
```json
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:33:33 GMT
Content-Type: application/json
Content-Length: 80
Connection: close

{
  "error": "invalid_api_key",
  "message": "API key khong ton tai hoac sai"
}
```
---

### 3. Dùng Key 1 gọi endpoint /api/reports (200 ok)
```bash
curl -i http://localhost:5000/api/reports -H "X-Api-Key: sk_live_FiQXS-myxIW3GMqURUNGHMHVg26he2Oik9wCHv5-sFE_a4657558"
```

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:35:43 GMT
Content-Type: application/json
Content-Length: 171
Connection: close

{
  "caller": {
    "api_key_id": 3,
    "owner_id": 101,
    "scopes": [
      "reports:read"
    ]
  },
  "data": "Bao cao doanh thu thang nay",
  "status": "success"
}
```

---

### 4. Dùng Key 1 gọi endpoint /api/pay (403 Forbidden)
```bash
curl -i -X POST http://localhost:5000/api/pay -H "X-Api-Key: sk_live_FiQXS-myxIW3GMqURUNGHMHVg26he2Oik9wCHv5-sFE_a4657558"
```

**Thiếu payments:write -> 403 forbidden**

response

```json
HTTP/1.1 403 FORBIDDEN
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:37:28 GMT
Content-Type: application/json
Content-Length: 179
Connection: close

{
  "error": "insufficient_scope",
  "granted_scopes": [
    "reports:read"
  ],
  "message": "API key khong du quyen truy cap",
  "required_scopes": [
    "payments:write"
  ]
}
```
### 5. Dùng Key 2 gọi endpoint /api/pay (200 ok)

```bash
curl -i -X POST http://localhost:5000/api/pay -H "X-Api-Key:sk_live_Y7HzLUZQRbV3pJgrdg2ZYL_SF50Qk3OFZx171W-6FD8_9be879c9"
```

response

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 17:40:49 GMT
Content-Type: application/json
Content-Length: 95
Connection: close

{
  "message": "Thanh toan thanh cong 500 000 VND",
  "owner_id": 102,
  "status": "success"
}
```
