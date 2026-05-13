from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField, DateField
from wtforms.validators import DataRequired
import datetime as dt


class AddWorkForm(FlaskForm):
    # surname = StringField('Surname', validators=[DataRequired()])
    # name = StringField('Name', validators=[DataRequired()])
    # team_leader = StringField('Team Leader per id', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # position = StringField('Position', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    work_size = StringField('Work Size', validators=[DataRequired()])
    collaborators_list = StringField('Collaborators List per id', validators=[DataRequired()])
    hazard = StringField('Hazard Category', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], default=dt.datetime.now)
    is_finished = BooleanField('Is Finished')
    end_date = DateField('End Date', validators=[DataRequired()], default=dt.datetime.now)
    submit = SubmitField('Submit')
