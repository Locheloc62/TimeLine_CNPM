import hashlib
import json
from multiprocessing import connection

from flask import current_app, jsonify, request
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import cursor

from BookStore import db, app
from models import Category, Product, User, Receipt, ReceiptDetail
from flask_login import current_user
from sqlalchemy import func


def load_categories():
    with open("data/category.json", encoding='utf-8') as f:
        return json.load(f)
    return Category.query.all()


def update_product(id, name, price, sold):
    # Cập nhật sản phẩm trong cơ sở dữ liệu MySQL sử dụng SQLAlchemy
    product = Product.query.get(id)  # Truy vấn sản phẩm theo id

    if product:
        product.name = name
        product.price = price
        product.sold = sold

        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    else:
        print(f"Product with id {id} not found")

def update_receipt_detail(receipt_detail_id, product_id):
    # Kiểm tra xem product_id có hợp lệ không
    if product_id is None:
        return jsonify({'error': 'Product ID cannot be null'}), 400  # Trả về lỗi nếu product_id là None

    # Cập nhật receipt_detail trong cơ sở dữ liệu
    receipt_detail = ReceiptDetail.query.get(receipt_detail_id)
    if receipt_detail:
        receipt_detail.product_id = product_id
        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    else:
        return jsonify({'error': 'Receipt detail not found'}), 404





def add_receipt(cart):
    # Mở file sản phẩm
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Tạo dict để tra nhanh
    product_dict = {str(p['id']): p for p in products}

    # Cập nhật số lượng đã bán
    for product_id, item in cart.items():
        quantity = item['quantity']
        if product_id in product_dict:
            product_dict[product_id]['sold'] += quantity

    # Ghi lại file
    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(list(product_dict.values()), f, ensure_ascii=False, indent=2)

def get_db_connection():
    """Tạo kết nối tới cơ sở dữ liệu MySQL"""
    connection = mysql.connector.connect(
        host=current_app.config['DB_HOST'],  # Địa chỉ máy chủ MySQL
        user=current_app.config['DB_USER'],  # Tên người dùng MySQL
        password=current_app.config['DB_PASSWORD'],  # Mật khẩu MySQL
        database=current_app.config['DB_NAME']  # Tên cơ sở dữ liệu
    )
    return connection

def update_product(id, name, price, sold):
    # Cập nhật sản phẩm trong cơ sở dữ liệu MySQL
    conn = get_db_connection()  # Lấy kết nối với cơ sở dữ liệu
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = %s, price = %s, sold = %s
        WHERE id = %s
    """, (name, price, sold, id))
    conn.commit()
    cursor.close()
    conn.close()

def read_books():
    with open('data/books.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def write_books(books):
    with open('data/books.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=2, ensure_ascii=False)


    write_books(books)
    print('Cập nhật sold thành công!')


def add_user(name, username, password, avatar):
    u = User(name=name, username=username, password=str(hashlib.md5(password.encode('utf-8')).hexdigest()), avatar=avatar)
    db.session.add(u)
    db.session.commit()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def count_product():
    return Product.query.count()

def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()

def load_products(q=None, cate_id=None, page=None):
    with open("data/products.json", encoding='utf-8') as f:
        products = json.load(f)
        if q:
            products = [p for p in products if p['name'].find(q)>=0]
        if cate_id:
            products = [p for p in products if p['cate_id'].__eq__(int(cate_id))]

        return products
    query = Product.query

    if q:
        query = query.filter(Product.name.contains(q))
    if cate_id:
        query = query.filter(Product.cate_id.__eq__(cate_id))

    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page)-1)*size
        query = query.slice(start, start+size)

    return query.all()

def get_product_by_id(id):
    with open("data/products.json", encoding='utf-8') as f:
        products = json.load(f)
        for p in products:
            if p["id"].__eq__(id):
                return p
    return Product.query.get(id)

def count_product_by_cate():
    query = db.session.query(Category.id, Category.name, func.count(Product.id))\
        .join(Product, Product.cate_id.__eq__(Category.id), isouter=True).group_by(Category.id)

    print(query)

    return query.all()

def stats_revenue_by_products(kw=None):
    query = db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True)

    if kw:
        query = query.filter(Product.name.contains(kw))

    return query.group_by(Product.id).all()


def get_statistics_by_revenue():
    # Đọc dữ liệu sản phẩm từ file JSON
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Lấy thông tin doanh thu từ sản phẩm
    statistics = {
        'labels': [product['name'] for product in products],
        'values': [product['price'] * product['sold'] for product in products]  # Doanh thu = Giá x Số lượng bán
    }
    return statistics


def get_statistics_by_frequency():
    # Đọc dữ liệu sản phẩm từ file JSON
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Lấy thông tin tần suất bán hàng
    statistics = {
        'labels': [product['name'] for product in products],
        'values': [product['sold'] for product in products]  # Tần suất = Số lượng đã bán
    }
    return statistics


if __name__=="__main__":
    with app.app_context():
        print(stats_revenue_by_products())