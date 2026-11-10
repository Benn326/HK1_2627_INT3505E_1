from flask import Blueprint, jsonify
from sqlalchemy import text

from ..extensions import db

health_bp = Blueprint("health", __name__, url_prefix="")


@health_bp.get("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200


@health_bp.get("/ready")
def readiness():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ready", "database": "ok"}), 200
    except Exception:
        return jsonify({"status": "not_ready", "database": "unavailable"}), 503
