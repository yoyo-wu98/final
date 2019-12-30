# flask 框架部分,用于前段交互
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# 数据库操作部分

# # SSH

# # SQL
from sqlalchemy import Column, String, Integer, Binary, ForeignKey, \
    create_engine, PrimaryKeyConstraint, and_,Float
from sqlalchemy.sql.schema import CheckConstraint, Index
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_utils import create_database, database_exists

# # MongoDB
import pymongo

# 全文索引
from sqlalchemy_fulltext import FullText, FullTextSearch


# 异常处理部分
import sqlalchemy
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature

# 设置的相关属性
from conf import conf


Base = declarative_base()
def to_dict(self):
    return {c.name : getattr(self, c.name, None) for c in self.__table__.columns}
Base.to_dict = to_dict
# with SSHTunnelForwarder(
#     (conf.ssh_host, conf.ssh_port),  # Remote server IP and SSH port
#     ssh_username=conf.ssh_user,
#     ssh_password=conf.ssh_password,
#     remote_bind_address=(conf.db_sql_ip, conf.db_sql_port)
# ) as server:
#     server.start()  # start ssh sever
#     local_port = str(server.local_bind_port)
#     engine = create_engine("{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(conf.db_sql_env_sql,
#                                                                         conf.db_sql_env_api,
#                                                                         conf.db_sql_username,
#                                                                         conf.db_sql_user_passwd,
#                                                                         '127.0.0.1',
#                                                                         conf.db_sql_port,
#                                                                         conf.db_sql_name),
#                            pool_recycle=1)
engine = create_engine("mysql+pymysql://root:981119@127.0.0.1:3306/final?charset=utf8",pool_size=20)
# engine = create_engine("{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(conf.db_sql_env_sql,
                                                                    # conf.db_sql_env_api,
                                                                    # conf.db_sql_username,
                                                                    # conf.db_sql_user_passwd,
                                                                    # conf.db_sql_ip,
                                                                    # conf.db_sql_port,
                                                                    # conf.db_sql_name))

DBsession=sessionmaker(bind=engine)
session = DBsession()
# MongoDb - order

client=pymongo.MongoClient(
    host=conf.db_mongodb_ip, port=conf.db_mongodb_port)
db_auth=client.admin
db=client[conf.db_mongodb_name]
mongo_order=db[conf.db_order_collection]
orderToCheck=db[conf.db_check_collection]


class auth(Base):
    __tablename__="user_tbl"

    user_id=Column(String, primary_key=True)
    passwd=Column(String, nullable=False)
    money=Column(Integer, default=0)
    terminal=Column(String)
    token=Column(String)

    def __repr__(self):
        return "user_id: %s, passwd: %s,\n\t money: %d, terminal: %s, token: %s" % (
            self.user_id, self.passwd, self.money, self.terminal, self.token)


class Market(Base):
    __tablename__="markets"
    user_id=Column(String, nullable=False)
    store_id=Column(String, nullable=False, primary_key=True, index=True)
    rank = Column(Integer)
    # __dict__ = {"owner_name": owner_name, "item_id": item_id}

    def __repr__(self):
        return "store_id: %s, user_id: %s" % (
            self.store_id, self.user_id)

    # def __init__(self, item_id, owner_name):
    # 	self.item_id = item_id
    # 	self.owner_name = owner_name
    # 	self.__dict__ = {"owner_name": self.owner_name, "item_id": self.item_id}


# BOOK 要使用mongodb来写picture的部分，mongodb的大文本存储并没有mysql高效，但是不在这里用就没地方用了。（手动狗头
# 全文索引没用的话就用这个网站里的 https://www.jb51.net/article/64453.htm ； 不支持中文的话： https://blog.csdn.net/yygg329405/article/details/97110984
# 再不济：https://github.com/mengzhuo/sqlalchemy-fulltext-search
# 中文的支持还不怎么样，可能需要改一点初始化的schema才能用
class Book(FullText, Base):  # TODO: to complete this table
    __tablename__="book"
    __fulltext_columns__=('book_intro', 'author_intro', 'content')
    id=Column(String, nullable=False, primary_key=True)
    title=Column(String, index=True)
    author=Column(String, index=True)
    publisher=Column(String)
    original_title=Column(String)
    translator=Column(String)
    pub_year=Column(String)
    pages=Column(String)
    price=Column(Integer, nullable=False)
    currency_unit=Column(String)
    binding=Column(String)
    isbn=Column(String)
    author_intro=Column(String)
    book_intro=Column(String)
    content=Column(String)
    tags=Column(String, index=True)
    picture=Column(Binary)
    Index("book_intro", mysql_prefix="FULLTEXT",mysql_with_parser="n-gram")
    Index("author_intro", mysql_prefix="FULLTEXT",mysql_with_parser="n-gram")
    Index("content", mysql_prefix="FULLTEXT",mysql_with_parser="n-gram")

    # def __repr__(self):
    #     return "bsession = db.DBsession()ook_id: %s, title: %s" % (
    #         self.store_id, self.user_id)
    # TODO: 继续完成book类的represent函数


class BookinStore(Base):
    __tablename__="bookinstore"
    book_id=Column(String,
                     nullable=False, primary_key=True)
    store_id=Column(String,
                      nullable=False, primary_key=True)
    stock=Column(Integer, nullable=False,default=0)
    price=Column(Integer, nullable=False,default=0)
    sales = Column(Integer)
    # book_info = Column(Class)  # TODO: 需要细化书籍信息，并且判断这个信息和book表中的是否冲突，面向范式编程
    CheckConstraint(stock >= 0)  # 初始库存，库存大于等于0

class order(Base):
    __tablename__ = 'order_tbl'
    order_id = Column(String,primary_key=True,)
    user_id = Column(String)
    store_id = Column(String)
    price = Column(Float)
    status = Column(Integer)



# class Order(Base):
#     __tablename__="order"
#     order_id=Column(String, primary_key=True)
#     user_id=Column(String, ForeignKey("auth.user_id"))
#     price=Column(Integer, nullable=False)
#     status=Column(Integer, nullable=False)

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
    conn=engine.connect()
    result=conn.execute("select 1")
    print(result.fetchone())
    if not database_exists(engine.url):
        try:
            create_database(engine.url)
            # Base.metadata.create_all(engine) #TODO: compare these two methods to create a database
        except ZeroDivisionError as e:
            print('Error occurs:', e)
        finally:
            print(engine)
            print("connected")
