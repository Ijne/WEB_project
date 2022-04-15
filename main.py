from flask import Flask, render_template, abort
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_login import login_user
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from data.products import Product

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    user_basket = db_sess.query(User).filter(User.id == current_user.id).first().basket
    user_basket = str(user_basket)
    products = []
    if user_basket:
        user_basket = list(user_basket)
        for product in user_basket:
            products.append(int(product))
    all_products = db_sess.query(Product).filter(Product.id.in_(products)).all()
    return render_template('profile.html', products=all_products)


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
                               item_id=product.id)
    else:
        abort(404)


@app.route('/cart/<int:id>')
def cart(id):
    db_sess = db_session.create_session()
    user_basket = db_sess.query(User).filter(User.id == current_user.id).first().basket
    user_basket = str(user_basket) + f'{str(id) } '
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.basket = user_basket
    db_sess.merge(user)
    db_sess.commit()
    return redirect('/profile')


def main():
    db_session.global_init('db/users_database.db')
    app.run()


if __name__ == '__main__':
    main()
