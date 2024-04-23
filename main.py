from flask import Flask, render_template, redirect, abort, request
from wtforms import EmailField, PasswordField
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
import requests
from data import db_session
from data.users import User
from data.explorations import Exploration
from data.comments import Comments
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
nasa_request = "https://api.nasa.gov/planetary/apod?api_key="
nasa_api_key = "f4lJMtfmic5Ietnc3qee4EzSfVccklD8SfqDdCGX"


class ExplorationsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    explorations = db_sess.query(Exploration).all()
    return render_template("index.html", explorations=explorations)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/explorations',  methods=['GET', 'POST'])
@login_required
def add_explorations():
    form = ExplorationsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        explorations = Exploration()
        explorations.title = form.title.data
        explorations.content = form.content.data
        explorations.is_private = form.is_private.data
        current_user.explorations.append(explorations)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('explorations.html', title='Добавление исследования',
                           form=form)


@app.route('/apod',  methods=['GET', 'POST'])
@login_required
def view_apod():
    response = requests.get(nasa_request + nasa_api_key).json()
    APOD = {"img_url": response["url"],
            "autor": response["copyright"],
            "title": response["title"],
            "date": response["date"],
            "explanation": response["explanation"]
            }
    print(response)
    return render_template('apod.html', APOD=APOD, title='Картинка дня')


@app.route('/explorations/<int:id>', methods=['GET', 'POST'])
@login_required
def explorations(id):
    form = ExplorationsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        explorations = db_sess.query(Exploration).filter(Exploration.id == id,
                                          Exploration.user == current_user
                                          ).first()
        if explorations:
            form.title.data = explorations.title
            form.content.data = explorations.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        explorations = db_sess.query(Exploration).filter(Exploration.id == id,
                                          Exploration.user == current_user
                                          ).first()
        if explorations:
            explorations.title = form.title.data
            explorations.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('explorations.html',
                           title='Редактирование исследования',
                           form=form
                           )


@app.route('/explorations_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def explorations_delete(id):
    db_sess = db_session.create_session()
    explorations = db_sess.query(Exploration).filter(Exploration.id == id,
                                      Exploration.user == current_user
                                      ).first()
    if explorations:
        db_sess.delete(explorations)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/explorations_comments/<int:id>', methods=['GET', 'POST'])
@login_required
def explorations_comments(id):
    db_sess = db_session.create_session()
    explorations = db_sess.query(Exploration).filter(Exploration.id == id,
                                                     Exploration.user == current_user
                                                     ).first()
    comments = db_sess.query(Comments).filter(Comments.user_id == explorations.id)
    return render_template('comments.html',
                           title='Комментарии к исследованию', explorations=explorations,
                           comments=comments)


@app.route('/comments',  methods=['GET', 'POST'])
@login_required
def add_explorations():
    form = ExplorationsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comments()
        comment.content = form.content.data
        current_user.comm.append(explorations)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('explorations.html', title='Добавление исследования',
                           form=form)


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
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            lastname=form.lastname.data,
            occupation=form.occupation.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()