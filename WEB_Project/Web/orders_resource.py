from flask_restful import Resource, abort, reqparse
from flask import jsonify, request
from functools import wraps

from data import db_session
from data.orders import Order

import os
from dotenv import load_dotenv


load_dotenv('data.env')
API_KEY = os.getenv('SECRET_API_KEY')


def abort_if_order_not_found(order_id):
    session = db_session.create_session()
    order = session.query(Order).get(order_id)
    session.close()
    if not order:
        abort(404, message=f"Order {order_id} not found")


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
parsers.add_argument('client', type=int, required=False)
parsers.add_argument('products', required=False)
parsers.add_argument('price', type=int, required=False)
parsers.add_argument('type', required=False)
parsers.add_argument('payment_type', required=False)
parsers.add_argument('address', required=False)
parsers.add_argument('delivery_man', type=int, required=False)
parsers.add_argument('is_complete', type=bool, required=False)


class OrderResource(Resource):

    @check_api_key
    def get(self, order_id):
        abort_if_order_not_found(order_id)
        session = db_session.create_session()
        order = session.get(Order, order_id)
        ans = jsonify({'order': order.to_dict(
            only=('id', 'client', 'products', 'price', 'type', 'address', 'payment_type',
                  'delivery_man', 'is_complete'))})
        session.close()
        return ans

    @check_api_key
    def delete(self, order_id):
        abort_if_order_not_found(order_id)
        session = db_session.create_session()
        order = session.get(Order, order_id)
        session.delete(order)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    @check_api_key
    def put(self, order_id):
        abort_if_order_not_found(order_id)
        args = parsers.parse_args()
        session = db_session.create_session()
        order = session.get(Order, order_id)
        for key, item in args.items():
            if item is not None:
                setattr(order, key, item)
        session.commit()
        ans = jsonify({'order': order.to_dict(
            only=('id', 'client', 'products', 'price', 'type', 'address', 'payment_type',
                  'delivery_man', 'is_complete'))})
        session.close()
        return ans




parser = reqparse.RequestParser()
parser.add_argument('client', type=int, required=True)
parser.add_argument('products', required=True)
parser.add_argument('price', type=int, required=True)
parser.add_argument('type', required=True)
parser.add_argument('payment_type', required=True)
parser.add_argument('address', required=False)
parser.add_argument('delivery_man', type=int, required=False, default=None)
parser.add_argument('is_complete', type=bool, required=False, default=False)


class OrderListResource(Resource):

    @check_api_key
    def get(self):
        session = db_session.create_session()
        orders = session.query(Order).all()
        ans = jsonify({'orders': [item.to_dict(
            only=('id', 'client', 'products', 'price', 'type', 'address', 'payment_type',
                                                               'delivery_man', 'is_complete')) for item in orders]})
        session.close()
        return ans

    @check_api_key
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        order = Order(
            client=args['client'],
            products=args['products'],
            price=args['price'],
            type=args['type'],
            payment_type=args['payment_type'],
            address=args['address'],
            delivery_man=args['delivery_man'],
            is_complete=args['is_complete']
        )
        session.add(order)
        session.commit()
        ans = jsonify({'id': order.id})
        session.close()
        return ans

