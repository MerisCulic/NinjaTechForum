from models.settings import db
from datetime import datetime
import uuid


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    session_token = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    verification_token = db.Column(db.String)
    verified = db.Column(db.Boolean, default=False)

    @classmethod
    def create(cls, username, email, password_hash, verification_token):
        session_token = str(uuid.uuid4())

        user = cls(username=username,
                   email=email,
                   password_hash=password_hash,
                   session_token=session_token,
                   verification_token=verification_token)

        db.add(user)
        db.commit()

        return user
