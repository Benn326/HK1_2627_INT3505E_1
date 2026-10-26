import sqlite3
from datetime import timedelta
from flask import Flask, jsonify, g
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from auth import require_roles, require_scopes, user_owns_resource, DB_FILE

app = Flask(__name__)
app.json.ensure_ascii = False

app.config["JWT_SECRET_KEY"] = "super-secret-jwt-key-for-lab4-2026"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_ALGORITHM"] = "HS256"

jwt = JWTManager(app)


USERS_LOOKUP = {
    "1": {"id": 1, "email": "userA@vnu.edu.vn", "roles": ["customer"], "scopes": ["orders:write"]},
    "2": {"id": 2, "email": "userB@vnu.edu.vn", "roles": ["customer"], "scopes": ["orders:write"]},
    "3": {"id": 3, "email": "viewer@vnu.edu.vn", "roles": ["viewer"], "scopes": ["orders:read"]},
    "99": {"id": 99, "email": "admin@vnu.edu.vn", "roles": ["admin"], "scopes": ["orders:write", "orders:read"]}
}


def init_database():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            );
        """)
        conn.execute("DELETE FROM orders;")
        conn.execute("INSERT INTO orders (id, owner_id, item_name) VALUES (101, 1, 'LapTop Dell XPS');")
        
        conn.execute("INSERT INTO orders (id, owner_id, item_name) VALUES (202, 2, 'Ban phim co');")
        conn.commit()


@app.before_request
def load_current_user():
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity and str(identity) in USERS_LOOKUP:
            g.current_user = USERS_LOOKUP[str(identity)]
        else:
            g.current_user = {"id": None, "roles": []}
    except Exception:
        g.current_user = {"id": None, "roles": []}


@app.get("/api/auth/token/<user_id>")
def get_token(user_id):
    if user_id not in USERS_LOOKUP:
        return jsonify({"error": "user_not_found"}), 404
    u = USERS_LOOKUP[user_id]
    claims = {"roles": u["roles"], "scopes": u["scopes"]}
    token = create_access_token(identity=str(u["id"]), additional_claims=claims)
    return jsonify({
        "user": u["email"],
        "roles": u["roles"],
        "scopes": u["scopes"],
        "token": token
    }), 200


@app.delete("/api/orders/<int:id>")
@jwt_required()                        
@require_roles("customer", "admin")      
@require_scopes("orders:write")         
@user_owns_resource(param="id")         
def delete_order(id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM orders WHERE id = ?", (id,))
        conn.commit()
    return jsonify({
        "status": "success",
        "message": f"Đơn hàng {id} đã được xóa thành công bởi user_id={g.current_user['id']}."
    }), 200


if __name__ == "__main__":
    init_database()
    app.run(host="127.0.0.1", port=5000, debug=True)