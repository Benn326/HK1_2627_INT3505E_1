import hashlib
import json
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 

BOOKS = [
    {"id": 1, "title": "Banh sinh nhat co cay nen", "author": "Spbook", "price": 50.0}
]

def generate_etag(book_dict):
    book_string = json.dumps(book_dict, sort_keys=True).encode('utf-8')
    return hashlib.md5(book_string).hexdigest()

@app.get("/books/<int:bid>")
def get_book(bid):
    book = next((b for b in BOOKS if b["id"] == bid), None)
    if not book:
        return jsonify(error="Not found"), 404
    etag = generate_etag(book)
    client_etag = request.headers.get("If-None-Match")
    if client_etag == etag:
        return "", 304

    resp = make_response(jsonify(book), 200)
    resp.headers["ETag"] = etag
    return resp

@app.patch("/books/<int:bid>")
def patch_book(bid):
    book = next((b for b in BOOKS if b["id"] == bid), None)
    req = request.get_json(silent=True) or {}
    
    if "price" in req:
        book["price"] = req["price"]
        
    return jsonify(book), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)