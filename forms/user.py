from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, RadioField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    lastname = StringField('Фамилия пользователя', validators=[DataRequired()])
    occupation = RadioField('Вы астроном?', choices=[("Астроном", "Да, я астроном."),
                                                     ("Гость", "Нет, я гость")], validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')