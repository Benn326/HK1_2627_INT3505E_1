from flask import Flask

from . import models  # noqa: F401
from .api.orders import orders_bp
from .api.products import products_bp
from .config import DefaultConfig
from .errors import register_error_handlers
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or DefaultConfig)
    db.init_app(app)
    migrate.init_app(app, db)
    register_error_handlers(app)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    return app
