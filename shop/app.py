from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from shop.data import db_session
from shop.user import RegisterForm, LoginForm, BuyForm, CheckForm, BlogsForm
from shop.data.users import User
from shop.data.Checklist import Checklist
from flask_ngrok import run_with_ngrok
from shop.data.news import News

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = SQLAlchemy(app)
run_with_ngrok(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    # text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', items=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()

    return redirect('/')


@app.route('/item_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def item_delete(id):
    item = Item.query.order_by(Item.price).filter(Item.id == id).first()
    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect('/')


@app.route('/buy/<int:id>', methods=['GET', 'POST'])
@login_required
def buyform(id):
    form = BuyForm()
    item = Item.query.get(id)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = Checklist(
            number0=form.number.data,
            time0=form.time.data,
            item_name=item.title
        )

        db_sess.add(user)
        db_sess.commit()
        return redirect("/")

    return render_template('buyform.html', item=item, form=form)


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    db_sess = db_session.create_session()
    if db_sess:
        news = db_sess.query(News)
    else:
        news = db_sess.query(News)
    return render_template('blog.html', news=news)


@app.route('/createblog', methods=['GET', 'POST'])
def createblog():
    form = BlogsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('createblog.html', title='Добавление новости',
                           form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.id != 1:
        return index()
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error'
    else:
        return render_template('create.html')


@app.route('/checklist', methods=['GET', 'POST'])
@login_required
def checklist():
    form = CheckForm()
    db_sess = db_session.create_session()
    numbers = db_sess.query(Checklist).all()
    if form.validate_on_submit():
        for lists in numbers:
            if lists.number0 == form.number.data:
                db_sess.delete(lists)
                db_sess.commit()
                break
        #user = Запросом из бд по номеру телефона (form.number.data) получить
        #db_sess.delete(user)

    return render_template('checklist.html', form=form, numbers=numbers)


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


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run()
    run_with_ngrok(app)
