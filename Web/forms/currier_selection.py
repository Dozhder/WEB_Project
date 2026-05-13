from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired


class CurrierSelectionForm(FlaskForm):
    currier = SelectField('Выберете курьера', choices=[])
    submit = SubmitField('Submit')
