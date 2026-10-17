from flask import Flask
from models import db, Category, Author, Book, User
from routes.books import bp as api_bp


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        if not Category.query.first():
            u1 = User(email="ben@vnu.edu.vn", display_name="Do Trung Hieu")
            c1 = Category(name="Technology", slug="tech")
            c2 = Category(name="Fiction", slug="fiction")
            a1 = Author(name="Martin Kleppmann", bio="Distributed systems researcher")
            a2 = Author(name="JJ Geewax", bio="Software engineer")
            db.session.add_all([u1, c1, c2, a1, a2])
            db.session.flush()

            b1 = Book(title="Designing Data-Intensive Applications", isbn="978-1449373320", price_vnd=450000, stock=12, category_id=c1.id, authors=[a1])
            b2 = Book(title="API Design Patterns", isbn="978-1617295850", price_vnd=380000, stock=8, category_id=c1.id, authors=[a2])
            b3 = Book(title="Clean Architecture", isbn="978-0134494166", price_vnd=320000, stock=20, category_id=c1.id, authors=[a1])
            db.session.add_all([b1, b2, b3])
            db.session.commit()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)