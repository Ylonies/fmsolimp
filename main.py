from flask import Flask, render_template, request

from flask_login import login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.utils import redirect

from data import db_session
from data.topics import Topics, Subtopics, Exercises, Subjects, Theory, Forum

from data.users import Users, User_exercises
from forms.answer import AnswerForm
from forms.users import RegisterForm, LoginForm

app = Flask(__name__)
db_session.global_init("db/info.db")
db_sess = db_session.create_session()

app.config['SECRET_KEY'] = 'project_web'


@app.context_processor
def context_processor():
    return dict(subjects=[sb.name for sb in db_sess.query(Subjects)], admins=[sb.author for sb in db_sess.query(Subjects)])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/personal")
def personal_account():
    return render_template("personal_account.html", user=current_user, title="Личный кабинет")



@app.route("/Предмет_<sbj_name>", methods=['GET', 'POST'])
def topics_page(sbj_name):
    sbj = db_sess.query(Subjects).filter(Subjects.name == sbj_name).first()
    author = db_sess.query(Users).filter(Users.id == sbj.author).first()
    topics = sbj.topics
    if request.method == "POST":
        new = Topics(name=request.form.get("new_option"), subjects_id = sbj.id)
        db_sess.add(new)
        db_sess.commit()
        return redirect(f"/{sbj_name}")
    return render_template("topics.html", subject=sbj, topics=topics, author = author, option = 'темы')


@app.route("/<topic_n>/subtopics", methods=['GET', 'POST'])
def subtopic_page(topic_n):
    topic = db_sess.query(Topics).filter(Topics.name == topic_n).first()
    sbj = topic.subjects
    subtopics = topic.subtopics
    done_exercises = [x.exercise_id for x in current_user.exercises]

    if request.method == "POST":
        new = Subtopics(name=request.form.get("new_option"), topic_id = topic.id)
        db_sess.add(new)
        db_sess.commit()
        return redirect(f"/{topic_n}/subtopics")
    return render_template("subtopics.html", topic=topic, done_exercises=done_exercises, subtopics=subtopics, sbj = sbj,
                           option = 'раздела', title=topic.name)

@app.route("/<sb_id>/theory")
def theory(sb_id):
    sb = db_sess.query(Subtopics).filter(Subtopics.id == sb_id).first()
    sbj = sb.topics.subjects
    theory = db_sess.query(Theory).order_by(Theory.id.desc()).filter(Theory.sb_id == sb.id).first()
    num = db_sess.query(Exercises).filter((Exercises.subtopics_id == sb.id)).count()
    return render_template("theory.html", title=sb.name, topic=sb.topics.name, sbj=sbj, theory=theory, num=num,
                           sb_id= sb_id)




@app.route("/<sb_id>/edit_theory", methods=['GET', 'POST'])
def edit_theory(sb_id):
    sb = db_sess.query(Subtopics).filter(Subtopics.id == sb_id).first()
    theory = db_sess.query(Theory).order_by(Theory.id.desc()).filter(Theory.sb_id == sb_id).first()
    sbj = sb.topics.subjects
    if request.method == "POST":
        new_th = Theory(sb_id = sb_id, data=request.form.get("new_theory"))
        db_sess.add(new_th)
        db_sess.commit()
        return redirect(f"/{sb_id}/theory")
    num = db_sess.query(Exercises).filter((Exercises.subtopics_id == sb.id)).count()

    return render_template("edit_theory.html", title=sb.name, topic=sb.topics.name, sbj=sbj, theory=theory, num=num,
                           sb_id = sb_id)




@app.route("/<sb_id>/exercise/<number>", methods=['GET', 'POST'])
def exercise_page(sb_id, number):

    sb = db_sess.query(Subtopics).filter(Subtopics.id == sb_id).first()
    topic = sb.topics.name
    sbj = sb.topics.subjects
    num = db_sess.query(Exercises).filter((Exercises.subtopics_id == sb.id)).count()
    form = AnswerForm()
    if number <= num:
        exercise = db_sess.query(Exercises).join(Subtopics).filter((Subtopics.id == sb_id),
                                                                   (Exercises.number == number)).first()
        message = exercise.message
        if exercise.answer:
            if db_sess.query(User_exercises).filter((User_exercises.exercise_id == exercise.id),
                                                    (User_exercises.user_id == current_user.id)).first():
                form.answer.data = exercise.answer
                message = "Решено"
            else:
                if form.validate_on_submit():
                    if form.answer.data == exercise.answer:
                        us_ex = User_exercises(exercise_id=exercise.id, user_id=current_user.id)
                        db_sess.add(us_ex)
                        db_sess.commit()
                        message = "Правильный ответ"

                    else:
                        message = "Неправильный ответ"
        return render_template("exercise.html", exercise=exercise, title=f"Задача № {exercise.number}", num=num, topic=topic,
                                   author=sbj.author, message=message, form=form, sb_id=sb_id)
    else:
        return redirect(f"/{sb_id}/edit_exercise/{number}")



@app.route("/<sb_id>/edit_exercise/<number>", methods=['GET', 'POST'])
def edit_ex_page(sb_id, number):
    number = int(number)
    sb = db_sess.query(Subtopics).filter(Subtopics.id == sb_id).first()
    num = db_sess.query(Exercises).filter((Exercises.subtopics_id == sb.id)).count()
    exercise = db_sess.query(Exercises).join(Subtopics).filter((Subtopics.name == sb.name),
                                                               (Exercises.number == number)).first()

    if request.method == "POST":
        if exercise is not None:
            db_sess.delete(exercise)
        new_ex = Exercises(subtopics_id=sb.id, text=request.form.get("text"), answer=request.form.get("answer"),
                           solution = request.form.get("solution"), number=number, message=request.form.get("message"))
        db_sess.add(new_ex)
        db_sess.commit()
        return redirect(f"/{sb_id}/exercise/{number}")
    return render_template("edit_exercise.html", title=f"Задача № {number}", number=number, num=num, exercise=exercise, sb_id=sb_id)


@app.route("/comments<num>")
def forum_page(num):
    num = int(num)
    x = 5
    if current_user.subject:
        all_comm = db_sess.query(Forum).join(Subtopics).join(Topics).filter(Topics.subjects == current_user.subject[0])[::-1]
    else:
        all_comm = current_user.forum[::-1]
    com_list = all_comm[(num-1)*x:num*x]
    return render_template("comments.html",  user=current_user, title="Комментарии", list=com_list, current_page= num,
                           all_pages=len(all_comm)//x+1)

@app.route("/forum/<ex_id>", methods=['GET', 'POST'])
def forum_ex_page(ex_id):
    exercise = db_sess.query(Exercises).filter(Exercises.id == ex_id).first()
    messages = db_sess.query(Forum).filter(Forum.exercise_id == ex_id)
    admin = exercise.subtopics.topics.subjects.author

    if request.method == "POST":
        parent_id = request.form.get("parent_id")
        new_ms = Forum(user_id=current_user.id, parent_id=parent_id, exercise_id=ex_id, text=request.form.get("message"), subtopic_id = exercise.subtopics.id)
        db_sess.add(new_ms)
        db_sess.commit()

    return render_template("forum_exercise.html", title=f"Задача № {exercise.number}", exercise=exercise, messages=messages, admin = admin)




@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    message= ""
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            message ="Пароли не совпадают"
        elif db_sess.query(Users).filter(Users.email == form.email.data).first():
            message ="Такой пользователь уже есть"
        else:
            user = Users(
                name=form.name.data,
                email=form.email.data,
                surname=form.surname.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, message= message)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
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

if __name__ == '__main__':
    app.run(host='127.0.0.2')


