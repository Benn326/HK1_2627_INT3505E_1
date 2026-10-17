import base64
import json
from pathlib import Path
from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
from sqlalchemy import asc, desc, and_, or_
from models import db, Book, Category, Author, Review, Order, OrderItem, User

bp = Blueprint("api", __name__, url_prefix="/api/v1")

SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "json-schema"

with open(SCHEMA_DIR / "book.schema.json", "r", encoding="utf-8") as f:
    BOOK_SCHEMA = json.load(f)

with open(SCHEMA_DIR / "review.schema.json", "r", encoding="utf-8") as f:
    REVIEW_SCHEMA = json.load(f)

with open(SCHEMA_DIR / "order.schema.json", "r", encoding="utf-8") as f:
    ORDER_SCHEMA = json.load(f)

ALLOWED_SORT_FIELDS = {
    "id": Book.id,
    "title": Book.title,
    "price_vnd": Book.price_vnd,
    "stock": Book.stock
}


def encode_cursor(data: dict) -> str:
    raw = json.dumps(data).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_cursor(token: str) -> dict:
    raw = base64.urlsafe_b64decode(token.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def parse_sort(sort_param: str):
    fields = []
    for part in sort_param.split(","):
        part = part.strip()
        if not part:
            continue
        direction = "desc" if part.startswith("-") else "asc"
        name = part.lstrip("+-")
        if name not in ALLOWED_SORT_FIELDS:
            raise ValueError(f"Invalid sort field: {name}")
        fields.append((name, direction))
    if not any(f[0] == "id" for f in fields):
        fields.append(("id", "asc"))
    return fields


def build_cursor_filter(sort_fields, cursor_vals):
    clauses = []
    for i in range(len(sort_fields)):
        prefix = [
            ALLOWED_SORT_FIELDS[sort_fields[j][0]] == cursor_vals[sort_fields[j][0]]
            for j in range(i)
        ]
        col_name, direction = sort_fields[i]
        col = ALLOWED_SORT_FIELDS[col_name]
        val = cursor_vals[col_name]
        comp = (col > val) if direction == "asc" else (col < val)
        clauses.append(and_(*prefix, comp) if prefix else comp)
    return or_(*clauses)


@bp.post("/books")
def create_book():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "message": "Malformed JSON"}), 400
    try:
        validate(payload, BOOK_SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400

    book = Book.from_payload(payload)
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@bp.get("/books")
def list_books():
    strategy = request.args.get("strategy", "cursor")
    genre = request.args.get("genre")
    sort_param = request.args.get("sort", "id")

    try:
        limit = min(max(int(request.args.get("limit", 10)), 1), 100)
        sort_fields = parse_sort(sort_param)
    except ValueError as e:
        return jsonify({"error": "bad_request", "message": str(e)}), 400

    query = Book.query
    if genre:
        query = query.join(Category).filter(Category.slug == genre)

    order_exprs = [
        asc(ALLOWED_SORT_FIELDS[name]) if d == "asc" else desc(ALLOWED_SORT_FIELDS[name])
        for name, d in sort_fields
    ]
    query = query.order_by(*order_exprs)

    if strategy == "offset":
        page = max(int(request.args.get("page", 1)), 1)
        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()
        return jsonify({
            "strategy": "offset",
            "data": [b.to_dict() for b in items],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": page * limit < total
            }
        }), 200

    if strategy == "cursor":
        cursor_token = request.args.get("cursor")
        if cursor_token:
            try:
                c_data = decode_cursor(cursor_token)
                if c_data.get("sort") != sort_param:
                    return jsonify({
                        "error": "invalid_cursor",
                        "message": "Sort key changed since cursor was issued"
                    }), 400
                query = query.filter(build_cursor_filter(sort_fields, c_data["values"]))
            except Exception:
                return jsonify({"error": "invalid_cursor", "message": "Malformed cursor"}), 400

        rows = query.limit(limit + 1).all()
        has_next = len(rows) > limit
        items = rows[:limit]

        next_cursor = None
        if has_next and items:
            last = items[-1]
            next_cursor = encode_cursor({
                "sort": sort_param,
                "values": {name: getattr(last, name) for name, _ in sort_fields}
            })

        return jsonify({
            "strategy": "cursor",
            "data": [b.to_dict() for b in items],
            "pagination": {
                "limit": limit,
                "has_next": has_next,
                "next_cursor": next_cursor
            }
        }), 200

    return jsonify({"error": "invalid_strategy", "message": "Use 'offset' or 'cursor'"}), 400


@bp.get("/books/<int:book_id>/reviews")
def list_reviews(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "not_found", "message": "Book not found"}), 404
    return jsonify({
        "book_id": book.id,
        "title": book.title,
        "reviews": [r.to_dict() for r in book.reviews]
    }), 200


@bp.post("/books/<int:book_id>/reviews")
def create_review(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "not_found", "message": "Book not found"}), 404

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "message": "Malformed JSON"}), 400

    try:
        validate(payload, REVIEW_SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400

    review = Review(
        rating=payload["rating"],
        comment=payload.get("comment"),
        book_id=book.id,
        user_id=payload["user_id"]
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201


@bp.get("/authors/<int:author_id>/books")
def list_author_books(author_id):
    author = db.session.get(Author, author_id)
    if not author:
        return jsonify({"error": "not_found", "message": "Author not found"}), 404
    return jsonify({
        "author": author.to_dict(),
        "books": [b.to_dict() for b in author.books]
    }), 200


@bp.post("/orders")
def create_order():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "message": "Malformed JSON"}), 400

    try:
        validate(payload, ORDER_SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400

    order = Order(
        user_id=payload["user_id"],
        status=payload.get("status", "pending")
    )
    for item in payload["items"]:
        order.items.append(OrderItem(
            book_id=item["book_id"],
            quantity=item["quantity"]
        ))

    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@bp.get("/orders/<int:order_id>")
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "not_found", "message": "Order not found"}), 404
    return jsonify(order.to_dict()), 200