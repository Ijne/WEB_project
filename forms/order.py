from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    second_name = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Ваш email', validators=[DataRequired()])
    phone_number = StringField('Ваш номер телефона', validators=[DataRequired()])
    address = StringField('Ваш домашний адрес (город;улица;дом;квартира)',
                          validators=[DataRequired()])
    submit = SubmitField('Сделать заказ')

