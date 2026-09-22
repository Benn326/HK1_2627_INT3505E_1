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
    gpa = body.get("gpa", 0.0) 
    
   
    if not isinstance(gpa, (int, float)) or not (0.0 <= gpa <= 4.0):
        return jsonify({"error": " 'gpa' bắt buộc là số và nằm trong khoảng 0.0 - 4.0"}), 400

    if not name:
        return jsonify({"error": "Thuộc tính 'name' là bắt buộc!"}), 400
        
    student = {
        "id": str(uuid4()),
        "name": name,
        "gpa": float(gpa),
        "status": body.get("status", "studying")
    }

    STUDENTS.append(student)
    return jsonify(student), 201, {"Location": f"/students/{student['id']}"}

@app.route("/students", methods=["GET"])
def list_students():
    limit = int(request.args.get("limit", 20))
    
    q = request.args.get("q", "").strip().lower()          
    sort_by = request.args.get("sort", "").strip().lower() 
    
    results = STUDENTS
    
    if q:
        results = [s for s in STUDENTS if q in s["name"].lower()]
        
    if sort_by == "name":
        results = sorted(results, key=lambda x: x["name"].lower())
    elif sort_by == "gpa":
        results = sorted(results, key=lambda x: x["gpa"], reverse=True)

    return jsonify({"items": results[:limit]}), 200

@app.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    student = find_student(student_id)
    if not student:
        return jsonify({"error": "ID không tồn tại"}), 404
    return jsonify(student), 200

@app.route("/students/<student_id>", methods=["PUT", "DELETE"])
def modify_student(student_id):
    student = find_student(student_id)
    if not student:
        return jsonify({"error": "ID không tồn tại"}), 404

    if request.method == "PUT":
        body = request.get_json(silent=True) or {}
        
        new_gpa = body.get("gpa", student["gpa"])
        if not isinstance(new_gpa, (int, float)) or not (0.0 <= new_gpa <= 4.0):
            return jsonify({"error": "Trường 'gpa' bắt buộc là số và nằm trong khoảng 0.0 - 4.0"}), 400
            
        student["name"] = body.get("name", student["name"])
        student["gpa"] = float(new_gpa)
        student["status"] = body.get("status", student["status"])
        return jsonify(student), 200

    if student.get("status") == "graduate":
        return jsonify({"error": "Không thể xóa hồ sơ của sinh viên đã tốt nghiệp"}), 409

    STUDENTS.remove(student)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)