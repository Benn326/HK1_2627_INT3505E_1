from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
app.json.ensure_ascii = False

STUDENTS = []

@app.route("/students", methods=["POST"])
def create_student():
    body = request.get_json(silent=True) or {}
    name = body.get("name")

    if not name:
        return jsonify({"error": "Thuộc tính 'name' là bắt buộc!"}), 400

    student = {
        "id": str(uuid4()),
        "name": name,
        "gpa": body.get("gpa", 0.0)
    }

    STUDENTS.append(student)
    return jsonify(student), 201

@app.route("/students/<student_id>",methods=["GET"])
def get_student(student_id):
    for student in STUDENTS:
        if student["id"] == student_id:
            return jsonify(student), 200
    return jsonify({"error": "ID không tồn tại"}), 404

@app.route("/students", methods=["GET"])
def list_students():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    results = STUDENTS
    if q:
        results = [s for s in STUDENTS if q in s["name"].lower()]

    return jsonify({"items": results[:limit]}), 200
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)