from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed  # Убрали FileRequired
from wtforms import SubmitField, StringField, IntegerField, FileField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    category = StringField('Категория товара')
    cost_price = IntegerField('Себестоимость', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])

    # Теперь поле необязательное, но проверяет расширение, если файл загружен
    image = FileField('Карточка товара', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Допускаются только изображения!')
    ])
    submit = SubmitField('Добавить товар')