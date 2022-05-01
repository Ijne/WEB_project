import os
from flask import Flask, render_template, abort
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from werkzeug.utils import redirect
from datetime import datetime as dt
import csv
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from data.products import Product
from data.orders import Orders
from forms.order import OrderForm
from data import users_api, orders_api, products_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mebel260422'
app.config['JSON_AS_ASCII'] = False
api = Api(app)

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


@app.route('/ordering/<string:order>', methods=['GET', 'POST'])
def ordering(order):
    form = OrderForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user_basket = user.basket.split(', ')
        total_price = 0
        all_products = []
        for i in user_basket:
            if db_sess.query(Product).filter(Product.id == i).first():
                all_products.append(db_sess.query(Product).filter(Product.id == i).first())
        product_name = ''
        for item in all_products:
            if all_products.index(item) == len(all_products) - 1:
                product_name += f'{item.name}'
            else:
                product_name += f'{item.name}, '
            total_price += item.price
        orders = Orders()
        orders.order = product_name
        orders.total_price = total_price
        orders.email = form.email.data
        orders.phone_number = form.phone_number.data
        orders.name = f'{form.second_name.data} {form.name.data}'
        orders.phone_number = form.phone_number.data
        orders.address = form.address.data
        user.basket = ''
        db_sess.add(orders)
        db_sess.commit()
        filename = f'receipts/{user.id}_{user.basket}_{dt.now().date()}_' \
                   f'{dt.now().hour}_{dt.now().minute}_{dt.now().second}.csv'
        dict_of_order = [{
            "order": product_name,
            "name": f'{form.second_name.data} {form.name.data}',
            "phone_number": form.phone_number.data,
            "address": form.address.data,
            "price": total_price,
            "time": dt.now().time()
        }]
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(dict_of_order[0].keys()),
                                    delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for d in dict_of_order:
                writer.writerow(d)
        return redirect('/profile')
    return render_template('ordering.html', form=form)


@app.route('/on_map')
def on_map():
    return render_template('on_map.html')


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
                               item_price=product.price,
                               item_id=product.id,
                               description=product.description,
                               added=False)
    else:
        abort(404)


@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if user:
        if user.basket == '':
            return render_template('profile.html',
                                   basket=False)
        else:
            user_basket = user.basket.split(', ')
            user_basket_string = ''
            for x in user_basket:
                user_basket_string += x
            total_price = 0
            all_products = []
            for i in user_basket:
                if db_sess.query(Product).filter(Product.id == i).first():
                    all_products.append(db_sess.query(Product).filter(Product.id == i).first())
            for item in all_products:
                total_price += item.price
            return render_template('profile.html',
                                   products=all_products,
                                   total_price=total_price,
                                   user=user,
                                   user_basket=user_basket_string)
    else:
        abort(404)


@app.route('/clear_cart')
def clear():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.basket = ''
    db_sess.commit()
    return redirect('/profile')


@app.route('/cart/<int:id>')
def cart(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    user_basket = db_sess.query(User).filter(User.id == current_user.id).first().basket
    if user_basket == '':
        user_basket = str(user_basket) + f'{str(id)}'
    else:
        user_basket = str(user_basket) + f', {str(id)}'
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.basket = user_basket
    db_sess.merge(user)
    db_sess.commit()
    return render_template('product.html',
                           product_name=product.name,
                           image_name=product.image_name,
                           item_price=product.price,
                           item_id=product.id,
                           description=product.description,
                           added=True)


def main():
    db_session.global_init('db/users_database.db')
    api.add_resource(users_api.UserResource, '/api/user/<int:user_id>')
    api.add_resource(users_api.UserListResource, '/api/user')
    api.add_resource(orders_api.OrderResource, '/api/order/<int:order_id>')
    api.add_resource(orders_api.OrderListResource, '/api/order')
    api.add_resource(products_api.ProductResource, '/api/product/<int:product_id>')
    api.add_resource(products_api.ProductListResource, '/api/product')
    app.run()


if __name__ == '__main__':
    try:
        os.mkdir("receipts")
    except OSError:
        pass
    main()
