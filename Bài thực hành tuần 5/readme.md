# Lab_01:

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
