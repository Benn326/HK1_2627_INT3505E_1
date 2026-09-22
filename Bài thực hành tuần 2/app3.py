from flask import Flask, jsonify, request, make_response
import math

app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Banhsinhnhatphaiconen", "author": "xoat", "price": 29.99, "isbn": "9780132350884"},
    {"id": 2, "title": "Congchuacocaibua", "author": "goat", "price": 34.99, "isbn": "9780134494166"},
    {"id": 3, "title": "Congandanhdan", "author": "voat", "price": 39.99, "isbn": "9780135957059"},
    {"id": 4, "title": "Tiennumaccan", "author": "hoat", "price": 45.50, "isbn": "9780201633610"},
    {"id": 5, "title": "Nangkieulobuoc", "author": "doat", "price": 42.00, "isbn": "9780134757599"},
    {"id": 6, "title": "Hoangtulacloi", "author": "roat", "price": 38.50, "isbn": "9780596007126"}
]

DEFAULT_SIZE, MAX_SIZE = 2, 100

@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400
        
    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)
    
    flt = BOOKS
    a = request.args.get("author")
    if a: 
        flt = [b for b in flt if b["author"].lower() == a.lower()]
    
    q = (request.args.get("q") or "").lower()
    if q: 
        flt = [b for b in flt if q in b["title"].lower()]
        
    total = len(flt)
    start = (page - 1) * size
    end = start + size
    items = flt[start:end]
    last = max((total + size - 1) // size, 1) 
    
    def u(p): 
        return f"/books?page={p}&size={size}"
        
    links = {
        "self": {"href": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(last)}
    }
    if page > 1: 
        links["prev"] = {"href": u(page - 1)}
    if end < total: 
        links["next"] = {"href": u(page + 1)}
        
    body = {
        "data": items,
        "pagination": {"page": page, "size": size, "total": total, "total_pages": last},
        "_links": links
    }
    
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp

if __name__ == "__main__":
    app.run(host= "127.0.0.1", port=5000, debug=True)