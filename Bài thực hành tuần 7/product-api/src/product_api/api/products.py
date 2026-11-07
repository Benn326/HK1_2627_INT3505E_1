from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..extensions import db
from ..models import Product
from ..schemas import ProductOut

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


@products_bp.get("")
def list_products():
    try:
        page = max(1, int(request.args.get("page", 1)))
        size = min(100, max(1, int(request.args.get("size", 20))))
    except ValueError as err:
        raise ValidationError({"query": ["page and size must be integers"]}) from err

    base = db.select(Product).where(Product.archived.is_(False))
    rows = (
        db.session.execute(
            base.order_by(Product.id).offset((page - 1) * size).limit(size)
        )
        .scalars()
        .all()
    )
    total = db.session.scalar(
        db.select(db.func.count())
        .select_from(Product)
        .where(Product.archived.is_(False))
    )
    return jsonify({
        "items": [ProductOut().dump(p) for p in rows],
        "page": page,
        "size": size,
        "total": total,
    }), 200
