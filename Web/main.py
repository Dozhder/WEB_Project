# flask
from flask import Flask, request, make_response, render_template, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource

# import from data
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.department import Department

# datetime
import datetime as dt

# import from forms
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.add_work import AddWorkForm
from forms.add_department import AddDepartmentForm

# import API resource
import users_resource
import jobs_resource


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# api
api = Api(app)
# add user resources
api.add_resource(users_resource.UserResource, '/api/users/<int:user_id>')
api.add_resource(users_resource.UserListResource, '/api/users')
# add job resources
api.add_resource(jobs_resource.JobResource, '/api/jobs/<int:job_id>')
api.add_resource(jobs_resource.JobListResource, '/api/jobs')

db_session.global_init('db/data_test.sqlite3')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    us = db_sess.get(User, user_id)
    db_sess.close()
    return us


def main():
    pass
    app.run(host='127.0.0.1', port='8080')


@app.route('/test')
def test():
    return 'Good'


@app.route('/')
def home():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        render = []
        for job in db_sess.query(Jobs).all():
            render.append(job)
        db_sess.close()
        return render_template('work_log.html', works=render)
    return '<br>'.join([render_template('base.html'),
                        '''<h3 align="center">Пожалуйста войдите в аккаунт
                         для просмотра информации о состоянии работ</h3>'''])


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            db_sess.close()
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_work', methods=['GET', 'POST'])
def add_work():
    form = AddWorkForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # user = db_sess.query(User).filter(User.surname == form.surname.data,
        #                                           User.name == form.name.data,
        #                                           User.position == form.position.data).first()
        #         if user and user.check_password(form.password.data):
        #             job = Jobs(team_leader=user.id,
        #                        job=form.job.data,
        #                        work_size=form.work_size.data,
        #                        collaborators=form.collaborators_list.data,
        #                        start_date=form.start_date.data,
        #                        is_finished=False)
        job = Jobs(team_leader=current_user.id,
                   job=form.job.data,
                   work_size=form.work_size.data,
                   collaborators=form.collaborators_list.data,
                   hazard=form.hazard.data,
                   start_date=form.start_date.data,
                   is_finished=form.is_finished.data,
                   end_date=form.end_date.data)
        db_sess.add(job)
        db_sess.commit()
        db_sess.close()
        return redirect("/")
    return render_template('add_work.html', title='Добавление работы', form=form)


@app.route('/edit_work/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_work(id):
    form = AddWorkForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if job and job.team_leader == (current_user.id or 1):
            form.job.data = job.job
            form.work_size.data = job.work_size
            form.collaborators_list.data = job.collaborators
            form.hazard.data = job.hazard
            form.start_date.data = job.start_date
            form.is_finished.data = job.is_finished
            form.end_date.data = job.end_date
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if job and current_user.id == (job.team_leader or 1):
            job.job = form.job.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators_list.data
            job.hazard = form.hazard.data
            job.start_date = form.start_date.data
            job.is_finished = form.is_finished.data
            job.end_date = form.end_date.data
            db_sess.commit()
            db_sess.close()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_work.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/delete_work/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_work(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if job and job.team_leader == (current_user.id or 1):
        db_sess.delete(job)
        db_sess.commit()
        db_sess.close()
    else:
        abort(404)
    return redirect('/')


@app.route('/department')
def departament_list():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        render = []
        for department in db_sess.query(Department).all():
            render.append(department)
        db_sess.close()
        return render_template('departament.html', departments=render)
    return '<br>'.join([render_template('base.html'),
                        '''<h3 align="center">Пожалуйста войдите в аккаунт
                         для просмотра информации о Департаментах</h3>'''])


@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    form = AddDepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # user = db_sess.query(User).filter(User.surname == form.surname.data,
        #                                           User.name == form.name.data,
        #                                           User.position == form.position.data).first()
        #         if user and user.check_password(form.password.data):
        #             job = Jobs(team_leader=user.id,
        #                        job=form.job.data,
        #                        work_size=form.work_size.data,
        #                        collaborators=form.collaborators_list.data,
        #                        start_date=form.start_date.data,
        #                        is_finished=False)
        department = Department(chief=current_user.id,
                   title=form.title.data,
                   members=form.members.data,
                   email=form.department_email.data)
        db_sess.add(department)
        db_sess.commit()
        return redirect("/department")
    return render_template('add_department.html', title='Добавление департамента', form=form)


@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = AddDepartmentForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == id).first()
        db_sess.close()
        if department and department.chief == (current_user.id or 1):
            form.title.data = department.title
            form.members.data = department.members
            form.department_email.data = department.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == id).first()
        if department and department.chief == (current_user.id or 1):
            department.title = form.title.data
            department.members = form.members.data
            department.email = form.department_email.data
            db_sess.commit()
            db_sess.close()
            return redirect('/department')
        else:
            abort(404)
    return render_template('add_department.html',
                           title='Редактирование департамента',
                           form=form
                           )


@app.route('/delete_department/<int:id>', methods=['GET', 'POST'])
@login_required
def department_delete(id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == id).first()
    if department and department.chief == (current_user.id or 1):
        db_sess.delete(department)
        db_sess.commit()
        db_sess.close()
    else:
        abort(404)
    return redirect('/department')


if __name__ == '__main__':
    main()
