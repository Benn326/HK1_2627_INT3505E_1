import hashlib
import secrets
from datetime import datetime, timezone
from functools import wraps
import sqlite3
from flask import g, jsonify, request

DB_FILE = "api_keys.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix TEXT NOT NULL,
                hash TEXT NOT NULL UNIQUE,
                last4 TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                scopes TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                revoked_at TIMESTAMP NULL
            );
        """)
        conn.commit()


def mint_key(prefix: str, owner_id: int, scopes: list[str], expires_at=None) -> str:
    raw = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8]
    plain_key = f"{prefix}_{raw}_{digest}"
    
    hashed = hashlib.sha256(plain_key.encode()).hexdigest()
    last4 = plain_key[-4:]
    scopes_str = ",".join(scopes)
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO api_keys (prefix, hash, last4, owner_id, scopes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (prefix, hashed, last4, owner_id, scopes_str, expires_at)
        )
        conn.commit()
        
    return plain_key


def require_api_key(scopes=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = request.headers.get("X-Api-Key", "").strip()
            if not key:
                return jsonify({"error": "missing_api_key", "message": "Header X-Api-Key bi thieu"}), 401

            hashed = hashlib.sha256(key.encode()).hexdigest()
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            with get_db() as conn:
                row = conn.execute(
                    """
                    SELECT id, owner_id, scopes, revoked_at, expires_at 
                    FROM api_keys 
                    WHERE hash = ?
                    """,
                    (hashed,)
                ).fetchone()

            if not row:
                return jsonify({"error": "invalid_api_key", "message": "API key khong ton tai hoac sai"}), 401

            if row["revoked_at"] is not None:
                return jsonify({"error": "revoked_api_key", "message": "API key da bi thu hoi"}), 401

            if row["expires_at"] is not None and row["expires_at"] <= now:
                return jsonify({"error": "expired_api_key", "message": "API key da het han"}), 401

            granted = set(row["scopes"].split(","))
            if scopes and not set(scopes).issubset(granted):
                return jsonify({
                    "error": "insufficient_scope",
                    "message": "API key khong du quyen truy cap",
                    "required_scopes": scopes,
                    "granted_scopes": list(granted)
                }), 403

            g.api_key_id = row["id"]
            g.owner_id = row["owner_id"]
            g.api_scopes = granted

            return fn(*args, **kwargs)
        return wrapper
    return decorator