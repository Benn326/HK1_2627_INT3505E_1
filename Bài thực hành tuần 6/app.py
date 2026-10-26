import bcrypt
from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.json.ensure_ascii = False
auth = HTTPBasicAuth()

USERS_DB = {
    "an@vnu.edu.vn": bcrypt.hashpw(b"correct horse battery staple", bcrypt.gensalt()),
    "ben@vnu.edu.vn": bcrypt.hashpw(b"secret123", bcrypt.gensalt())
}

ORDERS_DB = {
    "an@vnu.edu.vn": [
        {"order_id": "ORD-001", "total_vnd": 450000, "status": "completed"},
        {"order_id": "ORD-002", "total_vnd": 320000, "status": "processing"}
    ],
    "ben@vnu.edu.vn": [
        {"order_id": "ORD-003", "total_vnd": 180000, "status": "shipped"}
    ]
}


@auth.verify_password
def verify_password(username, password):
    if not username or not password:
        return None
    if username not in USERS_DB:
        return None
    
    stored_hash = USERS_DB[username]
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    
    if bcrypt.checkpw(password_bytes, stored_hash):
        return username
    return None


@auth.error_handler
def on_auth_error(status):
    return (
        jsonify({
            "error": "unauthorized",
            "message": "Thông tin xác thực HTTP Basic Auth không hợp lệ hoặc bị thiếu."
        }),
        401,
        {"WWW-Authenticate": 'Basic realm="orders"'}
    )


@app.get("/api/orders")
@auth.login_required
def list_orders():
    current_user = auth.current_user()
    user_orders = ORDERS_DB.get(current_user, [])
    return jsonify({
        "principal": current_user,
        "orders": user_orders,
        "total_items": len(user_orders)
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)