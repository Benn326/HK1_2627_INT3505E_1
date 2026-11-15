"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
import pytest
from copy import deepcopy
from jsonschema import validate, ValidationError
from tools import get_book_schema


def test_list_books_empty(client):
    res = client.get("/books")

    assert res.status_code == 200
    assert res.get_json() == []


def test_get_book_not_found(client):
    res = client.get("/books/9999")

    assert res.status_code == 404
    assert res.get_json()["code"] == "NOT_FOUND"


def test_create_book_missing_title(client):
    res = client.post("/books", json={
        "author": "Test Author"
    })

    assert res.status_code == 400

    data = res.get_json()
    assert any(
        item.get("field") == "title"
        for item in data.get("errors", [])
    )


def test_delete_book_then_get_404(client):
    created = client.post("/books", json={
        "title": "Test Book",
        "author": "Test Author",
        "year": 2024
    })

    assert created.status_code == 201

    book_id = created.get_json()["id"]

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204

    res = client.get(f"/books/{book_id}")
    assert res.status_code == 404
    assert res.get_json()["code"] == "NOT_FOUND"

def test_book_response_rejects_unknown_fields(client, sample_book):
    res = client.get(f"/books/{sample_book}")

    assert res.status_code == 200
    book = res.get_json()

    schema = deepcopy(get_book_schema())

    schema["properties"]["year"] = {
        "type": ["integer", "null"]
    }

    schema["properties"]["isbn"] = {
        "type": ["string", "null"],
        "pattern": "^\\d{13}$"
    }

    validate(instance=book, schema=schema)

    invalid_book = dict(book)
    invalid_book["password_hash"] = "secret"

    with pytest.raises(ValidationError):
        validate(instance=invalid_book, schema=schema)
