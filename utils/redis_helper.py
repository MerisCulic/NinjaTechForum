import os
import uuid
import smartninja_redis


redis = smartninja_redis.from_url(os.environ.get("REDIS_URL"))


def set_csrf_token(user):
    csrf_token = str(uuid.uuid4())
    redis.set(name=csrf_token, value=user.username)

    return csrf_token


def is_valid_csrf(csrf, username):
    redis_csrf_username = None
    redis_csrf_username_hex = redis.get(name=csrf)
    if redis_csrf_username_hex:
        redis_csrf_username = redis_csrf_username_hex.decode()

    if not redis_csrf_username:
        return False

    if redis_csrf_username != username:
        return "CSRF token is not valid!"

    return True