from flask_restful import reqparse, Resource
from flask import jsonify
from . import db_session
from .products import Product

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('price', required=True)
parser.add_argument('image_name', required=True)
parser.add_argument('description', required=True)


class ProductResource(Resource):
    def get(self, product_id):
        db_sess = db_session.create_session()
        product = db_sess.query(Product).get(product_id)
        return jsonify({'product': product.to_dict(
            only=('id', 'name', 'price', 'image_name', 'description')
        )})

    def delete(self, product_id):
        db_sess = db_session.create_session()
        product = db_sess.query(Product).get(product_id)
        db_sess.delete(product)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ProductListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        products = db_sess.query(Product).all()
        return jsonify({'products': [item.to_dict(
            only=('id', 'name', 'price', 'image_name', 'description')
        ) for item in products]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        product = Product()
        product.name = args['name']
        product.price = args['price']
        product.image_name = args['image_name']
        product.description = args['description']
        db_sess.add(product)
        db_sess.commit()
        return jsonify({'success': 'OK'})
