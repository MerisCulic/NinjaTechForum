import os
from sqla_wrapper import SQLAlchemy


db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite?check_same_thread=False"))
