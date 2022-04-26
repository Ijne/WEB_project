from flask_restful import reqparse, Resource
from flask import jsonify
from . import db_session
from .orders import Orders

parser = reqparse.RequestParser()
parser.add_argument('order', required=True)
parser.add_argument('phone_number', required=True)
parser.add_argument('email', required=True)
parser.add_argument('name', required=True)
parser.add_argument('address', required=True)
parser.add_argument('total_price', required=True)


class OrderResource(Resource):
    def get(self, order_id):
        db_sess = db_session.create_session()
        order = db_sess.query(Orders).get(order_id)
        return jsonify({'order': order.to_dict(
            only=('id', 'order', 'phone_number', 'email', 'name', 'address', 'total_price')
        )})

    def delete(self, order_id):
        db_sess = db_session.create_session()
        order = db_sess.query(Orders).get(order_id)
        db_sess.delete(order)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class OrderListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        orders = db_sess.query(Orders).all()
        return jsonify({'orders': [item.to_dict(
            only=('id', 'order', 'phone_number', 'email', 'name', 'address', 'total_price')
        ) for item in orders]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        order = Orders()
        order.order = args['order']
        order.phone_number = args['phone_number']
        order.email = args['email']
        order.name = args['name']
        order.address = args['address']
        order.total_price = args['total_price']
        db_sess.add(order)
        db_sess.commit()
        return jsonify({'success': 'OK'})
