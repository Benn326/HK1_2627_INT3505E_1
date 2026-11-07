import json
from pathlib import Path

from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["API_TITLE"] = "Product API"
app.config["API_VERSION"] = "1.0.0"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_JSON_PATH"] = "openapi.json"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

db = SQLAlchemy(app)


class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)


class ProductInSchema(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True)
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()


blp = Blueprint("products", __name__, url_prefix="/products")


@blp.route("")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return db.session.execute(db.select(Product)).scalars().all()

    @blp.arguments(ProductInSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        p = Product(**data)
        db.session.add(p)
        db.session.commit()
        return p


with app.app_context():
    db.create_all()

api = Api(app)
api.register_blueprint(blp)

spec_path = Path(__file__).with_name("openapi.json")
spec_path.write_text(
    json.dumps(api.spec.to_dict(), indent=2, ensure_ascii=False),
    encoding="utf-8",
)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
