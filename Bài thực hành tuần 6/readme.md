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


