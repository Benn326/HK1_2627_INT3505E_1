from contextlib import contextmanager

import pytest
from sqlalchemy import event

from product_api.config import TestConfig
from product_api.extensions import db
from product_api.factory import create_app


class QueryCounter:
    def __init__(self):
        self.statements = []

    @property
    def count(self) -> int:
        return len(self.statements)

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        sql = statement.strip().upper()
        if sql.startswith("SELECT"):
            self.statements.append(statement)


@contextmanager
def count_select_queries(engine):
    counter = QueryCounter()
    event.listen(engine, "before_cursor_execute", counter.callback)
    try:
        yield counter
    finally:
        event.remove(engine, "before_cursor_execute", counter.callback)


@pytest.fixture()
def query_counter(app):
    return lambda: count_select_queries(db.engine)


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
