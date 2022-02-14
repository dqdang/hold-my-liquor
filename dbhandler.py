from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload, relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, Sequence

import os
import psycopg2
import sqlalchemy as sql

Base = declarative_base()

# heroku pg:psql -a hold-my-liquor
# import dburl
url = os.getenv("DATABASE_URL")  # or other relevant config var
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
engine = sql.create_engine(url, pool_size=17, client_encoding='utf8')


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    fb_id = Column(BigInteger, nullable=False, unique=True)
    location = Column(String, nullable=False, unique=True)


table_dict = {
    "Users": Users
}


def start_sess():
    Session = sessionmaker(bind=engine, autocommit=False)
    return Session()


def create_tables():
    sess = start_sess()
    Base.metadata.create_all(engine)
    sess.commit()
    sess.close()


def user_exists(user, sess=start_sess()):
    return sess.query(Users).filter(Users.fb_id == user).scalar()


def insert_user(value):
    sess = start_sess()

    if user_exists(value, sess):
        sess.close()
        return False

    user = Users(fb_id=value)
    user.location = "san francisco"

    sess.add(user)
    sess.commit()
    sess.close()
    return True


""" Private getters """


def _get_object(table, sess=start_sess()):
    results = sess.query(table).all()
    return results


""" Public getters """


def get_table(table, column):
    sess = start_sess()
    results = sess.query(getattr(table_dict[table], column)).all()
    sess.close()
    return [] if len(results) == 0 else list(zip(*results))[0]


def get_location(fb_id):
    sess = start_sess()
    user = user_exists(fb_id, sess)
    if user:
        rv = user.location
        sess.close()
        return rv
    sess.close()
    return None


def change_location(fb_id, location):
    sess = start_sess()
    user = user_exists(fb_id, sess)

    if user:
        user.location = location
        sess.commit()
        sess.close()
        return True

    sess.close()
    return False


def delete_user(fb_id):
    sess = start_sess()
    user = user_exists(fb_id, sess)

    if user:
        sess.delete(user)
        sess.commit()
        sess.close()
        return True

    sess.close()
    return False
