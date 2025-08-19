import os
from dotenv import load_dotenv



load_dotenv()


SQLALCHEMY_DATABASE_URL_USER = os.environ.get("SQLALCHEMY_DATABASE_URL_USER")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES"))
