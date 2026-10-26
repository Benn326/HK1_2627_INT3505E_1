from flask import Flask, jsonify, g
from keys import init_db, mint_key, require_api_key

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/api/reports")
@require_api_key(scopes=["reports:read"])
def get_reports():
    return jsonify({
        "status": "success",
        "data": "Bao cao doanh thu thang nay",
        "caller": {
            "owner_id": g.owner_id,
            "api_key_id": g.api_key_id,
            "scopes": list(g.api_scopes)
        }
    }), 200


@app.post("/api/pay")
@require_api_key(scopes=["payments:write"])
def make_payment():
    return jsonify({
        "status": "success",
        "message": "Thanh toan thanh cong 500 000 VND",
        "owner_id": g.owner_id
    }), 200


if __name__ == "__main__":
    init_db()
    
    key_readonly = mint_key(prefix="sk_live", owner_id=101, scopes=["reports:read"])
    key_full = mint_key(prefix="sk_live", owner_id=102, scopes=["reports:read", "payments:write"])

    print("\n" + "=" * 65)
    print("DA TAO SAN 2 API KEYS MAU DE TEST:")
    print(f"Key 1 (chi xem bao cao): {key_readonly}")
    print(f"Key 2 (du quyen thanh toan + bao cao): {key_full}")
    print("=" * 65 + "\n")

    app.run(host="127.0.0.1", port=5000, debug=True)