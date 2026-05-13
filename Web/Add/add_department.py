from flask import Flask, request, make_response
from data import db_session
from data.department import Department
from data.users import User


db_session.global_init('db/data_test.sqlite3')

db_sess = db_session.create_session()

department = Department()
department.chief =  1
department.title = 'Department of Geological Exploration'
department.members = '2, 3'
for user in db_sess.query(User).filter(User.id == 1):
    department.email = user.email
db_sess.add(department)
db_sess.commit()
