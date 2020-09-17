from flask import render_template, request, redirect, url_for, make_response, Blueprint
import hashlib
import uuid
import os

from models.settings import db
from models.user import User

from utils.auth_helper import user_from_session_token
from utils.email_helper import send_email


auth_handlers = Blueprint("auth", __name__)


@auth_handlers.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")

    elif request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email-address")
        password = request.form.get("password")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Passwords don't match! Go back and try again."

        username_taken = db.query(User).filter_by(username=username).first()
        if username_taken:
            return "This username is already taken. Please choose another one."

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        verification_token = str(uuid.uuid4())

        user = User.create(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    verification_token=verification_token
                    )

        subject = "Welcome to the Ninja Tech Forum"
#        domain = "{0}.herokuapp.com".format(os.getenv("HEROKU_APP_NAME"))  #for Heroku
        domain = "{0}".format(os.getenv("HEROKU_APP_NAME"))  #for localhost

        text = "Hi! Click on this link to verify your email address: {0}/verify-email/{1}"\
            .format(domain, verification_token)

        send_email(receiver_email=email, subject=subject, text=text)

        response = make_response(redirect(url_for('topic.index')))
        response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')

        return response


@auth_handlers.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    user = db.query(User).filter_by(verification_token=token).first()

    if user:
        user.verified = True
        db.add(user)
        db.commit()

    return render_template("auth/email_verification_result.html", verified=user.verified)


@auth_handlers.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

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

                response = make_response(redirect(url_for('topic.index')))
                response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')

                return response
            else:
                return "Your password is incorrect!"


@auth_handlers.route("/logout")
def logout():
    user = user_from_session_token()

    user.session_token = ""
    db.add(user)
    db.commit()

    return redirect(url_for('topic.index'))
