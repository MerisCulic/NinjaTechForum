import datetime

from models.settings import db
from models.topic import Topic
from models.user import User
from utils.email_helper import send_email


def new_topics_email():
    print("Cron job: New topics daily email")

    yesterday_topics = db.query(Topic).filter(Topic.created > (datetime.datetime.now() - datetime.timedelta(days=1))).all()

    print(yesterday_topics)

    if not yesterday_topics:
        print("No new topics created yesterday, so no email will be sent.")
    else:
        message = "Topics created yesterday:\n"

        for topic in yesterday_topics:
            message += "- {0}\n".format(topic.title)

        print(message)

        users = db.query(User).all()

        for user in users:
            if user.email:
                send_email(receiver_email=user.email, subject="See new topics at Ninja Tech Forum", text=message)


if __name__ == '__main__':
    new_topics_email()