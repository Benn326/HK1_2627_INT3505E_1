# Lab_01: (bài 2 cuối slide + list_books)

## 1. CURL


### 1.1. Phân trang Offset + Filter theo genre + Multi-key Sort

Truy vấn danh sách sách thuộc danh mục tech, sắp xếp theo giá giảm dần (-price_vnd) kết hợp tên sách tăng dần (title), lấy page 1 với giới hạn 2 bản ghi:
```bash
curl "http://localhost:5000/api/v1/books?strategy=offset&genre=tech&sort=-price_vnd,title&page=1&limit=2"
```

Response:

```json
{
  "data": [
    {
      "authors": [
        {
          "id": 1,
          "name": "Martin Kleppmann"
        }
      ],
      "category": "tech",
      "id": 1,
      "isbn": "978-1449373320",
      "price_vnd": 450000,
      "stock": 12,
      "title": "Designing Data-Intensive Applications"
    },
    {
      "authors": [
        {
          "id": 2,
          "name": "JJ Geewax"
        }
      ],
      "category": "tech",
      "id": 2,
      "isbn": "978-1617295850",
      "price_vnd": 380000,
      "stock": 8,
      "title": "API Design Patterns"
    }
  ],
  "pagination": {
    "has_next": true,
    "limit": 2,
    "page": 1,
    "total": 3
  },
  "strategy": "offset"
}
```



### 1.2. Phân trang Cursor (keyset pagination)

**Bước 1:** Lấy trang đầu tiên limit = 2, sort theo -price_vnd

```bash
curl "http://localhost:5000/api/v1/books?strategy=cursor&sort=-price_vnd&limit=2"
```



```json
{
  "data": [
    {
      "authors": [
        {
          "id": 1,
          "name": "Martin Kleppmann"
        }
      ],
      "category": "tech",
      "id": 1,
      "isbn": "978-1449373320",
      "price_vnd": 450000,
      "stock": 12,
      "title": "Designing Data-Intensive Applications"
    },
    {
      "authors": [
        {
          "id": 2,
          "name": "JJ Geewax"
        }
      ],
      "category": "tech",
      "id": 2,
      "isbn": "978-1617295850",
      "price_vnd": 380000,
      "stock": 8,
      "title": "API Design Patterns"
    }
  ],
  "pagination": {
    "has_next": true,
    "limit": 2,
    "next_cursor": "eyJzb3J0IjogIi1wcmljZV92bmQiLCAidmFsdWVzIjogeyJwcmljZV92bmQiOiAzODAwMDAsICJpZCI6IDJ9fQ=="
  },
  "strategy": "cursor"
}
```

**Bước 2:** Dùng next_cursor để lấy trang tiếp theo

```bash 
curl "http://localhost:5000/api/v1/books?strategy=cursor&sort=-price_vnd&limit=2&cursor=eyJzb3J0IjogIi1wcmljZV92bmQiLCAidmFsdWVzIjogeyJwcmljZV92bmQiOiAzODAwMDAsICJpZCI6IDJ9fQ=="
```
Response:

```json

{
  "data": [
    {
      "authors": [
        {
          "id": 1,
          "name": "Martin Kleppmann"
        }
      ],
      "category": "tech",
      "id": 3,
      "isbn": "978-0134494166",
      "price_vnd": 320000,
      "stock": 20,
      "title": "Clean Architecture"
    }
  ],
  "pagination": {
    "has_next": false,
    "limit": 2,
    "next_cursor": null
  },
  "strategy": "cursor"
}
```


---

### 1.3. Kiểm tra JSON Schema Validation (POST /api/v1/books)

Code:

```bash
curl -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Principles of Web API Design\", \"isbn\": \"978-0137355631\", \"price_vnd\": 410000, \"stock\": 15, \"category_id\": 1, \"author_ids\": [1]}"
```

Response:


```json
{
  "authors": [
    {
      "id": 1,
      "name": "Martin Kleppmann"
    }
  ],
  "category": "tech",
  "id": 4,
  "isbn": "978-0137355631",
  "price_vnd": 410000,
  "stock": 15,
  "title": "Principles of Web API Design"
}
```
# Lab_02: (Bài 1 cuối slide gồm: thiết kế resrc + URL 16 endpoint + json schemas cho 3 resrc chính)
## 1. CURL:
### 1.1. Test khách reviews sách:
```bash
curl -X POST http://localhost:5000/api/v1/books/1/reviews -H "Content-Type: application/json" -d "{\"rating\": 5, \"comment\": \"Sach rat hay va chi tiet!\", \"user_id\": 1}"
```

response:

```json
{
  "book_id": 1,
  "comment": "Sach rat hay va chi tiet!",
  "id": 2,
  "rating": 5,
  "user_id": 1
}
```
### 1.2. Test xem đánh giá của sách số 1:

```Bash
curl "http://localhost:5000/api/v1/books/1/reviews"
```

response:

```json
{
  "book_id": 1,
  "reviews": [
    {
      "book_id": 1,
      "comment": "Sách rất hay và chi tiết!",
      "id": 1,
      "rating": 5,
      "user_id": 1
    },
    {
      "book_id": 1,
      "comment": "Sach rat hay va chi tiet!",
      "id": 2,
      "rating": 5,
      "user_id": 1
    }
  ],
  "title": "Designing Data-Intensive Applications"
}
```


### 1.3. Test tác giả số 1 đánh giá sách của họ:

```bash
curl "http://localhost:5000/api/v1/authors/1/books"
```


response:

```json
{
  "author": {
    "bio": "Distributed systems researcher",
    "id": 1,
    "name": "Martin Kleppmann"
  },
  "books": [
    {
      "authors": [
        {
          "id": 1,
          "name": "Martin Kleppmann"
        }
      ],
      "category": "tech",
      "id": 1,
      "isbn": "978-1449373320",
      "price_vnd": 450000,
      "stock": 12,
      "title": "Designing Data-Intensive Applications"
    },
    {
      "authors": [
        {
          "id": 1,
          "name": "Martin Kleppmann"
        }
      ],
      "category": "tech",
      "id": 3,
      "isbn": "978-0134494166",
      "price_vnd": 320000,
      "stock": 20,
      "title": "Clean Architecture"
    }
  ]
}
```

### 1.4. Khách hàng tạo đơn hàng mua nhiều sách kèm số lượng (Validate bằng order.schema.json):

```bash
curl -X POST http://localhost:5000/api/v1/orders -H "Content-Type: application/json" -d "{\"user_id\": 1, \"items\": [{\"book_id\": 1, \"quantity\": 2}, {\"book_id\": 2, \"quantity\": 1}]}"
```

response:

```json 
{
  "created_at": "2026-10-17T21:39:33.620868",
  "id": 1,
  "items": [
    {
      "book_id": 1,
      "quantity": 2,
      "title": "Designing Data-Intensive Applications"
    },
    {
      "book_id": 2,
      "quantity": 1,
      "title": "API Design Patterns"
    }
  ],
  "status": "pending",
  "user_id": 1
}
```

### 1.5. Xem chi tiết lịch sử đơn hàng số 1 vừa tạo:

```bash
curl "http://localhost:5000/api/v1/orders/1"
```

response:

``` json
{
  "created_at": "2026-10-17T21:39:33.620868",
  "id": 1,
  "items": [
    {
      "book_id": 1,
      "quantity": 2,
      "title": "Designing Data-Intensive Applications"
    },
    {
      "book_id": 2,
      "quantity": 1,
      "title": "API Design Patterns"
    }
  ],
  "status": "pending",
  "user_id": 1
}
```

