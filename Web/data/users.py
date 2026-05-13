import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.mutable import Mutable


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, dict):
                return cls(value)
            return Mutable.coerce(key, value)
        return value

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, MutableDict):
            value = MutableDict(value)
        dict.__setitem__(self, key, value)
        self.changed()

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        if isinstance(value, dict) and not isinstance(value, MutableDict):
            value = MutableDict(value)
            dict.__setitem__(self, key, value)
            # Важно: сообщаем SQLAlchemy, что структура изменилась
            self.changed()
        return value

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()

    def update(self, *args, **kwargs):
        # Преобразуем входящие словари в MutableDict при update
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
        self.changed()

    def pop(self, *args):
        res = dict.pop(self, *args)
        self.changed()
        return res

    def clear(self):
        dict.clear(self)
        self.changed()


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    addresses = sqlalchemy.Column(MutableDict.as_mutable(sqlalchemy.JSON), nullable=True, default={'addresses': []}) # format: {'addresses': []}
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    access = sqlalchemy.Column(sqlalchemy.Integer, nullable=False) # 0: User; 1: Delivery men; 2: Eatery/Manager
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    orders = orm.relationship('Order', foreign_keys='Order.client', back_populates='cl')
    orders_deliver = orm.relationship('Order', foreign_keys='Order.delivery_man', back_populates='del_men')

    cart = orm.relationship('Cart', foreign_keys='Cart.user_id', back_populates='user', uselist=False)

    eatery = orm.relationship('Eatery', foreign_keys='Eatery.chief_id', back_populates='chief', uselist=False)


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
