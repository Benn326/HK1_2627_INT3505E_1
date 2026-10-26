from datetime import timedelta
import bcrypt
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

app = Flask(__name__)
app.json.ensure_ascii = False

app.config["JWT_SECRET_KEY"] = "super-secret-jwt-key-256bit-min-length-security"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["JWT_ALGORITHM"] = "HS256"

jwt = JWTManager(app)
REVOKED_JTIS = set()

USERS_DB = {
    "an@vnu.edu.vn": {
        "id": "1",
        "email": "an@vnu.edu.vn",
        "pwd_hash": bcrypt.hashpw(b"secret123", bcrypt.gensalt()),
        "roles": ["customer"],
        "scopes": ["orders:read"],
    },
    "admin@vnu.edu.vn": {
        "id": "2",
        "email": "admin@vnu.edu.vn",
        "pwd_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()),
        "roles": ["admin"],
        "scopes": ["orders:read", "orders:write"],
    },
}

ORDERS_DB = {
    "1": [
        {"order_id": "ORD-001", "total_vnd": 450000, "status": "completed"}
    ],
    "2": [
        {"order_id": "ORD-002", "total_vnd": 1200000, "status": "processing"}
    ],
}


def load_permissions(user_id: str) -> dict:
    for user in USERS_DB.values():
        if user["id"] == user_id:
            return {"roles": user["roles"], "scopes": user["scopes"]}
    return {"roles": [], "scopes": []}


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in REVOKED_JTIS


@jwt.unauthorized_loader
def missing_token_callback(error_string):
    return jsonify({"error": "authorization_required", "message": error_string}), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "token_revoked", "message": "Token này đã bị thu hồi/vô hiệu hóa."}), 401


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password", "")

    user = USERS_DB.get(email)
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["pwd_hash"]):
        return jsonify({"error": "invalid_credentials", "message": "Sai email hoặc mật khẩu"}), 401

    uid = user["id"]
    claims = load_permissions(uid)

    access_token = create_access_token(identity=uid, additional_claims=claims)
    refresh_token = create_refresh_token(identity=uid, additional_claims=claims)

    return jsonify({
        "status": "success",
        "access": access_token,
        "refresh": refresh_token,
        "expires_in_minutes": 15
    }), 200


@app.get("/api/orders")
@jwt_required()
def list_orders():
    uid = get_jwt_identity()
    claims = get_jwt()
    granted_scopes = claims.get("scopes", [])

    if "orders:read" not in granted_scopes:
        return jsonify({
            "error": "insufficient_scope",
            "message": "Thiếu scope 'orders:read' để thực hiện hành động này"
        }), 403

    user_orders = ORDERS_DB.get(uid, [])
    return jsonify({
        "principal_id": uid,
        "granted_scopes": granted_scopes,
        "orders": user_orders
    }), 200


@app.post("/api/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    current_uid = get_jwt_identity()
    claims = load_permissions(current_uid)
    new_access_token = create_access_token(identity=current_uid, additional_claims=claims)
    return jsonify({"access": new_access_token}), 200

@app.post("/api/auth/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    REVOKED_JTIS.add(jti)
    return jsonify({"status": "success", "message": "Đăng xuất thành công, token đã bị vô hiệu hóa."}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)