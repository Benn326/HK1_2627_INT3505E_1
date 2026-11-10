from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.orm import selectinload

from ..errors import NotFound
from ..extensions import db
from ..models import Order, OrderItem, Product
from ..schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


@orders_bp.get("")
def list_orders():
    try:
        page = max(1, int(request.args.get("page", 1)))
        size = min(100, max(1, int(request.args.get("size", 20))))
    except ValueError as err:
        raise ValidationError({"query": ["page and size must be integers"]}) from err

    stmt = (
        db.select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.id)
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = db.session.execute(stmt).scalars().all()
    total = db.session.scalar(db.select(db.func.count()).select_from(Order))
    return jsonify({
        "items": [OrderOut().dump(o) for o in rows],
        "page": page,
        "size": size,
        "total": total,
    }), 200


@orders_bp.get("/<int:id>")
def get_order(id):
    stmt = (
        db.select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == id)
    )
    order = db.session.scalar(stmt)
    if order is None:
        raise NotFound(message="order not found")
    return jsonify(OrderOut().dump(order)), 200


@orders_bp.post("")
def create_order():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError({"_schema": ["Invalid JSON body"]})
    body = OrderIn().load(payload)

    product_ids = {item["product_id"] for item in body["items"]}
    stmt = db.select(Product).where(
        Product.id.in_(product_ids), Product.archived.is_(False)
    )
    products = {
        p.id: p for p in db.session.execute(stmt).scalars().all()
    }

    for item in body["items"]:
        pid = item["product_id"]
        if pid not in products:
            raise NotFound(message=f"product {pid} not found")

    order = Order(status="pending")
    for item in body["items"]:
        product = products[item["product_id"]]
        order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=item["quantity"],
                unit_price_cents=product.price_cents,
            )
        )

    db.session.add(order)
    db.session.commit()
    return jsonify(OrderOut().dump(order)), 201
