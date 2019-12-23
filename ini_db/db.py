# flask 框架部分,用于前段交互
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# 数据库操作部分
# # SQL
from sqlalchemy import Column, String, Integer, Binary, ForeignKey, \
    create_engine, PrimaryKeyConstraint, and_
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_utils import create_database, database_exists

# # MongoDB
import pymongo

# 异常处理部分
import sqlalchemy
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature

# 设置的相关属性
from conf import conf

Base = declarative_base()

engine = create_engine(
    "{}+{}://{}:{}@{}:{}/{}".format(conf.db_sql_env_sql,
                                    conf.db_sql_env_api,
                                    conf.db_sql_username,
                                    conf.db_sql_user_passwd,
                                    conf.db_sql_ip,
                                    conf.db_sql_port,
                                    conf.db_sql_name))
DBsession = sessionmaker(bind=engine)


# MongoDb - order

client = pymongo.MongoClient(
    host=conf.db_mongodb_ip, port=conf.db_mongodb_port)
db_auth = client.admin
# db_auth.authenticate(conf.db_mongodb_username,
#                      conf.db_mongodb_user_passwd)
db = client[conf.db_mongodb_name]
order = db[conf.db_order_collection]
orderToCheck = db[conf.db_check_collection]

class auth(Base):
    __tablename__ = "user_tbl"

    user_id = Column(String, primary_key=True)
    passwd = Column(String, nullable=False)
    money = Column(Integer, default=0)
    terminal = Column(String)
    token = Column(String)

    def __repr__(self):
        return "user_id: %s, passwd: %s,\n\t money: %d, terminal: %s, token: %s" % (
            self.user_id, self.passwd, self.money, self.terminal, self.token)


class Market(Base):
    __tablename__ = "markets"
    user_id = Column(String, ForeignKey(
        'users.username'), nullable=False)
    store_id = Column(String, nullable=False, primary_key=True, index=True)
    # __dict__ = {"owner_name": owner_name, "item_id": item_id}

    def __repr__(self):
        return "store_id: %s, user_id: %s" % (
            self.store_id, self.user_id)

    # def __init__(self, item_id, owner_name):
    # 	self.item_id = item_id
    # 	self.owner_name = owner_name
    # 	self.__dict__ = {"owner_name": self.owner_name, "item_id": self.item_id}


# BOKK 要使用mongodb来写
class Book(Base):  # TODO: to complete this table
    __tablename__ = "books"
    book_id = Column(String, nullable=False, primary_key=True)
    title = Column(String, index=True)
    author = Column(String)
    publisher = Column(String)
    original_title = Column(String)
    translator = Column(String),
    pub_year = Column(String),
    pages = Column(String),
    recommended_price = Column(Integer, nullable=False),
    currency_unit = Column(String),
    binding = Column(String),
    isbn = Column(String),
    author_intro = Column(String),
    book_intro = Column(String),
    content = Column(String),
    tags = Column(String),
    picture = Column(Binary)

    # def __repr__(self):
    #     return "book_id: %s, title: %s" % (
    #         self.store_id, self.user_id)
    # TODO: 继续完成book类的represent函数


class BookinStore(Base):
    __tablename__ = "bookinstore"
    book_id = Column(String, ForeignKey("books.book_id"),
                     nullable=False, primary_key=True)
    store_id = Column(String, ForeignKey("markets.store_id"),
                      nullable=False, primary_key=True)
    stock = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    # book_info = Column(Class)  # TODO: 需要细化书籍信息，并且判断这个信息和book表中的是否冲突，面向范式编程
    CheckConstraint(stock >= 0)  # 初始库存，库存大于等于0


class Order(Base):
    __tablename__ = "order"
    order_id = Column(String, primary_key = True)
    user_id = Column(String, ForeignKey("auth.user_id"))
    price = Column(Integer,nullable=False)
    status = Column(Integer, nullable=False)

# class Order(Base):
#     __tablename__ = "orders"
#     order_id = Column(String, nullable=False, primary_key=True)
#     price = Column(Integer, nullable=False)
#     store_id = Column(String, ForeignKey("markets.store_id"))
#     user_id = Column(String, ForeignKey("user_tbl.user_id"), nullable=False)
#     status = Column(bool, default=False)
#     # 这里可能要改Class具体的实现形式-------------------------------------------------------------
#     # book_id = Column(Class)


#     def __repr__(self):
#         return "order_id: %s,\n\t price: %d, starter_id: %s, store_id:%s, status: %d" % (
#             self.order_id, self.price, self.user_id, self.store_id, self.status)

# # TODO: whether is there any need to construct a new table to store order-book


# class OrderDetail(Base):
#     __tablename__ = "order_details"
#     order_id = Column(String, ForeignKey("orders.order_id"),
#                       nullable=False, primary_key=True)
#     book_id = Column(String, ForeignKey("books.book_id"),
#                      nullable=False, primary_key=True)
#     count = Column(Integer, nullable=False)
#     # store_id = Column(String, ForeignKey("markets.store_id"))
#     # user_id = Column(String, ForeignKey("user_tbl.user_id"), nullable=False)
#     # status = Column(bool, default=False)


def initDB():
    if not database_exists(engine.url):
        try:
            create_database(engine.url)
            # Base.metadata.create_all(engine) #TODO: compare these two methods to create a database
        except ZeroDivisionError as e:
            print('Error occurs:', e)
        finally:
            print(engine)
            print("connected")
