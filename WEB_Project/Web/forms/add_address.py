from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField, DateField, SelectField
from wtforms.validators import DataRequired


class AddAddressForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Submit')