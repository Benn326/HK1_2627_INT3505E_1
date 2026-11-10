from marshmallow import Schema, fields, validate


class OrderItemIn(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))


class OrderIn(Schema):
    items = fields.List(
        fields.Nested(OrderItemIn),
        required=True,
        validate=validate.Length(min=1),
    )


class OrderProductSummaryOut(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)


class OrderItemOut(Schema):
    id = fields.Int(dump_only=True)
    order_id = fields.Int(dump_only=True)
    product_id = fields.Int()
    quantity = fields.Int()
    unit_price_cents = fields.Int()
    product = fields.Nested(OrderProductSummaryOut, dump_only=True)


class OrderOut(Schema):
    id = fields.Int(dump_only=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemOut), dump_only=True)
