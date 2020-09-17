import datetime

from models.settings import db
from models.topic import Topic
from models.user import User
from utils.email_helper import send_email


def new_topics_email():
    #  check if it is Monday
    today = datetime.datetime.now()
    if today.isoweekday() == 1:

        print("Cron job: New topics weekly email")

        weekly_topics = db.query(Topic).filter(Topic.created > (datetime.datetime.now() - datetime.timedelta(days=7))).all()

        print(weekly_topics)

        if not weekly_topics:
            print("No new topics were created last week, so no email will be sent.")
        else:
            message = "Topics created in the previous week:\n"

            for topic in weekly_topics:
                message += "- {0}\n".format(topic.title)

            print(message)

            users = db.query(User).all()

            for user in users:
                if user.email:
                    send_email(receiver_email=user.email, subject="See new topics at Ninja Tech Forum", text=message)


if __name__ == '__main__':
    new_topics_email()
