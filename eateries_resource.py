from flask_restful import Resource, abort, reqparse
from flask import jsonify, request
from functools import wraps

from data import db_session
from data.eateries import Eatery
from data.users import User

import os
from dotenv import load_dotenv


load_dotenv('data.env')
API_KEY = os.getenv('SECRET_API_KEY')


def abort_if_eatery_not_found(eatery_id):
    session = db_session.create_session()
    eatery = session.query(Eatery).get(eatery_id)
    session.close()
    if not eatery:
        abort(404, message=f"Eatery {eatery_id} not found")


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
parsers.add_argument('address', required=False)
parsers.add_argument('chief_id', type=int, required=False)
parsers.add_argument('staff', required=False)


class EateryResource(Resource):

    @check_api_key
    def get(self, eatery_id):
        abort_if_eatery_not_found(eatery_id)
        session = db_session.create_session()
        eatery = session.get(Eatery, eatery_id)
        ans = jsonify({'product': eatery.to_dict(
            only=('id', 'name', 'address', 'chief_id', 'staff'))})
        session.close()
        return ans

    @check_api_key
    def delete(self, eatery_id):
        abort_if_eatery_not_found(eatery_id)
        session = db_session.create_session()
        eatery = session.get(Eatery, eatery_id)
        session.delete(eatery)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    @check_api_key
    def put(self, eatery_id):
        abort_if_eatery_not_found(eatery_id)
        args = parsers.parse_args()
        session = db_session.create_session()
        eatery = session.get(Eatery, eatery_id)
        for key, item in args.items():
            if item is not None:
                setattr(eatery, key, item)
        session.commit()
        ans = jsonify({'product': eatery.to_dict(
            only=('id', 'name', 'address', 'chief_id', 'staff'))})
        session.close()
        return ans




parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('address', required=True)
parser.add_argument('chief_id', type=int, required=True)
parser.add_argument('staff', required=False, default='')


class EateryListResource(Resource):

    @check_api_key
    def get(self):
        session = db_session.create_session()
        eateries = session.query(Eatery).all()
        ans = jsonify({'eateries': [item.to_dict(
            only=('id', 'name', 'address', 'chief_id', 'staff')) for item in eateries]})
        session.close()
        return ans

    @check_api_key
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        eatery = Eatery(
            name=args['name'],
            address=args['address'],
            chief_id=args['chief_id'],
            staff=args['staff']
        )
        chief = session.get(User, args['chief_id'])
        chief.eatery = eatery
        eatery.chief = chief
        session.add(eatery)
        session.commit()
        ans = jsonify({'id': eatery.id})
        session.close()
        return ans

