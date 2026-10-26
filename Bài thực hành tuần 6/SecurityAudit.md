# Báo cáo Đánh giá An ninh Bảo mật API (Security Audit)
**Bài tập về nhà - Buổi 06: API Security, Authentication & Authorization**  
**Tiêu chuẩn đối chiếu:** OWASP API Security Top 10 (2023)  

---

## 1. Bảng tổng hợp 5 rủi ro bảo mật

| STT | Mã OWASP | Tên lỗ hổng / Rủi ro | Vị trí ảnh hưởng | Mức độ |
|:---:|:---|:---|:---|:---:|
| 1 | **API1:2023** | Broken Object Level Authorization (BOLA) | `GET /posts/{id}` | **Critical** |
| 2 | **API2:2023** | Broken Authentication (Quản lý Token & Thu hồi) | `POST /auth/login`, `/auth/refresh` | **High** |
| 3 | **API4:2023** | Unrestricted Resource Consumption (Thiếu Rate Limit) | `POST /auth/login` | **High** |
| 4 | **API5:2023** | Broken Function Level Authorization (BFLA) | Các thao tác xóa/sửa bài viết | **High** |
| 5 | **API3:2023** | Broken Object Property Level Authorization (Lộ dữ liệu nhạy cảm) | Payload trả về của API | **Medium** |

---

## 2. Chi tiết 5 điểm rủi ro tiềm ẩn

### 1. API1:2023 - Broken Object Level Authorization (BOLA / IDOR)
* **Rủi ro:** Người dùng có token hợp lệ nhưng có thể xem hoặc xóa bài viết riêng tư (`is_private=true`) của người khác bằng cách thay đổi `id` trên đường dẫn URL.
* **Kịch bản khai thác:** User A (`id=1`) gửi request `GET /posts/105` (bài viết riêng tư của User B). Do backend chỉ xác thực token mà không kiểm tra quyền sở hữu đối tượng, User A đọc được nội dung riêng tư của User B.
* **Biện pháp khắc phục:** Bổ sung decorator/middleware kiểm tra quyền sở hữu tài nguyên (`owner_id == caller_id` hoặc có vai trò `admin`) trước khi trả về dữ liệu.

---

### 2. API2:2023 - Broken Authentication (Xác thực & Thu hồi Token)
* **Rủi ro:** Khóa bí mật `JWT_SECRET_KEY` bị hardcode trực tiếp trong mã nguồn; danh sách token đã thu hồi (`REVOKED_JTIS`) lưu tạm trong RAM sẽ bị mất sạch khi server khởi động lại.
* **Kịch bản khai thác:** Người dùng đã nhấn đăng xuất, nhưng server bị restart khiến RAM bị xóa. Kẻ tấn công lấy được token cũ trước đó vẫn có thể tiếp tục sử dụng để gửi request hợp lệ.
* **Biện pháp khắc phục:** 
  * Đưa `JWT_SECRET_KEY` vào biến môi trường hệ thống (`.env`).
  * Lưu trữ danh sách thu hồi token vào Redis có thời gian sống (TTL) tương ứng với thời hạn của token.

---

### 3. API4:2023 - Unrestricted Resource Consumption (Thiếu Rate Limiting)
* **Rủi ro:** Endpoint đăng nhập `/auth/login` không giới hạn tần suất gọi. Thuật toán băm mật khẩu `bcrypt` tiêu tốn nhiều CPU, dễ bị kẻ tấn công lợi dụng để làm quá tải server hoặc brute-force mật khẩu.
* **Kịch bản khai thác:** Kẻ tấn công gửi đồng thời hàng ngàn request đăng nhập trong 1 giây. Việc xử lý hash mật khẩu liên tục khiến CPU chạm ngưỡng 100%, gây nghẽn dịch vụ (DoS) cho toàn bộ người dùng khác.
* **Biện pháp khắc phục:** Áp dụng Rate Limiting bằng thư viện như `Flask-Limiter` (giới hạn tối đa 5 lần thử/phút cho mỗi IP) và khóa tạm tài khoản sau nhiều lần thất bại liên tiếp.

---

### 4. API5:2023 - Broken Function Level Authorization (BFLA)
* **Rủi ro:** Thiếu kiểm tra vai trò (Role) và phạm vi quyền hạn (Scope) cho từng thao tác cụ thể tại backend, chỉ phụ thuộc vào việc người dùng "đã đăng nhập".
* **Kịch bản khai thác:** Tài khoản có vai trò `viewer` (chỉ có quyền đọc) gửi request `DELETE /posts/101`. Nếu backend thiếu bước kiểm tra role, đơn hàng/bài viết sẽ bị xóa trái phép.
* **Biện pháp khắc phục:** Phân quyền chặt chẽ tại từng endpoint bằng decorator kiểm tra vai trò (`@require_roles("admin", "customer")`) và phạm vi (`@require_scopes("posts:write")`).

---

### 5. API3:2023 - Broken Object Property Level Authorization (Lộ dữ liệu nhạy cảm)
* **Rủi ro:** Server truy vấn toàn bộ bản ghi (`SELECT *`) rồi serialize trực tiếp trả về cho client, dẫn đến việc vô tình làm lộ các trường nhạy cảm như hash mật khẩu (`pwd_hash`) hay cờ hệ thống.
* **Kịch bản khai thác:** Người dùng gọi `GET /posts/101`, API trả về kèm đối tượng tác giả chứa cả cột `pwd_hash`. Kẻ tấn công thu thập hash để tiến hành bẻ khóa mật khẩu offline.
* **Biện pháp khắc phục:** Dùng DTO hoặc Schema Serialization (chỉ định danh sách trường Allowlist được phép trả về như `id`, `owner_id`, `content`, `created_at`), loại bỏ hoàn toàn các trường nhạy cảm.
