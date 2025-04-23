import json
from datetime import datetime
from BookStore import app, db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from flask_login import UserMixin


class UserEnum(RoleEnum):
    USER = 1
    ADMIN = 2

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)



class User(Base, UserMixin):
    __table_name__ = "users"
    name = Column(String(100))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    avatar = Column(String(300), default="https://res.cloudinary.com/dy1unykph/image/upload/v1740037805/apple-iphone-16-pro-natural-titanium_lcnlu2.webp")
    active = Column(Boolean, default=True)
    role = Column(Enum(UserEnum), default=UserEnum.USER)
    receipts = relationship('Receipt', backref="user", lazy=True)

def get_statistics_by_revenue():
    # Ví dụ dữ liệu giả
    return [
        {'product_name': 'Áo thể thao A', 'value': 5000000},
        {'product_name': 'Quần short B', 'value': 3000000},
        {'product_name': 'Giày chạy C', 'value': 7000000},
    ]

def get_statistics_by_frequency():
    return [
        {'product_name': 'Áo thể thao A', 'value': 120},
        {'product_name': 'Quần short B', 'value': 90},
        {'product_name': 'Giày chạy C', 'value': 150},
    ]

class Category(Base):
    name = Column(String(50), nullable=False, unique=True)
    products = relationship('Product', backref="category", lazy=True)



class Product(Base):
    # name = Column(String(100), nullable=False)
    # image = Column(String(300), default="https://res.cloudinary.com/dy1unykph/image/upload/v1740037805/apple-iphone-16-pro-natural-titanium_lcnlu2.webp")
    # price = Column(Float, default=0)
    # cate_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    # details = relationship('ReceiptDetail', backref='product', lazy=True)

    __tablename__ = 'product'
    name = Column(String(100), nullable=False)
    image = db.Column(String(500),
                   default="https://res.cloudinary.com/dy1unykph/image/upload/v1740037805/apple-iphone-16-pro-natural-titanium_lcnlu2.webp")
    price = Column(Float, default=0)
    cate_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    author = Column(String(100))
    sold = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    details = relationship('ReceiptDetail', backref='product', lazy=True)

    def __str__(self):
        return self.name

class Receipt(Base):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('ReceiptDetail', backref='receipt', lazy=True)


class ReceiptDetail(Base):
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)


if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        c1 = Category(name="Sách văn học")
        c2 = Category(name="Sách kinh tế")
        c3 = Category(name="Truyện tranh")

        db.session.add_all([c1, c2, c3])

        with open("data/products.json", encoding='utf-8') as f:
            products = json.load(f)
            for p in products:
                prod = Product(**p)
                db.session.add(prod)

        import hashlib
        u = User(name="User", username="user", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()))
        u2 = User(name="Hau Nguyen", username="admin", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),role=UserEnum.ADMIN)
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()