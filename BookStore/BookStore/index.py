import math
from datetime import datetime
from flask import render_template, request, redirect, session, jsonify
import dao, utils
from BookStore import app, login, admin
from flask_login import login_user, current_user, logout_user, login_required
import cloudinary.uploader
from flask import flash, redirect, session
from flask import Blueprint, jsonify, request
from models import get_statistics_by_revenue, get_statistics_by_frequency

@app.route('/')
def index():
    q = request.args.get("q")
    cate_id = request.args.get("category_id")
    page = request.args.get("page")
    products = dao.load_products(q=q, cate_id=cate_id, page=page)
    return render_template("index.html", products=products, pages=int(math.ceil(dao.count_product()/app.config["PAGE_SIZE"])))
api = Blueprint('api', __name__)

# Dữ liệu mẫu
products = [
    {
        "id": 1, "name": "Đắc nhân tâm", "price": 200000, "sold": 1500,
    },
    {
        "id": 2, "name": "Bồ câu không đưa thư", "price": 120000, "sold": 720,
    },
    {
        "id": 3, "name": "Cha nghèo cha giàu", "price": 220000, "sold": 2300,
    },
    {
        "id": 4, "name": "Doreamon", "price": 110000, "sold": 3500,
    },
    {
        "id": 5, "name": "Mắt biếc", "price": 100000, "sold": 1800,
    },
    {
        "id": 6, "name": "Tôi là Bê tô", "price": 110000, "sold": 1050,
    },
    {
        "id": 7, "name": "Bán bạc cắt thu bạc tỷ", "price": 150000, "sold": 980,
    },
    {
        "id": 8, "name": "Conan", "price": 100000, "sold": 4100,
    },
    {
        "id": 9, "name": "Trạng Quỳnh", "price": 90000, "sold": 1600,
    },
    {
        "id": 10, "name": "Naruto", "price": 90000, "sold": 5000,
    },
    {
        "id": 11, "name": "Think and grow rich", "price": 200000, "sold": 3000,
    },
    {
        "id": 12, "name": "Sổ tay kinh doanh", "price": 210000, "sold": 750,
    }
]


@app.route('/api/statistics', methods=['GET'])
def statistics():
    stat_type = request.args.get('statType')  # Loại thống kê: revenue hoặc frequency
    month = request.args.get('month')  # Tháng cần thống kê theo định dạng 'YYYY-MM'

    labels = []  # Tên sản phẩm
    values = []  # Giá trị thống kê

    # Dữ liệu mẫu
    products = [
        {"id": 1, "name": "Đắc nhân tâm", "price": 200000, "sold": 1500, "date_sold": '2025-03-01'},
        {"id": 2, "name": "Bồ câu không đưa thư", "price": 120000, "sold": 720, "date_sold": '2025-03-05'},
        {"id": 3, "name": "Cha nghèo cha giàu", "price": 220000, "sold": 2300, "date_sold": '2025-03-10'},
        {"id": 4, "name": "Doreamon", "price": 110000, "sold": 3500, "date_sold": '2025-03-12'},
        {"id": 5, "name": "Mắt biếc", "price": 100000, "sold": 1800, "date_sold": '2025-03-20'},
        {"id": 6, "name": "Tôi là Bê tô", "price": 110000, "sold": 1050, "date_sold": '2025-03-22'},
        {"id": 7, "name": "Bán bạc cắt thu bạc tỷ", "price": 150000, "sold": 980, "date_sold": '2025-03-25'},
        {"id": 8, "name": "Conan", "price": 100000, "sold": 4100, "date_sold": '2025-03-28'},
        {"id": 9, "name": "Trạng Quỳnh", "price": 90000, "sold": 1600, "date_sold": '2025-03-15'},
        {"id": 10, "name": "Naruto", "price": 90000, "sold": 5000, "date_sold": '2025-03-18'},
        {"id": 11, "name": "Think and grow rich", "price": 200000, "sold": 3000, "date_sold": '2025-03-11'},
        {"id": 12, "name": "Sổ tay kinh doanh", "price": 210000, "sold": 750, "date_sold": '2025-03-23'}
    ]

    # Lọc sản phẩm theo tháng
    filtered_products = [p for p in products if p['date_sold'].startswith(month)]

    for product in filtered_products:
        labels.append(product['name'])
        if stat_type == 'revenue':
            values.append(product['price'] * product['sold'])  # Doanh thu = giá * số lượng bán
        elif stat_type == 'frequency':
            values.append(product['sold'])  # Tần suất bán = số lượng bán
        else:
            return jsonify({'error': 'Invalid statType'}), 400

    return jsonify({
        'labels': labels,
        'values': values
    })

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id=user_id)
@app.route('/products/<int:id>')
def details(id):
    prod = dao.get_product_by_id(id)

    categories = {
        1: "Sách văn học",
        2: "Sách kinh tế",
        3: "Truyện tranh"
    }
    category_name = categories.get(prod['cate_id'], 'Không rõ')

    return render_template('product-details.html', prod=prod, category_name=category_name)

@app.route('/order-now/<int:prod_id>', methods=['POST'])
def order_now(prod_id):
    prod = dao.get_product_by_id(prod_id)
    if prod:
        cart = session.get("cart", {})
        id = str(prod['id'])

        if id in cart:
            cart[id]['quantity'] += 1
        else:
            cart[id] = {
                'id': prod['id'],
                'name': prod['name'],
                'price': prod['price'],
                'quantity': 1
            }

        session['cart'] = cart
        flash(f"✅ Đã thêm sản phẩm \"{prod['name']}\" vào giỏ hàng thành công!")

    return redirect('/cart')
@app.context_processor
def common_attributes():
    return {
        "cates": dao.load_categories(),
        "cart_stats": utils.cart_stats(session.get('cart'))
    }

@app.route('/login', methods=['get', 'post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None
    next = None
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user)
            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không khớp!"

    return render_template('login.html', err_msg=err_msg)

@app.route('/login-admin', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user)
    else:
        err_msg = "Tài khoản hoặc mật khẩu không khớp!"
    return redirect('/admin')

# @app.route('/api/statistics')
# def statistics():
#     type = request.args.get('type')
#
#     if type == 'revenue':
#         statistics = dao.get_statistics_by_revenue()
#     elif type == 'frequency':
#         statistics = dao.get_statistics_by_frequency()
#     else:
#         return jsonify({'error': 'Invalid type'}), 400
#
#     return jsonify(statistics)

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route('/staff')
@login_required
def staff():
    # Accessing the current user's role
    role = current_user.role if hasattr(current_user, 'role') else 'Chưa xác định'

    # Rendering the staff page and passing the role
    return render_template('staff/staff.html', role=role)


@app.route('/WM')
@login_required
def wm():
    # Accessing the current user's role
    role = current_user.role if hasattr(current_user, 'role') else 'Chưa xác định'

    # Rendering the WM page and passing the role
    return render_template('WM/WM.html', role=role)

@app.route("/register", methods=['GET','POST'])
def register():
    err_msg = None
    if request.method.__eq__("POST"):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            name = request.form.get('name')
            username = request.form.get('username')
            avatar = request.files.get('avatar')
            path = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                path = res['secure_url']
            dao.add_user(name, username, password, path)
            return redirect('/login')
        else:
            err_msg = "Mật khẩu không khớp!"
    return render_template('register.html', err_msg=err_msg)


@app.route('/api/carts', methods=['post'])
def add_to_cart():
    """
    {
        "cart": {
            "1": {
                "id": 1,
                "name": "",
                "price": 1000,
                "quantity": 2
            },
            "2": {
                "id": 1,
                "name": "",
                "price": 2000,
                "quantity": 1
            }
        }
    }

    :return:
    """
    cart = session.get("cart")

    if not cart:
        cart = {}

    id = str(request.json.get("id"))

    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            'id': id,
            'name': request.json.get("name"),
            'price': request.json.get("price"),
            "quantity": 1
        }

    session['cart'] = cart

    print(session)

    return jsonify(utils.cart_stats(cart))

@app.route('/api/cart/<id>', methods=['delete'])
def delete_cart(id):
    cart = session['cart']
    if cart and id in cart:
        del cart[id]
        session['cart'] = cart

    return jsonify(utils.cart_stats(cart))

@app.route('/api/cart/<id>', methods=['put'])
def update_cart(id):
    cart = session.get('cart')

    if cart and id in cart:
        cart[id]['quantity'] = request.json.get('quantity')
        session['cart'] = cart

    return jsonify(utils.cart_stats(cart))

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    cart = session.get('cart', {})

    try:
        dao.add_receipt(cart)
    except Exception as ex:
        print(ex)
        return jsonify({'status': 500})
    else:
        del session['cart']
        return jsonify({'status': 200})
app.register_blueprint(api)

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
