from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.variable import *


engine = create_engine(SQLALCHEMY_DATABASE_URL_USER, pool_recycle=3600, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()