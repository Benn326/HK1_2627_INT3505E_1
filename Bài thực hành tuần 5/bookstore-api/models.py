from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), primary_key=True)


class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    books: Mapped[list["Book"]] = relationship(back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Author(db.Model):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(500))

    books: Mapped[list["Book"]] = relationship(
        secondary="book_authors", back_populates="authors"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "bio": self.bio}


class Book(db.Model):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    price_vnd: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category | None"] = relationship(back_populates="books")
    authors: Mapped[list["Author"]] = relationship(
        secondary="book_authors", back_populates="books"
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="book")

    @classmethod
    def from_payload(cls, data: dict):
        book = cls(
            title=data["title"],
            isbn=data["isbn"],
            price_vnd=data["price_vnd"],
            stock=data.get("stock", 0),
            category_id=data.get("category_id")
        )
        if "author_ids" in data:
            authors = Author.query.filter(Author.id.in_(data["author_ids"])).all()
            book.authors = authors
        return book

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category": self.category.slug if self.category else None,
            "authors": [{"id": a.id, "name": a.name} for a in self.authors]
        }


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def to_dict(self):
        return {"id": self.id, "email": self.email, "display_name": self.display_name}


class Review(db.Model):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(500))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    book: Mapped["Book"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.comment,
            "book_id": self.book_id,
            "user_id": self.user_id
        }


class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="orders")