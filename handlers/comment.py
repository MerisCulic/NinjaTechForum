from flask import request, redirect, render_template, url_for, Blueprint

from models.settings import db
from models.topic import Topic
from models.comment import Comment

from utils.redis_helper import set_csrf_token, is_valid_csrf
from utils.auth_helper import user_from_session_token

comment_handlers = Blueprint("comment", __name__)


@comment_handlers.route("/topic/<topic_id>/create-comment", methods=["POST"])
def comment_create(topic_id):
    user = user_from_session_token()

    if not user:
        return redirect(url_for('auth.login'))

    csrf = request.form.get("csrf")

    if not is_valid_csrf(csrf, user.username):
        return "CSRF token is not valid!"

    text = request.form.get("text")
    topic = Topic.read(topic_id)

    Comment.create(topic=topic, text=text, author=user)

    return redirect(url_for('topic.topic_details', topic_id=topic_id))


@comment_handlers.route("/comment/<comment_id>/edit", methods=["GET", "POST"])
def comment_edit(comment_id):
    comment = Comment.get_comment(comment_id)

    user = user_from_session_token()

    if not user:
        return redirect(url_for('auth.login'))
    elif comment.author.id != user.id:
        return "You can only edit your own comments!"

    if request.method == "GET":
        csrf_token = set_csrf_token(username=user.username)
        return render_template("comment/comment_edit.html", comment=comment, csrf_token=csrf_token)

    elif request.method == "POST":
        text = request.form.get("text")

        csrf = request.form.get("csrf")

        if is_valid_csrf(csrf, user.username):
            comment.text = text
            db.add(comment)
            db.commit()
            return redirect(url_for('topic.topic_details', topic_id=comment.topic.id))
        else:
            return "CSRF error: tokens don't match!"


@comment_handlers.route("/comment/<comment_id>/delete", methods=["POST"])
def comment_delete(comment_id):
    comment = Comment.get_comment(comment_id)

    user = user_from_session_token()

    if not user:
        return redirect(url_for('auth.login'))
    elif comment.author.id != user.id:
        return "You can only delete your own comments!"

    csrf = request.form.get("csrf")

    if is_valid_csrf(csrf, user.username):
        topic_id = comment.topic.id

        db.delete(comment)
        db.commit()
        return redirect(url_for('topic.topic_details', topic_id=topic_id))
    else:
        return "CSRF error: tokens don't match!"
