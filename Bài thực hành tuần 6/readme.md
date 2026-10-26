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
---

# Lab_03:
## Stateless JWT & refresh token:
### 1. Gọi /api/orders khi chưa đăng nhập (401 unauthorized)

```bash
curl -i http://localhost:5000/api/orders
```

response:

```json
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 18:19:59 GMT
Content-Type: application/json
Content-Length: 85
Connection: close

{
  "error": "authorization_required",
  "message": "Missing Authorization Header"
}
```
---

### 2. Đăng nhập để nhận token: access và refresh (200 ok)

```bash
curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"an@vnu.edu.vn\", \"password\": \"secret123\"}"
```

Server trả về 200 OK chứa cặp token:

response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 18:20:11 GMT
Content-Type: application/json
Content-Length: 862
Connection: close

{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgxMSwianRpIjoiM2U4ZmE2MDgtNmI3OS00MDlhLWFhMmItY2U3NGJiODA2NDIwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3OTMwMzg4MTEsImNzcmYiOiIxOWI3NzUxNy1jYjBiLTQ2MmYtOTExNS1hZDIzNDBiMGRhZTkiLCJleHAiOjE3OTMwMzk3MTEsInJvbGVzIjpbImN1c3RvbWVyIl0sInNjb3BlcyI6WyJvcmRlcnM6cmVhZCJdfQ.TepI5_8XXeaBZtIgTyPya6bcOAt7ygM5kByUwrrnUC4",
  "expires_in_minutes": 15,
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgxMSwianRpIjoiZGM3ZDY5ZTEtNzUwYi00M2U0LThiZGUtYjA4ZTQ4NGRkNmFiIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxIiwibmJmIjoxNzkzMDM4ODExLCJjc3JmIjoiOGU2MTc4YWYtZTJjMC00Y2VjLTliOTktOWU3M2EwYjk5ZjI1IiwiZXhwIjoxNzk1NjMwODExLCJyb2xlcyI6WyJjdXN0b21lciJdLCJzY29wZXMiOlsib3JkZXJzOnJlYWQiXX0.23AOEc20t6noqQnmh-1GGR7opEYbI85uQI94sjkf6z0",
  "status": "success"
}
```

*(Copy chuỗi access và refresh vừa nhận được để dùng cho các bước dưới).*

---

### 3. Dùng Access Token gọi API đọc đơn hàng (200 ok)

*(Thay chuỗi access của bạn vào sau chữ Bearer)*:

```bash
curl -i http://localhost:5000/api/orders \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgxMSwianRpIjoiM2U4ZmE2MDgtNmI3OS00MDlhLWFhMmItY2U3NGJiODA2NDIwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3OTMwMzg4MTEsImNzcmYiOiIxOWI3NzUxNy1jYjBiLTQ2MmYtOTExNS1hZDIzNDBiMGRhZTkiLCJleHAiOjE3OTMwMzk3MTEsInJvbGVzIjpbImN1c3RvbWVyIl0sInNjb3BlcyI6WyJvcmRlcnM6cmVhZCJdfQ.TepI5_8XXeaBZtIgTyPya6bcOAt7ygM5kByUwrrnUC4"
```

response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 18:20:19 GMT
Content-Type: application/json
Content-Length: 186
Connection: close

{
  "granted_scopes": [
    "orders:read"
  ],
  "orders": [
    {
      "order_id": "ORD-001",
      "status": "completed",
      "total_vnd": 450000
    }
  ],
  "principal_id": "1"
}
```

---

### 4. Đổi Refresh Token lấy Access Token mới (200 ok)

*(Dùng chuỗi refresh nhận được ở Bước 2)*:

```bash
curl -i -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgxMSwianRpIjoiZGM3ZDY5ZTEtNzUwYi00M2U0LThiZGUtYjA4ZTQ4NGRkNmFiIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxIiwibmJmIjoxNzkzMDM4ODExLCJjc3JmIjoiOGU2MTc4YWYtZTJjMC00Y2VjLTliOTktOWU3M2EwYjk5ZjI1IiwiZXhwIjoxNzk1NjMwODExLCJyb2xlcyI6WyJjdXN0b21lciJdLCJzY29wZXMiOlsib3JkZXJzOnJlYWQiXX0.23AOEc20t6noqQnmh-1GGR7opEYbI85uQI94sjkf6z0"
```

response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 18:20:26 GMT
Content-Type: application/json
Content-Length: 406
Connection: close

{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgyNiwianRpIjoiNjRiMWU5NjctNTkyMy00M2YyLWIxYzYtMDhlY2E5MzNmZTM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3OTMwMzg4MjYsImNzcmYiOiIzN2YyMmJjNy0xYWYzLTQyY2UtYjJkZS00YmYyNjRlN2FjMjQiLCJleHAiOjE3OTMwMzk3MjYsInJvbGVzIjpbImN1c3RvbWVyIl0sInNjb3BlcyI6WyJvcmRlcnM6cmVhZCJdfQ.vuOJ1IUC1EftvjoEg_1F8iGo_dzD7Vcc-v_ikEFUJoI"
}
```

---

### 5. Đăng xuất (Logout) và kiểm tra thu hồi token
Lần 1:
```bash
curl -i -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgxMSwianRpIjoiM2U4ZmE2MDgtNmI3OS00MDlhLWFhMmItY2U3NGJiODA2NDIwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3OTMwMzg4MTEsImNzcmYiOiIxOWI3NzUxNy1jYjBiLTQ2MmYtOTExNS1hZDIzNDBiMGRhZTkiLCJleHAiOjE3OTMwMzk3MTEsInJvbGVzIjpbImN1c3RvbWVyIl0sInNjb3BlcyI6WyJvcmRlcnM6cmVhZCJdfQ.TepI5_8XXeaBZtIgTyPya6bcOAt7ygM5kByUwrrnUC4"
```

response:

```json
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 18:20:34 GMT
Content-Type: application/json
Content-Length: 103
Connection: close

{
  "message": "Đăng xuất thành công, token đã bị vô hiệu hóa.",
  "status": "success"
}
```

Lần 2: gọi lại `/api/orders`:

```bash
curl -i http://localhost:5000/api/orders \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5MzAzODgxMSwianRpIjoiM2U4ZmE2MDgtNmI3OS00MDlhLWFhMmItY2U3NGJiODA2NDIwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3OTMwMzg4MTEsImNzcmYiOiIxOWI3NzUxNy1jYjBiLTQ2MmYtOTExNS1hZDIzNDBiMGRhZTkiLCJleHAiOjE3OTMwMzk3MTEsInJvbGVzIjpbImN1c3RvbWVyIl0sInNjb3BlcyI6WyJvcmRlcnM6cmVhZCJdfQ.TepI5_8XXeaBZtIgTyPya6bcOAt7ygM5kByUwrrnUC4"
```

Kết quả bị từ chối (401 Unauthorized):

```json
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.3 Python/3.13.9
Date: Mon, 26 Oct 2026 18:20:39 GMT
Content-Type: application/json
Content-Length: 95
Connection: close

{
  "error": "token_revoked",
  "message": "Token này đã bị thu hồi/vô hiệu hóa."
}
```
