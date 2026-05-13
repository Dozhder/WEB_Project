from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired


class CreateOrderForm(FlaskForm):
    type = SelectField('Способ получения заказа', choices=[('delivery', 'Доставка'), ('pickup', "Самовывоз")], validators=[DataRequired()])
    payment_type = SelectField('Способ оплаты', choices=[('non-cash', 'Безналичный'), ('cash', 'Наличные')])
    cash = IntegerField('Сдача с', default=0)
    address_to_order = SelectField('Адрес доставки', choices=[('', '')], default='')
    address_eatery = SelectField('Адрес для самовывоза', choices=[('', '')], default='')
    submit = SubmitField('Submit')
