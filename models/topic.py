from models.settings import db
from datetime import datetime


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    text = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")
    created = db.Column(db.DateTime, default=datetime.now())

    @classmethod
    def create(cls, title, text, author):
        topic = cls(title=title, text=text, author=author)

        db.add(topic)
        db.commit()

        return topic

    @classmethod
    def update(cls, topic_id, title, text):
        topic = db.query(Topic).get(int(topic_id))

        topic.title = title
        topic.text = text

        db.add(topic)
        db.commit()

        return topic
