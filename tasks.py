import os
import json
import requests
from huey import RedisHuey

huey = RedisHuey(url=os.getenv("REDIS_URL"))


@huey.task(retries=10, retry_delay=600)
def send_email_task(receiver_email, subject, text):
    sender_email = os.getenv("MY_SENDER_EMAIL")
    api_key = os.getenv('SENDGRID_API_KEY')

    if sender_email and api_key:
        url = "https://api.sendgrid.com/v3/mail/send"

        data = {"personalizations": [{
                    "to": [{"email": receiver_email}],
                    "subject": subject
                }],

                "from": {"email": sender_email},

                "content": [{
                    "type": "text/plain",
                    "value": text
                }]
        }

        headers = {
            'authorization': "Bearer {0}".format(api_key),
            'content-type': "application/json"
        }

        response = requests.request("POST", url=url, data=json.dumps(data), headers=headers)

        print("Sent to SendGrid")
        print(response.text)
    else:
        print("No env vars or no email address.")
        print("The email was not sent.")
        print("If it was sent, this would be the subject: {}".format(subject))
        print("This would be the text: {}".format(text))
        print("And this would be the receiver: {}".format(receiver_email))