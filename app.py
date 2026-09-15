from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/status", methods=["GET"])
def check_status():
    return jsonify({"Shop:": "Đang mở", "Time": "8:00 - 22:00"}), 200

@app.route("/order", methods=["POST"])
def order():
    data = request.get_json(silent=True) or {}
    food = data.get("Item", "Mỳ cay 21724 cấp độ")
    return jsonify({"Message": f"Đã nhận đơn :{food}. Vui lòng chờ!"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000,debug=True )