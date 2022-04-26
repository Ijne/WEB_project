import datetime
from flask_restful import reqparse, Resource
from flask import jsonify
from . import db_session
from .users import User
from werkzeug.security import generate_password_hash

parser = reqparse.RequestParser()
parser.add_argument('hashed_password', required=True)
parser.add_argument('email', required=True)
parser.add_argument('name', required=True)


class UserResource(Resource):
    def get(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'name', 'email', 'created_date', 'basket')
        )})

    def delete(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'name', 'email', 'created_date', 'basket')) for item in users]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        user = User()
        user.name = args['name']
        user.email = args['email']
        user.hashed_password = generate_password_hash(args['hashed_password'])
        user.created_date = datetime.datetime.now()
        user.basket = args['basket']
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


