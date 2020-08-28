from flask import render_template, request, redirect, url_for, Blueprint

from models.settings import db
from models.topic import Topic
from models.comment import Comment

from utils.auth_helper import user_from_session_token
from utils.redis_helper import set_csrf_token, is_valid_csrf


topic_handlers = Blueprint("topic", __name__)


@topic_handlers.route('/', methods=["GET", "POST"])
def index():
    user = user_from_session_token()
    topics = db.query(Topic).all()

    return render_template("topic/index.html", user=user, topics=topics)


@topic_handlers.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    user = user_from_session_token()

    if request.method == "GET":
        csrf_token = set_csrf_token(username=user.username)
        return render_template("topic/topic_create.html", csrf_token=csrf_token)

    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        csrf = request.form.get("csrf")

        if not user:
            return redirect(url_for('auth.login'))

        if not is_valid_csrf(csrf, username=user.username):
            return "CSRF token is not valid!"

        Topic.create(title=title, text=text, author=user)

        return redirect(url_for('topic.index'))


@topic_handlers.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    user = user_from_session_token()
    topic = Topic.read(topic_id)
    comments = Comment.read_all(topic)
    csrf_token = set_csrf_token(username=user.username)

    # START test background tasks (TODO: delete this code later)
    if os.getenv('REDIS_URL'):
        from tasks import get_random_num
        get_random_num()
    # END test background tasks

    return render_template("topic/topic_details.html",
                           topic=topic,
                           user=user,
                           csrf_token=csrf_token,
                           comments=comments)


@topic_handlers.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = Topic.read(topic_id)
    user = user_from_session_token()

    if request.method == "GET":
        csrf_token = set_csrf_token(username=user.username)
        return render_template("topic/topic_edit.html", topic=topic, csrf_token=csrf_token)

    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        if not user:
            return redirect(url_for('auth.login'))
        elif topic.author.id != user.id:
            return "You are not the author!"
        else:
            Topic.update(topic_id, title, text)

            return redirect(url_for('topic.topic_details', topic_id=topic_id))


@topic_handlers.route("/topic/<topic_id>/delete", methods=["GET", "POST"])
def topic_delete(topic_id):
    topic = Topic.read(topic_id)

    if request.method == "GET":
        return render_template("topic/topic_delete.html", topic=topic)

    elif request.method == "POST":
        user = user_from_session_token()

        if not user:
            return redirect(url_for('auth.login'))
        elif topic.author_id != user.id:
            return "You are not the author!"
        else:
            comments = Comment.read_all(topic)
            for comment in comments:
                db.delete(comment)
            db.delete(topic)

            db.commit()
            return redirect(url_for('topic.index'))
