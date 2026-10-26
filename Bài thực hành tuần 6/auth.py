import sqlite3
from functools import wraps
from flask import g, jsonify
from flask_jwt_extended import get_jwt

DB_FILE = "orders.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def require_roles(*allowed):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_roles = set(g.current_user.get("roles", []))
            if not user_roles & set(allowed):
                return jsonify({
                    "error": "forbidden",
                    "message": "Người dùng không có vai trò phù hợp.",
                    "need_one_of": list(allowed),
                    "your_roles": list(user_roles)
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_scopes(*needed):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            granted = set(claims.get("scopes", []))
            if not set(needed).issubset(granted):
                return jsonify({
                    "error": "insufficient_scope",
                    "message": "Token thiếu phạm vi quyền hạn cần thiết.",
                    "need_all_of": list(needed),
                    "granted": list(granted)
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def user_owns_resource(param="id"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            resource_id = kwargs.get(param)
            with get_db() as conn:
                row = conn.execute(
                    "SELECT owner_id FROM orders WHERE id = ?",
                    (resource_id,)
                ).fetchone()

            if not row:
                return jsonify({
                    "error": "not_found",
                    "message": f"Không tìm thấy đơn hàng id={resource_id}."
                }), 404

            is_owner = str(row["owner_id"]) == str(g.current_user["id"])
            is_admin = "admin" in g.current_user.get("roles", [])

            if not is_owner and not is_admin:
                return jsonify({
                    "error": "forbidden",
                    "message": "BOLA Violated: Bạn không có quyền thao tác trên tài nguyên của người khác."
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator