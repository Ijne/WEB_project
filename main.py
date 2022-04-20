import json

from flask import Flask, render_template, abort
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_login import login_user
from werkzeug.utils import redirect
import requests
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from data.products import Product
from data.orders import Orders
from forms.order import OrderForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Мебельный магазин 'Мебель'")


@app.route('/registration', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Данная почта уже зарегистрированна")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неверный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/ordering/<int:order>', methods=['GET', 'POST'])
def ordering(order):
    form = OrderForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user_basket = [int(x) for x in str(order)]
        all_products = db_sess.query(Product).filter(Product.id.in_(user_basket)).all()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if all_products and user:
            orders = Orders()
            product_name = ''
            total_price = 0
            for item in all_products:
                product_name += f'{item.name}, '
                total_price += item.price
            orders.name = product_name
            orders.total_price = total_price
            orders.email = form.email.data
            orders.phone_number = form.phone_number.data
            orders.name = f'{form.second_name.data} {form.name.data}'
            orders.phone_number = form.phone_number
            user.basket = ''
            db_sess.add(orders)
            db_sess.commit()
            return redirect('/profile')
    return render_template('ordering.html', form=form)


@app.route('/products')
def products():
    db_sess = db_session.create_session()
    all_products = db_sess.query(Product).all()
    return render_template('products.html', products=all_products, title='Товары')


@app.route('/products/<int:id>', methods=['GET', 'POST'])
def single_product(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if product:
        return render_template('product.html',
                               product_name=product.name,
                               image_name=product.image_name,
                               item_count=product.count,
                               item_price=product.price,
                               item_id=product.id,
                               added=False)
    else:
        abort(404)


@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if user:
        user_basket = [x for x in str(user.basket)]
        user_basket = [int(i) for i in user_basket]
        total_price = 0
        all_products = db_sess.query(Product).filter(Product.id.in_(user_basket)).all()
        for item in all_products:
            total_price += item.price
        return render_template('profile.html',
                               products=all_products,
                               total_price=total_price,
                               user=user)
    else:
        abort(404)


@app.route('/cart/<int:id>')
def cart(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    user_basket = db_sess.query(User).filter(User.id == current_user.id).first().basket
    user_basket = str(user_basket) + f'{str(id) } '
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.basket = user_basket
    db_sess.merge(user)
    db_sess.commit()
    return render_template('product.html',
                           product_name=product.name,
                           image_name=product.image_name,
                           item_count=product.count,
                           item_price=product.price,
                           item_id=product.id,
                           added=True)


def main():
    db_session.global_init('db/users_database.db')
    app.run()


if __name__ == '__main__':
    main()
