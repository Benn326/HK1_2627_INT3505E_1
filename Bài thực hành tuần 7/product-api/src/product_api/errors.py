from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message="", code=None, status=None, detail=None):
        msg = detail if detail is not None else message
        super().__init__(msg)
        if code:
            self.code = code
        if status:
            self.status_code = status
        self.message = msg


class NotFound(ApiError):
    status_code = 404
    code = "not_found"


class Conflict(ApiError):
    status_code = 409
    code = "conflict"


class OutOfStock(Conflict):
    status_code = 409
    code = "out_of_stock"


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({
            "error": "validation_error",
            "detail": err.messages,
        }), 422

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify({
            "error": err.code,
            "detail": err.message,
        }), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({
            "error": err.name.lower().replace(" ", "_"),
            "detail": err.description,
        }), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("unhandled")
        return jsonify({
            "error": "internal_error",
            "detail": "Internal server error",
        }), 500
