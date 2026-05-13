import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin


class Eatery(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'eateries'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String)
    chief_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    staff = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    chief = orm.relationship('User', foreign_keys=[chief_id], back_populates='eatery', uselist=False)