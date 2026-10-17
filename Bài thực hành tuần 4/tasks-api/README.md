# Tasks API — Bài tập B4

Flask + OpenAPI **3.0.3** + Swagger UI, dựa trên đề ở slide B4 trang 22–23 và bài tập về nhà trang 33.

## Cấu trúc

```text
tasks-api/
├── app.py
├── openapi.yaml
├── templates/docs.html
├── requirements.txt
├── requirements-dev.txt
├── test_app.py
├── screenshots/
├── .gitignore
└── README.md
```

## Cài đặt và chạy

Python 3.10 trở lên. Mở terminal trong `tasks-api/`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python app.py
```

Mở http://127.0.0.1:5000/docs để xem Swagger UI; http://127.0.0.1:5000/openapi.json trả đặc tả JSON. Cần Internet để tải Swagger UI từ CDN. Nếu cổng 5000 bận, dùng `python -m flask --app app run --port 5001`, mở docs trên cổng 5001.

## Try it out và ảnh nộp bài

1. Mở `/docs`, chọn **Authorize**, nhập `demo-token` (không thêm `Bearer`), chọn **Authorize**, rồi **Close**.
2. Mở **POST /tasks**, chọn **Try it out**, nhập body rồi **Execute**:

   ```json
   {"title":"Hoàn thành bài tập B4","priority":"high","dueDate":"2026-10-18"}
   ```

3. Kiểm tra **201**, header `Location`, body có UUID `id`. Sao chép ID này.
4. Chạy **GET /tasks** và **GET /tasks/{taskId}**: nhận **200**, thấy task vừa tạo.
5. Chạy **PATCH /tasks/{taskId}** với `{"status":"done"}`: nhận **200**, tiêu đề giữ nguyên.
6. Chạy **DELETE /tasks/{taskId}**: nhận **204**, không có body. GET lại nhận **404**.
7. Chụp màn hình có Request URL, Server response **201/200** và body; lưu `screenshots/try-it-out.png` để nộp.

Token được kiểm tra thật ở cả 5 endpoint. Đây là token demo cố định, **không phải JWT**. Có thể thay bằng biến môi trường trước khi chạy:

```sh
export TASKS_API_TOKEN='token-rieng-cua-ban'
python app.py
```

Không đưa token riêng lên Git. `/docs` và `/openapi.json` không yêu cầu token.

## Hợp đồng API

| Method | Path | Thành công | Chức năng |
|---|---|---|---|
| GET | `/tasks` | 200 | `{items, total}`, lọc status, giới hạn limit |
| POST | `/tasks` | 201 + Location | Tạo task, server sinh UUID |
| GET | `/tasks/{taskId}` | 200 | Đọc task |
| PATCH | `/tasks/{taskId}` | 200 | Sửa một phần |
| DELETE | `/tasks/{taskId}` | 204 | Xóa, không có body |

Task gồm `id`, `title`, `status`, `priority` và hai trường tùy chọn `dueDate`, `assigneeId`. Khi tạo, `title` bắt buộc và không được chỉ có khoảng trắng; `status` mặc định `open` (enum `open/done`), `priority` mặc định `normal` (enum `low/normal/high`). `dueDate` là ngày hợp lệ `YYYY-MM-DD`; `assigneeId` là UUID, chưa kiểm tra người được giao có tồn tại.

GET mặc định lấy mọi trạng thái, tối đa 10 task; `limit` từ 1 đến 100. `total` tính sau lọc nhưng trước giới hạn. Task theo thứ tự tạo; chưa có offset/cursor.

Lỗi dùng `application/problem+json` với `type`, `title`, `status`, `detail`: **400** khi JSON/null, Content-Type, query hoặc UUID đường dẫn sai; **401** thiếu/sai token; **404** không tìm thấy; **422** khi body sai schema, có trường lạ hoặc PATCH rỗng.

## Hai quyết định thiết kế khó nhất

### 1. Tách dữ liệu tạo và cập nhật

Dùng chung schema bắt buộc `title` sẽ khiến PATCH đổi trạng thái cũng phải gửi lại tiêu đề. Vì vậy `CreateTaskInput` bắt buộc `title`, còn `UpdateTaskInput` cho phép từng trường riêng lẻ nhưng phải có ít nhất một trường. PATCH chỉ sửa trường được gửi, giữ nguyên phần còn lại và không áp lại giá trị mặc định. `id` do server quản lý; từ chối `id`, trường lạ và `null` trong input. Bản đơn giản chưa hỗ trợ xóa riêng dueDate/assigneeId.

`Task` được tái sử dụng qua `$ref` trong phản hồi tạo/đọc/sửa và danh sách. `TaskId` dùng chung ở path-level; `PageLimit`, `StatusFilter` ở `components.parameters`. Các response thành công/lỗi nằm ở `components.responses`. Thuộc tính input được viết rõ, tránh kết hợp `allOf` và `additionalProperties: false` gây khó hiểu trong OpenAPI 3.0.

### 2. Giữ YAML là nguồn chung cho đặc tả, docs và validation

Bài tập yêu cầu tự viết YAML, nên Flask đọc chính file đó để trả `/openapi.json`; Swagger UI tải JSON này. Kiểm tra body dùng schema trong YAML bằng `jsonschema`, tránh duy trì thêm bộ validation thủ công. Schema ở đây dùng tập từ khóa tương thích JSON Schema Draft 4; đây không phải bộ xử lý toàn bộ OpenAPI, ví dụ cần xử lý thêm nếu dùng `nullable`.

Không thêm apispec/flask-smorest vì chưa cần sinh spec từ code. `servers: /` giúp Try it out gọi đúng origin/cổng hiện tại mà không cần CORS. Giữ đường dẫn `/tasks` đúng yêu cầu thay vì tiền tố `/v1` trong ví dụ slide. Có Bearer auth đơn giản nhưng không khai báo `bearerFormat: JWT` vì chưa triển khai JWT.

## Kiểm thử

```sh
python -m unittest -v
python -m openapi_spec_validator openapi.yaml
```

Đã chạy: **3 test đạt** (chứa nhiều trường hợp), `openapi.yaml: OK`. Test kiểm tra chuẩn 3.0.3, JSON spec khớp YAML, cấu hình docs, CRUD, lọc, giới hạn, token, dữ liệu sai và request lỗi không làm thay đổi task. Response được đối chiếu với schema/status trong đặc tả.

Chưa xác minh thao tác Try it out trên trình duyệt và chưa có ảnh: trình duyệt tích hợp của môi trường thực hiện chặn localhost. Làm theo các bước trên để bổ sung ảnh thật trước khi nộp.

## Giới hạn và nộp bài

Dữ liệu trong bộ nhớ, mất khi tắt app; khóa bảo vệ thao tác trong một process. Chạy một process để demo. Không có database, đăng nhập hay phân quyền từng người; không dùng dữ liệu thật hoặc triển khai công khai với token demo.

Chưa đẩy lên GitHub do chưa có repo nhóm đích. Đưa mã nguồn và ảnh thật lên repo nhóm, không đưa `.venv/` hoặc token riêng. File tham chiếu của dự án không bị chỉnh sửa.
