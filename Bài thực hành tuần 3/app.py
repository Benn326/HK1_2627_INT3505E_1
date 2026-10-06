from flask import Flask, request, jsonify, url_for

app = Flask(__name__)
app.json.ensure_ascii = False

VALID_STATUS = {"draft", "published"}
MAX_PAGE_SIZE = 100

posts_db = [
    {"id": 1, "title": "Giới thiệu REST API", "content": "Nội dung bài 1", "author_id": 101, "status": "published"},
    {"id": 2, "title": "Best Practices Flask", "content": "Nội dung bài 2", "author_id": 102, "status": "draft"},
]
next_post_id = 3


def problem(status, title, detail, slug):
    resp = jsonify({
        "type": f"https://example.com/errors/{slug}",
        "title": title,
        "status": status,
        "detail": detail,
    })
    resp.status_code = status
    resp.mimetype = "application/problem+json"
    return resp


def post_not_found(post_id):
    return problem(404, "Resource Not Found",
                   f"Không tìm thấy bài viết với ID {post_id}", "not-found")


def find_post(post_id):
    return next((p for p in posts_db if p["id"] == post_id), None)


def validate_fields(payload, partial):
    """Trả về chuỗi lỗi hoặc None. partial=True dành cho PATCH."""
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
        return problem(400, "Bad Request",
                       f"'page' >= 1 và 'page_size' trong khoảng 1..{MAX_PAGE_SIZE}",
                       "validation-error")

    filtered = posts_db
    if status:
        filtered = [p for p in filtered if p["status"] == status]
    if author_id is not None:
        filtered = [p for p in filtered if p["author_id"] == author_id]

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
        return problem(400, "Bad Request", "Body phải là JSON object", "validation-error")
    error = validate_fields(payload, partial=False)
    if error:
        return problem(400, "Bad Request", error, "validation-error")

    new_post = {
        "id": next_post_id,
        "title": payload["title"].strip(),
        "content": payload["content"].strip(),
        "author_id": payload.get("author_id", 1),  # thực tế: lấy từ token
        "status": payload.get("status", "draft"),
    }
    posts_db.append(new_post)
    next_post_id += 1

    resp = jsonify(new_post)
    resp.status_code = 201
    resp.headers["Location"] = url_for("get_post", post_id=new_post["id"])
    return resp


@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    post = find_post(post_id)
    if not post:
        return post_not_found(post_id)
    return jsonify(post), 200


@app.patch("/api/v1/posts/<int:post_id>")
def update_post(post_id):
    post = find_post(post_id)
    if not post:
        return post_not_found(post_id)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return problem(400, "Bad Request", "Body phải là JSON object", "validation-error")
    error = validate_fields(payload, partial=True)
    if error:
        return problem(400, "Bad Request", error, "validation-error")

    for key in ("title", "content", "status"):
        if key in payload:
            post[key] = payload[key].strip() if key != "status" else payload[key]

    return jsonify(post), 200


@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id):
    post = find_post(post_id)
    if not post:
        return post_not_found(post_id)
    posts_db.remove(post)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)