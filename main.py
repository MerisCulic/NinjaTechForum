from flask import Flask, render_template, request, redirect, url_for, make_response
from models.settings import db
from models.user import User
from models.topic import Topic
import hashlib
import uuid


app = Flask(__name__)
db.create_all()


def user_from_session_token():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    return user


@app.route('/', methods=["GET", "POST"])
def index():
    user = user_from_session_token()
    topics = db.query(Topic).all()

    return render_template("index.html", user=user, topics=topics)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Passwords don't match! Go back and try again."

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User.create(
                    username=username,
                    password_hash=password_hash,
                    )

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')

        return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(username=username).first()

        if not user:
            return "This user does not exist"
        else:
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())
                db.add(user)
                db.commit()

                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')

                return response
            else:
                return "Your password is incorrect!"


@app.route("/logout")
def logout():
    user = user_from_session_token()

    user.session_token = ""
    db.add(user)
    db.commit()

    return redirect(url_for('index'))

@app.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    if request.method == "GET":
        return render_template("topic_create.html")
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        user = user_from_session_token()

        if not user:
            return redirect(url_for('login'))

        Topic.create(title=title, text=text, author=user)

        return redirect(url_for('index'))


@app.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    user = user_from_session_token()

    return render_template("topic_details.html", topic=topic, user=user)


@app.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topic_edit.html", topic=topic)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        user = user_from_session_token()

        if not user:
            return redirect(url_for('login'))
        elif topic.author.id != user.id:
            return "You are not the author!"
        else:
            topic.title = title
            topic.text = text
            db.add(topic)
            db.commit()

            return redirect(url_for('topic_details', topic_id=topic_id))


@app.route("/topic/<topic_id>/delete", methods=["GET", "POST"])
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topic_delete.html", topic=topic)

    elif request.method == "POST":
        user = user_from_session_token()

        if not user:
            return redirect(url_for('login'))
        elif topic.author_id != user.id:
            return "You are not the author!"
        else:
            db.delete(topic)
            db.commit()
            return redirect(url_for('index'))

if __name__=='__main__':
    app.run(debug=True)