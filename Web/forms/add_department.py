from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField, DateField
from wtforms.validators import DataRequired
import datetime as dt


class AddDepartmentForm(FlaskForm):
    # surname = StringField('Surname', validators=[DataRequired()])
    # name = StringField('Name', validators=[DataRequired()])
    # team_leader = StringField('Team Leader per id', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # position = StringField('Position', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    department_email = EmailField('Department Email', validators=[DataRequired()])
    submit = SubmitField('Submit')
