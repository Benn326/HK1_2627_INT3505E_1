## 1. Xác định Resources trong miền nghiệp vụ
* **users**: Quản lý người dùng, tác giả bài viết và hệ thống theo dõi (follow).
* **posts**: Quản lý bài viết trên blog (Tài nguyên chính đang được triển khai trong source code).
* **comments**: Quản lý bình luận tương tác trên từng bài viết.
* **tags**: Quản lý các thẻ phân loại nội dung bài viết.

---

## 2. Phân loại Collection / Item / Sub-resource

### Tài nguyên: Posts (Dựa trên Source code thực tế)
* `/api/v1/posts` [GET, POST] ➔ **Collection** (Lấy danh sách / Tạo bài mới)
* `/api/v1/posts/{post_id}` [GET, PATCH, DELETE] ➔ **Item** (Xem chi tiết / Sửa một phần / Xóa bài)

### Tài nguyên: Users
* `/api/v1/users` [GET, POST] ➔ **Collection**
* `/api/v1/users/{user_id}` [GET, PATCH, DELETE] ➔ **Item**
* `/api/v1/users/{user_id}/followers` [GET] ➔ **Sub-resource**
* `/api/v1/users/{user_id}/following` [GET] ➔ **Sub-resource**

### Tài nguyên: Comments
* `/api/v1/posts/{post_id}/comments` [GET, POST] ➔ **Sub-resource** (Bình luận nằm trong 1 bài viết)
* `/api/v1/comments/{comment_id}` [GET, PATCH, DELETE] ➔ **Item**

### Tài nguyên: Tags
* `/api/v1/tags` [GET, POST] ➔ **Collection**
* `/api/v1/tags/{tag_id}` [GET, PATCH, DELETE] ➔ **Item**
* `/api/v1/posts/{post_id}/tags` [GET, PUT] ➔ **Sub-resource** (Gắn/Lấy thẻ của 1 bài viết)
## 3. Kiểm thử Error Handler

### 3.1. Kiểm tra Resource không tồn tại

Gửi request đến một bài viết không tồn tại:

```bash
curl http://localhost:5000/api/v1/posts/999
```

Response:

```json
{
    "type": "https://api.example.com/probs/post-not-found",
    "title": "Resource Not Found",
    "status": 404,
    "instance": "/api/v1/posts/999",
    "trace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "detail": "Không tìm thấy bài viết với ID 999",
    "resource_id": 999
}
```



### 3.2. Kiểm tra khi Client không gửi `Accept`

Gửi request không có header `Accept`:

```bash
curl http://localhost:5000/api/v1/posts/999
```

Response:


```json
{
    "type": "https://api.example.com/probs/post-not-found",
    "title": "Resource Not Found",
    "status": 404,
    "instance": "/api/v1/posts/999",
    "trace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "detail": "Không tìm thấy bài viết với ID 999",
    "resource_id": 999
}
```
Server vẫn trả về định dạng `application/problem+json` dù Client không cung cấp header `Accept`.

---

### 3.3. Kiểm tra với `Accept: application/json`

Gửi request với header:

```bash
curl -H "Accept: application/json" http://localhost:5000/api/v1/posts/999
```

Response:


```json
{
    "type": "https://api.example.com/probs/post-not-found",
    "title": "Resource Not Found",
    "status": 404,
    "instance": "/api/v1/posts/999",
    "trace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "detail": "Không tìm thấy bài viết với ID 999",
    "resource_id": 999
}
```

---

### 3.4. Kiểm tra HTTP Exception

Gửi request đến một endpoint không tồn tại:

```bash
curl http://localhost:5000/api/v1/unknown
```

Flask sẽ phát sinh `HTTPException` với mã `404`.

Error handler sẽ chuyển lỗi thành `application/problem+json`.


Response có dạng:

```json
{
    "type": "https://api.example.com/probs/http-error",
    "title": "Not Found",
    "status": 404,
    "instance": "/api/v1/unknown",
    "trace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "detail": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```

---

### 3.5. Kiểm tra Unhandled Exception

Endpoint dùng để mô phỏng lỗi chưa được xử lý:

```bash
curl http://localhost:5000/api/v1/test-error
```

Server phát sinh:

```python
RuntimeError("Database connection failed")
```

Response:

```json
{
    "type": "https://api.example.com/probs/internal-server-error",
    "title": "Internal Server Error",
    "status": 500,
    "instance": "/api/v1/test-error",
    "trace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "detail": "Đã xảy ra lỗi không mong muốn."
}
```

Thông tin lỗi chi tiết được ghi ở phía server thông qua:

```python
app.logger.exception("Unhandled exception")
```
### 3.6. Kiểm tra Validation Error

```bash
curl -X POST http://localhost:5000/api/v1/posts \
-H "Content-Type: application/json" \
-d "{}"
```

Response:

```json
{
    "type": "https://api.example.com/probs/validation-error",
    "title": "Bad Request",
    "status": 400,
    "instance": "/api/v1/posts",
    "trace_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "detail": "'title' không được để trống"
}
```