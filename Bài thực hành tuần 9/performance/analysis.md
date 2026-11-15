# Báo cáo Phân tích Load Test Books API (Lab 04)

## 1. Bảng tổng hợp số liệu thực tế

Thử nghiệm được thực hiện trên môi trường local (Flask 3.1, SQLite, Locust 2.47). Các file báo cáo HTML chi tiết được lưu trong thư mục `reports/`.

| Kịch bản | Users | Spawn rate | Thời gian (Duration) | Requests | RPS (Req/s) | Fail rate (Tổng) | p95 (Tổng) | p99 (Tổng) | Max Latency | Báo cáo |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **A (Baseline)** | 10 | 2 | 30s | 140 | 4.77 | 0.00% | 31 ms | 37 ms | 281 ms | [reports/A.html](reports/A.html) |
| **B (Load test)** | 50 | 5 | 60s | 1398 | 23.49 | 0.21% | 31 ms | 53 ms | 74 ms | [reports/B.html](reports/B.html) |
| **C (Spike test)** | 200 | 50 | 30s | 2817 | 95.71 | 0.25% | 170 ms | 290 ms | 627 ms | [reports/C.html](reports/C.html) |

---

## 2. Chi tiết phân tích theo yêu cầu

### Câu 1: Trong ba kịch bản, kịch bản nào có p95 cao nhất? Vì sao?
- **Kịch bản có p95 cao nhất:** **Kịch bản C (Spike test)** với `p95 = 170 ms` (ở kịch bản A và B, p95 chỉ dừng ở mức `31 ms`). Cụ thể theo từng endpoint trong kịch bản C:
  - `POST /books`: p95 = 230 ms, p99 = 440 ms, Max = 627 ms
  - `GET /books/search`: p95 = 180 ms
  - `GET /books`: p95 = 160 ms
  - `GET /books/{id}`: p95 = 150 ms
- **Nguyên nhân kỹ thuật:**
  1. **Đột biến người dùng (Spike):** Kịch bản C đẩy từ 0 lên 200 user chỉ trong vòng 4 giây (spawn rate = 50 user/giây).
  2. **Bão hòa hàng đợi (Queue Saturation):** Máy chủ Flask development server (Werkzeug) và tài nguyên CPU đơn luồng bị dồn ứ số lượng kết nối đồng thời trong tích tắc.
  3. **Khóa dữ liệu SQLite:** Endpoint `POST /books` thực hiện ghi vào database SQLite (cơ chế database-level lock khi ghi), dẫn đến các request ghi và đọc phải xếp hàng đợi giải phóng lock, làm đuôi độ trễ (*tail latency*: p95, p99, max) tăng phi tuyến tính.

---

### Câu 2: Có endpoint nào có fail rate tăng theo số user không? Phân tích nguyên nhân dựa trên code.
- **Hiện tượng quan sát:** 
  - Chỉ có duy nhất endpoint `GET /books/search` ghi nhận thất bại:
    - Kịch bản A: 0 lỗi / 31 request (0.00%)
    - Kịch bản B: 3 lỗi / 356 request (0.84% ~ 1%)
    - Kịch bản C: 7 lỗi / 690 request (1.01% ~ 1%)
- **Bản chất nguyên nhân dựa trên code:**
  - **Lỗi giả lập từ phía client load test (`locustfile.py`), KHÔNG PHẢI lỗi của server API:**
    Trong `locustfile.py`, task `search_by_year` cố ý cấu hình tỷ lệ tiêm lỗi 1%:
    ```python
    if random.random() < 0.01:
        response.failure("Injected 1% simulated HTTP 500 error")
    ```
  - **Phía Backend API (`app.py`):** Server xử lý đúng logic, trả về HTTP 200 cho tất cả request hợp lệ. Hoàn toàn **không có lỗi HTTP 500 thực tế** nào phát sinh từ phía server.
  - Tỷ lệ lỗi duy trì quanh mốc ~1% của endpoint này là hoàn toàn do xác suất ngẫu nhiên `random.random() < 0.01` của kịch bản test.

---

### Câu 3: Nếu production yêu cầu SLO p95 < 300ms, kịch bản nào đạt? Giới hạn phép đo và đề xuất baseline cho CI gate.
- **Đánh giá theo SLO (`p95 < 300ms`):**
  - **Kịch bản A (10 users):** `p95 = 31 ms` < 300ms ➔ **ĐẠT**.
  - **Kịch bản B (50 users):** `p95 = 31 ms` < 300ms ➔ **ĐẠT**.
  - **Kịch bản C (200 users):** `p95 = 170 ms` < 300ms ➔ **ĐẠT** trên chỉ số p95 tổng thể. Tuy nhiên, `p99 = 290 ms` đã mấp mé ngưỡng 300ms và Max latency của `POST /books` đã vọt lên tới `627 ms`.
- **Giới hạn của phép đo:**
  - Phép đo được thực thi trên môi trường local sử dụng Flask development server (`app.run()`) và SQLite file database.
  - Phép đo không đại diện cho năng lực thực tế của môi trường production (thường chạy trên Gunicorn/Uvicorn multi-worker, reverse proxy Nginx, PostgreSQL/MySQL có connection pooling và cluster riêng).
- **Đề xuất baseline cho CI Gate (Automated Pipeline):**
  - **Kịch bản khuyến nghị:** Chạy kịch bản tải vừa phải (20 - 50 users, 30s).
  - **Tiêu chuẩn gate (Fail build nếu vi phạm):**
    - `p95 < 100 ms` (đảm bảo biên an toàn dự phòng trước ngưỡng 300ms ở production).
    - `Error rate = 0%` (hoặc `<= 1.5%` nếu có giả lập client-side injection).
    - `RPS >= 20 req/s`.

---

### Câu 4 (Bonus): Phân tích tình huống Connection Pool giới hạn ở 5 khi 200 user truy cập đồng thời. Cách xác nhận bằng Locust.
- **Hiện tượng lý thuyết khi Connection Pool = 5:**
  - Với 200 user gửi request đồng thời, chỉ có tối đa 5 kết nối database được phục vụ tại một thời điểm. 195 request còn lại sẽ phải xếp hàng trong connection queue của SQLAlchemy (`QueuePool`).
  - Khi hàng đợi đầy hoặc thời gian chờ vượt quá `pool_timeout` (mặc định 30s của SQLAlchemy), các request sẽ bị từ chối với ngoại lệ `TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out`.
  - Hậu quả: Server sẽ trả về hàng loạt lỗi **HTTP 500 Internal Server Error**, throughput (RPS) sụt giảm nghiêm trọng và độ trễ tăng vọt lên mức bằng hoặc vượt quá `pool_timeout`.
- **Cách xác nhận hiện tượng bằng Locust:**
  1. **Quan sát tab Failures / Error report:** Cột `# fails` tăng vọt với các lỗi `HTTPError("500 Internal Server Error")` hoặc connection refused/timeout.
  2. **Quan sát đồ thị Response Times (ms):** Đồ thị Median và 95th Percentile sẽ tăng đột biến theo đường thẳng đứng (chạm ngưỡng timeout 30,000 ms).
  3. **Quan sát đồ thị Total Requests per Second (RPS):** Đường xanh (Requests/s) bị chặn trần (bão hòa) rồi suy giảm nhanh chóng, trong khi đường đỏ (Failures/s) tăng vọt.
