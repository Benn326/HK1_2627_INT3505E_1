from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Banhsinhnhatphaiconen", "author": "xoat", "price": 29.99, "isbn": "9780132350884"},
    {"id": 2, "title": "Congchuacocaibua", "author": "goat", "price": 34.99, "isbn": "9780134494166"},
    {"id": 3, "title": "Congandanhdan", "author": "voat", "price": 39.99, "isbn": "9780135957059"},
    {"id": 4, "title": "Tiennumaccan", "author": "hoat", "price": 45.50, "isbn": "9780201633610"},
    {"id": 5, "title": "Nangkieulobuoc", "author": "doat", "price": 42.00, "isbn": "9780134757599"},
    {"id": 6, "title": "Hoangtulacloi", "author": "roat", "price": 38.50, "isbn": "9780596007126"}
]

@app.get("/books/<int:bid>")
def fetch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None: 
        return jsonify(error="not found"), 404
        
    resp = make_response(jsonify(BOOKS[i]), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    return resp

@app.put("/books/<int:bid>")
def put(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None: 
        return jsonify(error="not found"), 404
        
    p = request.get_json(silent=True) or {}
    t, a = p.get("title"), p.get("author")
    if not t or not a: 
        return jsonify(error="need title+author"), 422
        
    BOOKS[i] = {
        "id": bid, 
        "title": t.strip(), 
        "author": a.strip(),
        "isbn": p.get("isbn"), 
        "price": p.get("price")
    }
    return jsonify(BOOKS[i]), 200

@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None: 
        return jsonify(error="not found"), 404
        
    p = request.get_json(silent=True) or {}
    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422
        
    for k in "title author isbn price".split():
        if k in p: 
            BOOKS[i][k] = p[k]
    return jsonify(BOOKS[i]), 200

@app.delete("/books/<int:bid>")
def delete(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None: 
        return jsonify(error="not found"), 404
        
    BOOKS.pop(i)
    return "", 204 

if __name__ == "__main__":
    app.run(host= "127.0.0.1", port=5000, debug=True)