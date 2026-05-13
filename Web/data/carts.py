import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from .products import Product
from sqlalchemy.ext.mutable import MutableDict


# def price_calculation(context):
#     session = context.bind
#
#     price = 0
#
#     products = context.get_current_parameters()['products']
#     for id, amount in products.items():
#         price += session.query(Product).filter(Product.id == id).first() * amount


class Cart(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'carts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    user_id =  sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    products = sqlalchemy.Column(MutableDict.as_mutable(sqlalchemy.JSON), default={}) # format: {id_product: quantity product, ...}
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)

    user = orm.relationship('User', foreign_keys=[user_id], back_populates='cart')