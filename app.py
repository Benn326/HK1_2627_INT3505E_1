from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
app.json.ensure_ascii = False

STUDENTS = []

def find_student(student_id):
    return next((s for s in STUDENTS if s["id"] == student_id), None)

@app.route("/students", methods=["POST"])
def create_student():
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    
    if not name:
        return jsonify({"error": "Thuộc tính 'name' là bắt buộc!"}), 400
    student = {
        "id": str(uuid4()),
        "name": name,
        "gpa": body.get("gpa", 0.0),
        "status": body.get("status")
    }

    STUDENTS.append(student)
    return jsonify(student), 201, {"Location": f"/students/{student['id']}"}

@app.route("/students/<student_id>",methods=["GET"])
def get_student(student_id):
    student = find_student(student_id)
    if not student:
        return jsonify({"error": "ID không tồn tại"}), 404
    return jsonify(student), 200

@app.route("/students", methods=["GET"])
def list_students():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    results = STUDENTS
    if q:
        results = [s for s in STUDENTS if q in s["name"].lower()]

    return jsonify({"items": results[:limit]}), 200

@app.route("/students/<student_id>", methods=["PUT","DELETE"])
def modify_student(student_id):
    student = find_student(student_id)
    if not student:
        return jsonify({"error": "ID không tồn tại"}), 404

    if request.method == "PUT":
        body = request.get_json(silent=True) or {}

        student["name"] = body.get("name", student["name"])
        student["gpa"] = body.get("gpa", student["gpa"])
        student["status"] = body.get("status", student["status"])
        return jsonify(student), 200

    if student.get("status") == "graduate":
        return jsonify({"error": "Không thể xóa hồ sơ của sinh viên đã tốt nghiệp"}), 400


    STUDENTS.remove(student)
    return "", 204
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)