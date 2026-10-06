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