import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin


class Product(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost_price = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    price = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    markup = sqlalchemy.Column(sqlalchemy.Numeric(precision=5, scale=2))
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)


