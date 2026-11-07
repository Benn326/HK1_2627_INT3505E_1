from flask import Flask

from .api.products import products_bp
from .config import DefaultConfig
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or DefaultConfig)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(products_bp)
    return app
