from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from ..errors import Conflict, NotFound, OutOfStock
from ..extensions import db
from ..models import Product
from ..schemas import ProductIn, ProductOut, ReserveIn

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


@products_bp.post("")
def create_product():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError({"_schema": ["Invalid JSON body"]})
    body = ProductIn().load(payload)
    p = Product(**body)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        raise Conflict(message="sku already exists") from err
    return jsonify(ProductOut().dump(p)), 201


@products_bp.get("/<int:id>")
def get_product(id):
    stmt = db.select(Product).where(
        Product.id == id, Product.archived.is_(False)
    )
    p = db.session.scalar(stmt)
    if p is None:
        raise NotFound(message="product not found")
    return jsonify(ProductOut().dump(p)), 200


@products_bp.post("/<int:id>/reserve")
def reserve_product(id):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError({"_schema": ["Invalid JSON body"]})
    body = ReserveIn().load(payload)
    stmt = db.select(Product).where(
        Product.id == id, Product.archived.is_(False)
    )
    p = db.session.scalar(stmt)
    if p is None:
        raise NotFound(message="product not found")
    if p.qty_in_stock < body["qty"]:
        raise OutOfStock(message=f"only {p.qty_in_stock} left")
    p.qty_in_stock -= body["qty"]
    db.session.commit()
    return jsonify(ProductOut().dump(p)), 200
