#!/usr/bin/env python3
from flask import Blueprint
from flask import jsonify
from flask import request
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint
from sqlalchemy.sql.schema import CheckConstraint
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql.sqltypes import TIMESTAMP
import datetime

from ini_db import db
from . import auth
from conf import conf

seller = Blueprint("seller", __name__, url_prefix="/seller")


'''
创建商铺函数逻辑：
1. 判断token是否过期，过期返回失败，否则继续；
2. 查看seller_id和store_id是否已经存在，存在则返回‘失败，已有’，没有则继续；
'''


@seller.route("/create_store", methods=['POST'])
def create_market():
    if request.method == 'POST':
        token = request.headers["token"]
        user_id = request.json.get("user_id")
        store_id = request.json.get("store_id")

        if auth.verify_token(user_id, token) == False:
            return 401, "登陆失败，用户id或token错误。"  # TODO: 需要修改，等一波邹哥哥的函数

        if user_id == "" or store_id == "":
            return jsonify({"code": 502, "message": "参数错误，user_id和store_id不能为空。"})
        code, msg = find_market(user_id=user_id, store_id=store_id)
        if code == 200:
            return jsonify({"code": 501, "message": "商铺ID：" + store_id + "已存在。"})
        elif code == 401:
            return jsonify({"code": code, "message": msg})
        elif code != 500:
            return jsonify({"code": 509, "message": "参数错误，查找商铺时返回未知参数。"})

        # 执行插入请求
        code, msg = add_market(user_id=user_id, store_id=store_id)
        return jsonify({"code": code, "message": msg})


def find_market(user_id, store_id):
    element = None
    session = db.DBsession()
    try:
        element = session.query(db.Market).filter(
            db.Market.user_id == user_id, db.Market.store_id == store_id).one()
        session.close()
    except ZeroDivisionError as e:
        print("发生错误: ", e)
        return 401, "发生错误: " + e
    finally:
        if element != None:
            return 200, element
        else:
            return 500, "用户" + user_id + "没有此商铺" + store_id + "。"


def add_market(user_id, store_id):
    session = db.DBsession()
    newcolumn = db.Market(
        user_id=user_id, store_id=store_id)
    try:
        session.add(newcolumn)
        session.commit()
    except ZeroDivisionError as e:
        session.rollback()
        session.close()
        return 401, "发生错误: " + e
    finally:
        session.close()
        code, msg = find_market(user_id, store_id)
        if code == 200:
            return code, "创建商铺成功"
        elif code == 500:
            return code, "创建商铺失败，在add_market部分发生错误。"
        else:
            return code, msg


# TODO: Need to initialize the book table
@seller.route("/add_book", methods=['POST'])  # TODO: 需要重新考虑很多东西
def add_book():
    if request.method == 'POST':
        token = request.headers["token"]

        user_id = request.json.get("user_id")
        store_id = request.json.get("store_id")
        book_id = request.json.get("id")
        stock_level = request.json.get("stock_level")

        if auth.verify_token(user_id, token) == False:
            return 401, "登陆失败，用户id或token错误。"

        if user_id == "" or store_id == "" or book_id == "":
            return jsonify({"code": 502, "message": "参数错误，user_id和store_id不能为空。"})
        code, msg = find_market(
            user_id=user_id, store_id=store_id)  # TODO: 检查是DB不存在还是DB不属于user
        if code == 500:
            return jsonify({"code": 501, "message": "商铺ID：" + store_id + "不属于用户：" + user_id})
        elif code == 401:
            return jsonify({"code": code, "message": msg})
        elif code != 200:
            return jsonify({"code": 509, "message": "参数错误，验证商铺是否存在时返回未知参数。"})

        code, msg = find_book_in_store(book_id=book_id, store_id=store_id)
        if code == 200:
            return jsonify({"code": 501, "message": "商铺ID：" + store_id + "已有图书：" + book_id + "，建议改成增加库存函数add_stock。"})
        elif code == 401:
            return jsonify({"code": code, "message": msg})
        elif code != 500:
            return jsonify({"code": 509, "message": "参数错误，验证商铺是否拥有图书时返回未知参数。"})

        # 执行插入请求
        code, msg = add_book_to_store(
            book_id=book_id, store_id=store_id, stock=stock_level)
        return jsonify({"code": code, "message": msg})


def find_book_in_store(book_id, store_id):  # TODO: 修改判断：是否这个商店有了这本书
    element = None
    session = db.DBsession()
    try:
        element = session.query(db.BookinStore).filter(
            db.BookinStore.book_id == book_id, db.BookinStore.store_id == store_id).one()
        session.close()
    except ZeroDivisionError as e:
        print("发生错误: ", e)
        return 401, "发生错误: " + e
    finally:
        if element != None:
            return 200, element
        else:
            return 500, "店铺" + store_id + "没有此书" + book_id + "销售。"


def add_book_to_store(book_id, store_id, stock):
    session = db.DBsession()
    newcolumn = db.BookinStore(
        book_id=book_id, store_id=store_id)
    try:
        session.add(newcolumn)
        session.commit()
    except ZeroDivisionError as e:
        session.rollback()
        session.close()
        return 401, "发生错误: " + e
    finally:
        session.close()
        code, msg = find_book_in_store(book_id, store_id)
        if code == 200:
            return code, "在店铺：{}增加图书：{}成功".format(store_id, book_id)
        elif code == 500:
            return code, "创建店铺失败，在add_book_to_store部分发生错误。"
        else:
            return code, msg


# TODO: Need to initialize the book table
@seller.route("/add_stock_level", methods=['POST'])  # TODO: 需要重新考虑很多东西
def add_stock_level():
    if auth.verify_token() == False:
        return 401, "登陆失败。"  # TODO: 需要修改，等一波邹哥哥的函数
    if request.method == 'POST':

        token = request.headers["token"]

        user_id = request.json.get("user_id")
        store_id = request.json.get("store_id")
        book_id = request.json.get("book_id")
        add_stock_level = request.json.get("add_stock_level")

        if auth.verify_token(user_id, token) == False:
            return 401, "登陆失败，用户id或token错误。"

        if user_id == "" or store_id == "" or book_id == "" or add_stock_level == "":
            return jsonify({"code": 502, "message": "参数错误，user_id和store_id不能为空。"})
        code, msg = find_market(user_id=user_id, store_id=store_id)
        if code == 500:
            return jsonify({"code": 501, "message": "商铺ID：" + store_id + "不属于用户：" + user_id})
        elif code == 401:
            return jsonify({"code": code, "message": msg})
        elif code != 200:
            return jsonify({"code": 509, "message": "参数错误，验证商铺是否存在时返回未知参数。"})

        code, msg = find_book_in_store(book_id=book_id, store_id=store_id)
        if code == 500:
            return jsonify({"code": 501, "message": "商铺ID：" + store_id + "没有图书：" + book_id + "在售，建议改成增加图书函数add_book。"})
        elif code == 401:
            return jsonify({"code": code, "message": msg})
        elif code != 200:
            return jsonify({"code": 509, "message": "参数错误，验证商铺是否拥有图书时返回未知参数。"})

        # 执行插入请求
        code, msg = add_up_book_stock(
            book_id=book_id, store_id=store_id, add_stock_level=add_stock_level)
        return jsonify({"code": code, "message": msg})


def add_up_book_stock(book_id, store_id, add_stock_level):
    session = db.DBsession()
    element = session.query(db.BookinStore).filter(
        db.BookinStore.book_id == book_id, db.BookinStore.store_id == store_id).one()
    original_stock = element.stock
    try:
        element.stock = original_stock + add_stock_level
        session.commit()
    except ZeroDivisionError as e:
        session.rollback()
        session.close()
        return 401, "发生错误: " + e
    finally:
        element = session.query(db.BookinStore).filter(
            db.BookinStore.book_id == book_id, db.BookinStore.store_id == store_id).one()
        new_stock = element.stock
        session.close()
        if new_stock == original_stock + add_stock_level:
            return 200, "在店铺：{}增加图书：{}库存成功".format(store_id, book_id)
        else:
            return 401, "增加书本库存失败，在add_up_book_stock部分发生错误。"
