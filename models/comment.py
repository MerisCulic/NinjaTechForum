from models.settings import db
from utils.email_helper import send_email
from datetime import datetime


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")

    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    topic = db.relationship("Topic")

    created = db.Column(db.DateTime, default=datetime.now())

    @classmethod
    def create(cls, text, author, topic):
        comment = cls(text=text, author=author, topic=topic)
        db.add(comment)
        db.commit()

        if topic.author.email:
            send_email(receiver_email=topic.author.email, subject="New comment for your topic!",
                       text="Your topic {} has a new comment.".format(topic.title))

        return comment

    @classmethod
    def read_all(cls, topic):
        comments = db.query(Comment).filter_by(topic=topic).all()

        return comments

    @classmethod
    def get_comment(cls, comment_id):
        comment = db.query(Comment).get(int(comment_id))

        return comment
