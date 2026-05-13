from flask_restful import Resource, abort, reqparse
from flask import jsonify, request
from functools import wraps

from data import db_session
from data.users import User

import os
from dotenv import load_dotenv


load_dotenv('data.env')
API_KEY = os.getenv('SECRET_API_KEY')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    if not user:
        abort(404, message=f"User {user_id} not found")


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
parsers.add_argument('surname', required=False)
parsers.add_argument('name', required=False)
parsers.add_argument('age', required=False)
parsers.add_argument('position', required=False)
parsers.add_argument('speciality', required=False)
parsers.add_argument('address', required=False)
parsers.add_argument('email', required=False)
parsers.add_argument('password', required=False)


class UserResource(Resource):

    @check_api_key
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        ans = jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'))})
        session.close()
        return ans

    @check_api_key
    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    @check_api_key
    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = parsers.parse_args()
        session = db_session.create_session()
        user = session.get(User, user_id)
        for key, item in args.items():
            if item is not None:
                setattr(user, key, item)
        if 'password' in args:
            user.set_password(args['password'])
        session.commit()
        ans = jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'))})
        session.close()
        return ans




parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True)
parser.add_argument('position', required=True)
parser.add_argument('speciality', required=True)
parser.add_argument('address', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)


class UserListResource(Resource):

    @check_api_key
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        ans = jsonify({'users': [item.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email')) for item in users]})
        session.close()
        return ans

    @check_api_key
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if session.query(User).filter(User.email == args.email).first() is not None:
            abort(409, messages="A user with this email address already exists")
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        ans = jsonify({'id': user.id})
        session.close()
        return ans

