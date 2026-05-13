from flask_restful import Resource, abort, reqparse
from flask import jsonify, request
from functools import wraps

from data import db_session
from data.products import Product

import os
from dotenv import load_dotenv


load_dotenv('data.env')
API_KEY = os.getenv('SECRET_API_KEY')


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    session.close()
    if not product:
        abort(404, message=f"Product {product_id} not found")


def check_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key == API_KEY:
            return func(*args, **kwargs)
        else:
            abort(403, messages='Invalid API key')
    return wrapper


parsers = reqparse.RequestParser()
parsers.add_argument('name', required=False)
parsers.add_argument('category', required=False)
parsers.add_argument('cost_price', type=int, required=False)
parsers.add_argument('price', type=int, required=False)
parsers.add_argument('markup', type=float, required=False)
parsers.add_argument('image', required=False)


class ProductResource(Resource):

    @check_api_key
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.get(Product, product_id)
        ans = jsonify({'product': product.to_dict(
            only=('id', 'name', 'category', 'cost_price', 'price', 'markup', 'image'))})
        session.close()
        return ans

    @check_api_key
    def delete(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.get(Product, product_id)
        session.delete(product)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    @check_api_key
    def put(self, product_id):
        abort_if_product_not_found(product_id)
        args = parsers.parse_args()
        session = db_session.create_session()
        product = session.get(Product, product_id)
        for key, item in args.items():
            if item is not None:
                setattr(product, key, item)
        session.commit()
        ans = jsonify({'product': product.to_dict(
            only=('id', 'name', 'category', 'cost_price', 'price', 'markup', 'image'))})
        session.close()
        return ans




parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('category', required=True)
parser.add_argument('cost_price', type=int, required=True)
parser.add_argument('price', type=int, required=True)
parser.add_argument('markup', type=float, required=True)
parser.add_argument('image', required=False)


class ProductListResource(Resource):

    @check_api_key
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        ans = jsonify({'products': [item.to_dict(
            only=('id', 'name', 'category', 'cost_price', 'price', 'markup', 'image')) for item in products]})
        session.close()
        return ans

    @check_api_key
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product(
            name=args['name'],
            category=args['category'],
            cost_price=args['cost_price'],
            price=args['price'],
            markup=args['markup'],
            image=args['image']
        )
        session.add(product)
        session.commit()
        ans = jsonify({'id': product.id})
        session.close()
        return ans

