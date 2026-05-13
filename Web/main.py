# flask
from flask import Flask, request, make_response, render_template, redirect, abort, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource

# waitress
from waitress import serve

# sqlalchemy
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import or_
from unicodedata import category

# import from data
from data import db_session
from data.users import User
from data.products import Product
from data.orders import Order
from data.carts import Cart
from data.eateries import Eatery

# datetime
import datetime as dt

# secrets
import secrets

# werkzeug
from werkzeug.utils import secure_filename

# requests
import requests

# import from forms
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.create_order import CreateOrderForm
from forms.add_address import AddAddressForm
from forms.add_product import AddProductForm
from forms.currier_selection import CurrierSelectionForm

# import API resource
import users_resource
import products_resuorce
import orders_resource

# for .env
import os
from dotenv import load_dotenv


# import .env
load_dotenv('*.env')
API_KEY = os.getenv('SECRET_API_KEY')

app = Flask(__name__)
# configuration setting
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static')
# api
api = Api(app)
# add user resources
api.add_resource(users_resource.UserResource, '/api/users/<int:user_id>')
api.add_resource(users_resource.UserListResource, '/api/users')
# add product resources
api.add_resource(products_resuorce.ProductResource, '/api/products/<int:product_id>')
api.add_resource(products_resuorce.ProductListResource, '/api/products')
# add order resources
api.add_resource(orders_resource.OrderResource, '/api/orders/<int:order_id>')
api.add_resource(orders_resource.OrderListResource, '/api/orders')

db_session.global_init('db/data_delivery.sqlite3')

login_manager = LoginManager()
login_manager.init_app(app)

# host
HOST = '0.0.0.0'
PORT = '5000'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    us = db_sess.get(User, user_id, options=[joinedload(User.cart), joinedload(User.eatery)])
    db_sess.close()
    return us


def main():
    # app.run(host=HOST, port=PORT)
    serve(app, host=HOST, port=PORT)


@app.route('/')
def home():
    sess = db_session.create_session()
    prod = sess.query(Product).all()
    sess.close()
    if current_user.is_authenticated:
        if current_user.access == 1:
            return redirect('/currier')
        if current_user.access == 2:
            return redirect('/eatery')
        return render_template('shop.html', products=prod)
    return render_template('shop.html', products=prod)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            db_sess.close()
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            access=0,
            addresses={'addresses': []}
        )
        if form.address.data is not None and form.address.data != "":
            user.addresses['addresses'].append(form.address.data)
        user.set_password(form.password.data)
        cart = Cart(user_id=user.id)
        user.cart = cart
        db_sess.add(user)
        db_sess.add(cart)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/cart')
def cart():
    sess = db_session.create_session()
    products = []
    for prod in sess.query(Product).filter(Product.id.in_([int(x) for x in current_user.cart.products.keys()])).all():
        products.append(prod)
    sess.close()
    return render_template('cart.html', products=products, cart=current_user.cart)


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    db_sess = db_session.create_session()
    cart = db_sess.get(Cart, current_user.cart.id)
    cart.products[product_id] = 1
    cart.price += db_sess.get(Product, product_id).price
    db_sess.commit()
    db_sess.close()
    return redirect("/")


@app.route('/update_cart', methods=['GET', 'POST'])
def update_cart():
    if request.method == 'POST':
        sess = db_session.create_session()
        data = request.get_json()
        p_id = str(data.get('product_id'))
        quan = int(data.get('quantity'))
        cart = sess.get(Cart, current_user.cart.id)
        cart.price += (quan - cart.products[p_id]) * sess.get(Product, p_id).price
        cart.products[p_id] = quan
        current_cart_price = cart.price
        sess.commit()
        sess.close()
        return jsonify({
            "status": "success",
            "new_total_price": current_cart_price
        }), 200
    return redirect('/')


@app.route('/remove_from_cart/<product_id>')
def remove_from_cart(product_id):
    sess = db_session.create_session()
    cart = sess.get(Cart, current_user.cart.id)
    cart.price -= cart.products[product_id] * sess.get(Product, product_id).price
    cart.products.pop(product_id, None)
    sess.commit()
    sess.close()
    return redirect('/cart')


@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    form = CreateOrderForm()
    sess = db_session.create_session()
    for address in current_user.addresses['addresses']:
        form.address_to_order.choices.append((address, address))
    for eatery in sess.query(Eatery).all():
        form.address_eatery.choices.append((eatery.address, eatery.address))
    sess.close()
    if form.validate_on_submit():
        if form.address_to_order.data == '' and form.addresses_eateries.data == '':
            return render_template('create_order.html', messege='Не указан адрес', form=form)
        if form.payment_type.data == 'cash' and form.cash.data == 0:
            return render_template('create_order.html', messege='Не указан размер оплаты', form=form)
        if form.type.data == 'delivery':
            address = form.address_to_order.data
        else:
            address = form.addresses_eateries.data
        sess = db_session.create_session()
        order = Order(
            client=current_user.id,
            products=current_user.cart.products,
            price=current_user.cart.price,
            type=form.type.data,
            payment_type=form.payment_type.data,
            address=address
        )
        sess.add(order)
        cart = sess.get(Cart, current_user.cart.id)
        cart.products = {}
        cart.price = 0
        sess.commit()
        sess.close()
        return redirect("/")
    return render_template('create_order.html', form=form)


@app.route('/add_address', methods=['GET', 'POST'])
def add_address():
    form = AddAddressForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.get(User, current_user.id)
        user.addresses['addresses'].append(form.address.data)
        flag_modified(user, "addresses")
        db_sess.commit()
        db_sess.close()
        return redirect("/")
    return render_template('add_address.html', form=form)


@app.route('/currier')
@login_required
def currier_home():
    if current_user.access != 1:
        return redirect('/')
    db_sess = db_session.create_session()

    orders = db_sess.query(Order).filter(Order.delivery_man == current_user.id,
                                         Order.is_complete == 0).all()

    orders_with_products = []
    for order in orders:
        product_ids = [int(pid) for pid in order.products.keys()] if order.products else []

        products = db_sess.query(Product).filter(Product.id.in_(product_ids)).all()

        if not order.is_complete:
            orders_with_products.append({
                'order': order,
                'products': products
            })

    db_sess.close()
    return render_template('currier_home.html', orders_data=orders_with_products)


@app.route('/complete_order/<int:order_id>')
def complete_order(order_id):
    sess = db_session.create_session()
    order = sess.get(Order, order_id)
    order.is_complete = True
    sess.commit()
    sess.close()
    return redirect('/')


@app.route('/currier/profile')
def currier_profile():
    if current_user.access != 1:
        return redirect('/')
    sess = db_session.create_session()
    com_or = len(sess.query(Order).filter(Order.delivery_man == current_user.id, Order.is_complete).all())
    ncom_or = len(sess.query(Order).filter(Order.delivery_man == current_user.id, not Order.is_complete).all())
    return render_template('currier_profile.html', com_or=com_or, ncom_or=ncom_or)


@app.route('/eatery')
@login_required
def eatery_home():
    if current_user.access != 2:
        return redirect('/')
    sess = db_session.create_session()
    eatery_address = current_user.eatery.address if current_user.eatery else None
    orders = []
    orders_with_products = []
    for order in sess.query(Order).filter(or_((Order.type == 'pickup') & (Order.address == eatery_address),
                                              Order.type == 'delivery')).all():
        product_ids = [int(pid) for pid in order.products.keys()] if order.products else []

        products = sess.query(Product).filter(Product.id.in_(product_ids)).all()

        if not order.is_complete:
            orders_with_products.append({
                'order': order,
                'products': products,
                'currier': order.del_men
            })

    sess.close()
    return render_template('eatery_home.html', orders_data=orders_with_products)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            sess = db_session.create_session()

            product = Product(name=form.name.data,
                              category=form.category.data,
                              cost_price=form.cost_price.data,
                              price=form.price.data,
                              markup=(((form.price.data - form.cost_price.data) / form.cost_price.data) * 100)
                              )

            file = form.image.data

            # Получаем расширение оригинального файла (например, '.jpg')
            _, f_ext = os.path.splitext(secure_filename(file.filename))

            # Генерируем случайное имя из 16 шестнадцатеричных символов + расширение
            filename = secrets.token_hex(8) + f_ext

            # Полный путь для сохранения файла
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            product.image = filename
            sess.add(product)
            sess.commit()
            sess.close()
            return redirect('/')
    return render_template('add_product.html', form=form)


@app.route('/currier_selection/<int:order_id>', methods=['GET', 'POST'])
def currier_selection(order_id):
    form = CurrierSelectionForm()
    sess = db_session.create_session()
    for currier in sess.query(User).filter(User.access == 1):
        form.currier.choices.append((currier.id, currier.name))
    if form.validate_on_submit():
        if form.currier.data == '':
            return render_template('currier_selection.html', form=form, message='Необходимо указать Курьера')
        order = sess.get(Order, order_id)
        currier = sess.get(User, form.currier.data)
        currier.orders_deliver.append(order)
        order.delivery_man = form.currier.data
        order.del_men = currier
        sess.commit()
        sess.close()
        return redirect('/')
    return render_template('currier_selection.html', form=form)


if __name__ == '__main__':
    main()
