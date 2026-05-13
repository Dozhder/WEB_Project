import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.mutable import MutableDict


class Order(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    client = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    products = sqlalchemy.Column(MutableDict.as_mutable(sqlalchemy.JSON)) # format: {id_product: quantity product, ...}
    price = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    type = sqlalchemy.Column(sqlalchemy.String)
    payment_type = sqlalchemy.Column(sqlalchemy.String)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    delivery_man = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    is_complete = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    cl = orm.relationship('User', foreign_keys=[client], back_populates='orders', uselist=False)
    del_men = orm.relationship('User', foreign_keys=[delivery_man], back_populates='orders_deliver', uselist=False)


