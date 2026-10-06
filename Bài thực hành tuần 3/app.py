from flask import Flask, request, jsonify, url_for
from werkzeug.exceptions import HTTPException
from error import ApiProblem, problem
import base64
import json
import logging

app = Flask(__name__)
app.json.ensure_ascii = False


@app.errorhandler(ApiProblem)
def handle_api_problem(error):
    return problem(
        error.status,
        error.title,
        error.detail,
        error.type_path,
        **error.extra
    )


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    return problem(
        error.code,
        error.name,
        error.description,
        "http-error"
    )


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("Unhandled exception")

    return problem(
        500,
        "Internal Server Error",
        "Đã xảy ra lỗi không mong muốn.",
        "internal-server-error"
    )


VALID_STATUS = {"draft", "published"}
MAX_PAGE_SIZE = 100

posts_db = [
    {
        "id": 1,
        "title": "Giới thiệu REST API",
        "content": "Nội dung bài 1",
        "author_id": 101,
        "status": "published"
    },
    {
        "id": 2,
        "title": "Best Practices Flask",
        "content": "Nội dung bài 2",
        "author_id": 102,
        "status": "draft"
    },
]

orders_db = [
    {
        "id": 1,
        "customer_id": 101,
        "total": 250000,
        "status": "paid"
    },
    {
        "id": 2,
        "customer_id": 102,
        "total": 180000,
        "status": "pending"
    },
    {
        "id": 3,
        "customer_id": 101,
        "total": 420000,
        "status": "shipped"
    },
    {
        "id": 4,
        "customer_id": 103,
        "total": 150000,
        "status": "cancelled"
    },
    {
        "id": 5,
        "customer_id": 102,
        "total": 320000,
        "status": "paid"
    },
    {
        "id": 6,
        "customer_id": 104,
        "total": 500000,
        "status": "paid"
    },
    {
        "id": 7,
        "customer_id": 103,
        "total": 275000,
        "status": "pending"
    },
    {
        "id": 8,
        "customer_id": 101,
        "total": 390000,
        "status": "shipped"
    },
    {
        "id": 9,
        "customer_id": 105,
        "total": 125000,
        "status": "paid"
    },
    {
        "id": 10,
        "customer_id": 104,
        "total": 610000,
        "status": "pending"
    },
]
next_post_id = 3


def post_not_found(post_id):
    raise ApiProblem(
        status=404,
        title="Resource Not Found",
        detail=f"Không tìm thấy bài viết với ID {post_id}",
        type_path="post-not-found",
        resource_id=post_id
    )


def find_post(post_id):
    return next((p for p in posts_db if p["id"] == post_id), None)


def validate_fields(payload, partial):
    for key in ("title", "content"):
        if key in payload or not partial:
            value = payload.get(key)

            if not isinstance(value, str) or not value.strip():
                return f"'{key}' không được để trống"

    if "status" in payload and payload["status"] not in VALID_STATUS:
        return f"'status' phải là một trong {sorted(VALID_STATUS)}"

    return None


@app.get("/api/v1/posts")
def list_posts():
    status = request.args.get("status")
    author_id = request.args.get("author_id", type=int)
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    if page < 1 or not 1 <= page_size <= MAX_PAGE_SIZE:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail=f"'page' >= 1 và 'page_size' trong khoảng 1..{MAX_PAGE_SIZE}",
            type_path="validation-error"
        )

    filtered = posts_db

    if status:
        filtered = [
            p for p in filtered
            if p["status"] == status
        ]

    if author_id is not None:
        filtered = [
            p for p in filtered
            if p["author_id"] == author_id
        ]

    start = (page - 1) * page_size

    return jsonify({
        "data": filtered[start:start + page_size],
        "page": page,
        "page_size": page_size,
        "total": len(filtered),
    }), 200


@app.post("/api/v1/posts")
def create_post():
    global next_post_id

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail="Body phải là JSON object",
            type_path="validation-error"
        )

    error = validate_fields(payload, partial=False)

    if error:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail=error,
            type_path="validation-error"
        )

    new_post = {
        "id": next_post_id,
        "title": payload["title"].strip(),
        "content": payload["content"].strip(),
        "author_id": payload.get("author_id", 1),
        "status": payload.get("status", "draft"),
    }

    posts_db.append(new_post)
    next_post_id += 1

    resp = jsonify(new_post)
    resp.status_code = 201
    resp.headers["Location"] = url_for(
        "get_post",
        post_id=new_post["id"]
    )

    return resp


@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    post = find_post(post_id)

    if not post:
        post_not_found(post_id)

    return jsonify(post), 200


@app.patch("/api/v1/posts/<int:post_id>")
def update_post(post_id):
    post = find_post(post_id)

    if not post:
        post_not_found(post_id)

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail="Body phải là JSON object",
            type_path="validation-error"
        )

    error = validate_fields(payload, partial=True)

    if error:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail=error,
            type_path="validation-error"
        )

    for key in ("title", "content", "status"):
        if key in payload:
            post[key] = (
                payload[key].strip()
                if key != "status"
                else payload[key]
            )

    return jsonify(post), 200


@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id):
    post = find_post(post_id)

    if not post:
        post_not_found(post_id)

    posts_db.remove(post)

    return "", 204


@app.get("/api/v1/test-error")
def test_error():
    raise RuntimeError("Database connection failed")

ORDER_STATUSES = {
    "pending",
    "paid",
    "cancelled",
    "shipped"
}

ORDER_FIELDS = {
    "id",
    "customer_id",
    "total",
    "status"
}

ORDER_SORT_FIELDS = {
    "id",
    "customer_id",
    "total"
}


def encode_cursor(order_id):
    raw = str(order_id).encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_cursor(cursor):
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        return int(raw)
    except Exception:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail="Cursor không hợp lệ",
            type_path="invalid-cursor"
        )


@app.get("/orders")
def list_orders():
    limit = request.args.get("limit", default=10, type=int)
    cursor = request.args.get("cursor")
    status = request.args.get("status")
    customer_id = request.args.get("customer_id", type=int)
    sort = request.args.get("sort", "id")
    fields = request.args.get("fields")

    if limit < 1 or limit > 100:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail="'limit' phải nằm trong khoảng 1..100",
            type_path="validation-error"
        )

    if status and status not in ORDER_STATUSES:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail="'status' không hợp lệ",
            type_path="validation-error"
        )

    reverse = sort.startswith("-")
    sort_field = sort[1:] if reverse else sort

    if sort_field not in ORDER_SORT_FIELDS:
        raise ApiProblem(
            status=400,
            title="Bad Request",
            detail="'sort' không hợp lệ",
            type_path="validation-error"
        )

    if fields:
        selected_fields = fields.split(",")

        if any(field not in ORDER_FIELDS for field in selected_fields):
            raise ApiProblem(
                status=400,
                title="Bad Request",
                detail="'fields' chứa trường không hợp lệ",
                type_path="validation-error"
            )
    else:
        selected_fields = [
            "id",
            "customer_id",
            "total",
            "status"
        ]

    result = orders_db[:]

    if status:
        result = [
            order for order in result
            if order["status"] == status
        ]

    if customer_id is not None:
        result = [
            order for order in result
            if order["customer_id"] == customer_id
        ]

    result.sort(
        key=lambda order: (
            order[sort_field],
            order["id"]
        ),
        reverse=reverse
    )

    if cursor:
        cursor_id = decode_cursor(cursor)

        ids = [order["id"] for order in result]

        if cursor_id not in ids:
            raise ApiProblem(
                status=400,
                title="Bad Request",
                detail="Cursor không hợp lệ",
                type_path="invalid-cursor"
            )

        index = ids.index(cursor_id)
        result = result[index + 1:]

    page = result[:limit]

    next_cursor = None

    if len(result) > limit:
        next_cursor = encode_cursor(page[-1]["id"])

    data = []

    for order in page:
        item = {}

        for field in selected_fields:
            item[field] = order[field]

        data.append(item)

    return jsonify({
        "data": data,
        "limit": limit,
        "next_cursor": next_cursor
    }), 200
if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    app.run(debug=True)