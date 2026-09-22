import sqlite3
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
DB_FILE = "books.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                price REAL
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY, 
                total REAL NOT NULL,
                status TEXT NOT NULL
            );
        """)

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/books")
def list_books():
    with get_db_connection() as conn:
        books = conn.execute("SELECT * FROM books").fetchall()
        result = [dict(b) for b in books]
    return jsonify({"data": result, "total": len(result)}), 200

@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
        
    p = request.get_json(silent=True) or {}
    t, a = (p.get("title") or "").strip(), (p.get("author") or "").strip()
    isbn, price = p.get("isbn"), p.get("price")
    
    if not t or not a:
        return jsonify(error="title and author required"), 422
        
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO books (title, author, isbn, price) VALUES (?, ?, ?, ?)", 
            (t, a, isbn, price)
        )
        conn.commit()
        new_id = cursor.lastrowid
        
    book = {"id": new_id, "title": t, "author": a, "isbn": isbn, "price": price}
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{new_id}"
    return resp

@app.get("/books/<int:bid>")
def get_book(bid):
    with get_db_connection() as conn:
        book = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
        
    if book is None:
        return jsonify(error="not found"), 404
        
    resp = make_response(jsonify(dict(book)), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    return resp

@app.put("/books/<int:bid>")
def put_book(bid):
    p = request.get_json(silent=True) or {}
    t, a = p.get("title"), p.get("author")
    
    if not t or not a: 
        return jsonify(error="need title+author"), 422

    with get_db_connection() as conn:
        existing = conn.execute("SELECT id FROM books WHERE id = ?", (bid,)).fetchone()
        if existing is None:
            return jsonify(error="not found"), 404
        conn.execute("""
            UPDATE books 
            SET title = ?, author = ?, isbn = ?, price = ?
            WHERE id = ?
        """, (t.strip(), a.strip(), p.get("isbn"), p.get("price"), bid))
        conn.commit()
        updated = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
        return jsonify(dict(updated)), 200

@app.patch("/books/<int:bid>")
def patch_book(bid):
    p = request.get_json(silent=True) or {}
    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422
        
    with get_db_connection() as conn:
        existing = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
        if existing is None:
            return jsonify(error="not found"), 404
            
        fields = []
        values = []
        for k in ["title", "author", "isbn", "price"]:
            if k in p:
                fields.append(f"{k} = ?")
                values.append(p[k])
                
        if fields:
            values.append(bid)
            query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
            
        updated = conn.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
        return jsonify(dict(updated)), 200

@app.delete("/books/<int:bid>")
def delete_book(bid):
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM books WHERE id = ?", (bid,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify(error="not found"), 404
            
    return "", 204 

@app.get("/orders/<oid>")
def get_order(oid):
    with get_db_connection() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        
    if order is None:
        return jsonify(error="order not found"), 404
        
    return jsonify(dict(order)), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)