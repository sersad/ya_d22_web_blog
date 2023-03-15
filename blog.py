import datetime
import os

from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from data import db_session, news_api, news_resources
from data.category import Category
from data.news import News
from data.users import User
from forms.loginform import LoginForm
from forms.news import NewsForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource
from waitress import serve


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


# для списка объектов
api.add_resource(news_resources.NewsListResource, '/api/v2/news')

# для одного объекта
api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        print(current_user.name)
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()

    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in categories]

    if form.validate_on_submit():
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data

        news.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())

        # current_user.news.append(news)
        # db_sess.merge(current_user)

        news.user = current_user
        db_sess.merge(news)

        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    #######
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in categories]
    ######
    if request.method == "GET":
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            print(news.categories)
            form.category.data = [i.id for i in news.categories]
        else:
            abort(404)
    if form.validate_on_submit():
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data

            news.categories = []
            news.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())

            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

#
# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify({'error': 'Not found'}), 404)
#
#
# @app.errorhandler(400)
# def bad_request(_):
#     return make_response(jsonify({'error': 'Bad Request'}), 400)
#

def main():
    db_session.global_init('db/blogs.db')
    app.register_blueprint(news_api.blueprint)

    # app.run(port=8080, host='127.0.0.1')

    port = int(os.environ.get('PORT', 8080))
    serve(app, port=port, host="127.0.0.1")

    # db_sess = db_session.create_session()
    # user = User()
    # user.name = "Пользователь 3"
    # user.about = "биография пользователя 3"
    # user.email = "email3@email.ru"
    # db_sess.add(user)
    # db_sess.commit()

    # users = db_sess.query(User).filter((User.id > 1) | (User.email.notilike("%1%")))
    # for user in users:
    #     print(user)


    # user = db_sess.query(User).filter(User.id == 1).first()
    # print(user)
    # user.name = "Измененное имя пользователя"
    # user.created_date = datetime.datetime.now()
    # db_sess.commit()
    # print(db_sess.query(User).filter(User.id == 1).first())


    # news = News(title="Первая новость", content="Привет блог!",
    #             user_id=1, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()

    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Вторая новость", content="Уже вторая запись!",
    #             user=user, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()

    # user = db_sess.query(User).filter(User.id == 4).first()
    # news = News(title="Личная запись SSSSS", content="Эта запись личная",
    #             is_private=True)
    # user.news.append(news)
    # db_sess.commit()


    # cat = Category(name='Политика')
    # cat2 = Category(name='Происшествия')
    # db_sess.add(cat)
    # db_sess.add(cat2)
    # db_sess.commit()


if __name__ == '__main__':
    main()
