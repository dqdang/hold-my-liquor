#!/usr/bin/python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload, relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, Sequence

import os
import psycopg2
import sqlalchemy as sql

Base = declarative_base()

# heroku pg:psql -a hold-my-liquor
# import dburl
url = os.environ['HEROKU_POSTGRESQL_WHITE_URL']
engine = sql.create_engine(url, pool_size=17, client_encoding='utf8')

# class Users(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     fb_id = Column(BigInteger, nullable=False, unique=True)
#     locations = relationship('Location', secondary='current', backref=sql.orm.backref('current', lazy='dynamic'))

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    fb_id = Column(BigInteger, nullable=False, unique=True)
    locations = Column(String, nullable=False, unique=True)

# class Location(Base):
#     __tablename__ = "location"
#     id = Column(Integer, primary_key=True)
#     location_name = Column(String, nullable=False, unique=True)
    
#     def __eq__(self, other):
#         return self.location_name == other.location_name

# class Current(Base):
#     __tablename__ = "current"
#     location_id = Column(Integer, ForeignKey('location.id'), primary_key=True)
#     location = relationship('Location', uselist=False)
    
table_dict = {
        "Users": Users,
        # "Location": Location,
        # "Current": Current
}

def start_sess():
    Session = sessionmaker(bind=engine, autocommit=False)
    return Session()

def create_tables():
    sess = start_sess()
    Base.metadata.create_all(engine)
    sess.commit()
    sess.close()

def admin_exists(fb_id, sess=start_sess()):
    return sess.query(Admins).filter(Admins.user.has(Users.fb_id==fb_id)).scalar()

def user_exists(user, sess=start_sess()):
    return sess.query(Users).filter(Users.fb_id==user).scalar()

def location_exists(loc, sess):
    return sess.query(Location).filter(Location.loc_name.like(loc)).scalar()

def current_exists(cur, sess):
    return sess.query(Current).filter(Current.product.has(Location.location_name==cur)).scalar()

def new_items(prod_names, prod_urls=None):
    new = []
    restock = {}
    sess = start_sess()

    for i, name in enumerate(prod_names):
        prod = prod_exists(name,sess)
        cur = current_exists(name,sess)
        # new product
        if not prod:
            if(prod_urls):
                new.append((name, prod_urls[i]))
            else:
                new.append((name, None))
        # restock
        if prod and (not cur):
            for sub in prod.subscribers:
                if prod_urls:
                    restock.setdefault(sub.fb_id, []).append((name, prod_urls[i]))
                else:
                    restock.setdefault(sub.fb_id, []).append(name)
    
    sess.close()
    return new, restock

# def insert_products(vlist):
#     sess = start_sess()
#     prods = []
#     users = get_object(Users, sess)

#     for v in vlist:
#         product = Products(prod_name=v)
#         product.subscribers.extend(users)
#         prods.append(product)

#     sess.add_all(prods)
#     sess.commit()
#     sess.close()

#     return prods

# def insert_admin(fb_id, sess=start_sess()):
    
#     user = user_exists(fb_id, sess)
#     if admin_exists(fb_id, sess) or not user:
#         sess.close()
#         return False

#     new_admin = Admins()
#     new_admin.user = user

#     sess.add(new_admin)
#     sess.commit()
#     sess.close()
#     return True

def insert_user(value):
    sess = start_sess()
    
    if user_exists(value, sess):
        sess.close()
        return False
        
    user = Users(fb_id=value)
    
    sess.add(user)
    sess.commit()
    sess.close()
    return True

# def insert_current(vlist, url_list=None):
#     sess = start_sess()
#     prods = []

#     sess.query(Current).delete()

#     if not vlist:
#         return

#     for i, v in enumerate(vlist):
#         prod = get_product(v, sess)
#         curr = Current()
#         curr.product = prod
#         if url_list:
#             curr.prod_url = url_list[i]
#         prods.append(curr)

#     sess.add_all(prods)
#     sess.commit()
#     sess.close()

""" Private getters """
def get_object(table, sess=start_sess()):
    results = sess.query(table).all()
    return results

# def get_product(prod, sess=start_sess()):
#     return sess.query(Products).filter(Products.prod_name==prod).first()

# def get_subscribers(prod, sess=start_sess()):
#     p = sess.query(Products).filter(Products==prod).first()
#     rv = p.subscribers.all()
#     return rv

""" Public getters """
def get_table(table, column):
    sess = start_sess()
    results = sess.query(getattr(table_dict[table],column)).all()
    sess.close()
    return [] if len(results) == 0 else list(zip(*results))[0]

# def get_current():
#     sess = start_sess()
#     current = sess.query(Products.prod_name).join(Current).all()
#     sess.close()
#     return list(zip(*current))[0]

# def get_subscriptions(fb_id):
#     sess = start_sess()
#     user = user_exists(fb_id, sess)

#     if user:
#         rv = [prod.prod_name for prod in user.subscriptions]
#         sess.close()
#         return rv
        
#     sess.close()
#     return None

def delete_user(fb_id):
    sess = start_sess()
    user = user_exists(fb_id, sess)

    if user:
        user.subscriptions.clear()
        sess.delete(user)
        sess.commit()
        sess.close()
        return True

    sess.close()
    return False
