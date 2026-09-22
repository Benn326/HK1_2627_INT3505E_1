# Audit GitHub REST API

**1. GET /users/{username}**
- **Method & Status Code:** `GET` | `200 OK` (Thành công), `404 Not Found` (Không thấy user).
- **Headers chính:** `Accept: application/vnd.github+json`, `ETag`.
- **Đánh giá RESTful:** Có. Thỏa mãn Uniform Interface, method GET an toàn (safe) và idempotent. Dùng URL phân cấp danh từ chuẩn.

**2. POST /user/repos**
- **Method & Status Code:** `POST` | `201 Created` (Tạo thành công).
- **Headers chính:** `Authorization: Bearer <token>`, `Location: <url_repo_moi>`.
- **Đánh giá RESTful:** Có. Trả về đúng mã 201 và header `Location` trỏ đến tài nguyên vừa tạo theo chuẩn REST.

**3. PATCH /repos/{owner}/{repo}**
- **Method & Status Code:** `PATCH` | `200 OK`.
- **Headers chính:** `Content-Type: application/json`.
- **Đánh giá RESTful:** Có. Dùng PATCH đúng nghĩa vụ là cập nhật một phần thông tin của repository (như đổi tên, mô tả).

**4. DELETE /repos/{owner}/{repo}**
- **Method & Status Code:** `DELETE` | `204 No Content`.
- **Headers chính:** `Authorization: Bearer <token>`.
- **Đánh giá RESTful:** Có. Trả về mã 204 không có body, method mang tính idempotent (xóa nhiều lần kết quả trạng thái server vẫn thế).

**5. GET /rate_limit**
- **Method & Status Code:** `GET` | `200 OK`.
- **Headers chính:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`.
- **Đánh giá RESTful:** Có vi phạm nhẹ. `rate_limit` mang tính chất RPC (gọi hàm kiểm tra) hơn là một "tài nguyên" vật lý. Tuy nhiên, GitHub dùng nó để cung cấp siêu dữ liệu nên có thể chấp nhận.