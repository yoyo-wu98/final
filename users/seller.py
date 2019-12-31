#!/usr/bin/env python3
from flask import Blueprint
from flask import jsonify
from flask import request
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint
from sqlalchemy.sql.schema import CheckConstraint
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.sql.sqltypes import TIMESTAMP
import datetime

from ini_db import db
from ini_db.db import session

from . import auth
from conf import conf

seller = Blueprint("seller", __name__, url_prefix="/seller")

def testIfOK(user_id,password):
    user = session.query(db.auth).filter(db.auth.user_id==user_id,db.auth.passwd==password).first()
    if user is None:
        return False
    else:
        return True


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
            return  jsonify({"登陆失败，用户id或token错误。"}) , 401 # TODO: 需要修改，等一波邹哥哥的函数

        if user_id == "" or store_id == "":
            code = 502
            msg = "参数错误，user_id和store_id不能为空。"
            return jsonify({"message":msg}),code
        
        code, msg = find_market(user_id=user_id, store_id=store_id)
        if code == 200:
            code = 501
            msg =  "商铺ID：" + store_id + "已存在。"
            return jsonify({"message":msg}),code
        elif code == 401:
            return jsonify({"message":msg}),code
        elif code != 500:
            code = 509
            msg = "参数错误，查找商铺时返回未知参数。"
            return jsonify({"message":msg}),code

        # 执行插入请求
        code, msg = add_market(user_id=user_id, store_id=store_id)
        return jsonify({"message":msg}),code


def find_market(user_id, store_id):
    element = None
    # session = db.DBsession()
    try:
        element = session.query(db.Market).filter(
            db.Market.user_id == user_id, db.Market.store_id == store_id).one()
        # session.close()
    except ZeroDivisionError as e:
        print("发生错误: ", e)
        return 401, "发生错误: " + e
    finally:
        if element != None:
            return 200, element
        else:
            return 500, "用户" + user_id + "没有此商铺" + store_id + "。"


def add_market(user_id, store_id):
    # session = db.DBsession()
    newcolumn = db.Market(
        user_id=user_id, store_id=store_id)
    try:
        session.add(newcolumn)
        session.commit()
    except ZeroDivisionError as e:
        session.rollback()
        # session.close()
        return 401, "发生错误: " + e
    finally:
        # session.close()
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
        book_id = request.json.get("book_info")["id"]
        book_price = request.json.get("book_info")["price"]
        stock_level = request.json.get("stock_level")

        if auth.verify_token(user_id, token) == False:
            code = 401
            msg = "登陆失败，用户id或token错误。"
            return jsonify({"message":msg}),code

        if user_id == "" or store_id == "" or book_id == "" or user_id == None or store_id == None or book_id == None:
            msg = "参数错误，user_id，store_id和book_id不能为空。"
            code = 502
            return jsonify({"message":msg}),code
        code, msg = find_market(
            user_id=user_id, store_id=store_id)  # TODO: 检查是DB不存在还是DB不属于user
        if code == 500:
            code = 501
            msg = "商铺ID：" + store_id + "不属于用户：" + user_id
            return jsonify({"message":msg}),code
        elif code == 401:
            return jsonify({"message":msg}),code
        elif code != 200:
            code = 509
            msg = "参数错误，验证商铺是否存在时返回未知参数。"
            return jsonify({"message":msg}),code

        code, msg = find_book_in_store(book_id=book_id, store_id=store_id)
        if code == 200:
            code = 501
            msg = "商铺ID：" + store_id + "已有图书：" + book_id + "，建议改成增加库存函数add_stock。"
            return jsonify({"message":msg}),code
        elif code == 401:
            return jsonify({"message":msg}),code
        elif code != 500:
            code = 509
            msg = "参数错误，验证商铺是否拥有图书时返回未知参数。"
            return jsonify({"message":msg}),code

        # 执行插入请求
        code, msg = add_book_to_store(
            book_id=book_id, store_id=store_id, stock=stock_level,price = book_price)
        return jsonify({"message":msg}),code


def find_book_in_store(book_id, store_id):  # TODO: 修改判断：是否这个商店有了这本书
    element = None
    # session = db.DBsession()
    try:
        element = session.query(db.BookinStore).filter(
            db.BookinStore.book_id == book_id, db.BookinStore.store_id == store_id).one()
        # session.close()
    except ZeroDivisionError as e:
        print("发生错误: ", e)
        return 401, "发生错误: " + e
    finally:
        if element != None:
            return 200, element
        else:
            return 500, "店铺" + store_id + "没有此书" + book_id + "销售。"


def add_book_to_store(book_id, store_id, stock,price):
    # session = db.DBsession()
    #caocaocaocoacoacoacoacoacoasocoacoacoacoacoaocaocoacoacoacoaco
    newcolumn = db.BookinStore(
        book_id=book_id, store_id=store_id,stock=stock,price = price)
    try:
        session.add(newcolumn)
        session.commit()
    except ZeroDivisionError as e:
        session.rollback()
        # session.close()
        return 401, "发生错误: " + e
    finally:
        # session.close()
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
    if request.method == 'POST':

        token = request.headers["token"]

        user_id = request.json.get("user_id")
        store_id = request.json.get("store_id")
        book_id = request.json.get("book_id")
        add_stock_level = request.json.get("add_stock_level")

        if auth.verify_token(user_id, token) == False:
            code = 401
            msg = "登陆失败，用户id或token错误。"
            return jsonify({"message":msg}),code

        if user_id == "" or store_id == "" or book_id == "" or add_stock_level == "":
            code = 502
            msg = "参数错误，user_id和store_id不能为空。"
            return jsonify({"message":msg}),code
        code, msg = find_market(user_id=user_id, store_id=store_id)
        #
        if code == 500:
            code = 501
            msg ="商铺ID：" + store_id + "不属于用户：" + user_id
            return jsonify({"message":msg}),code
        elif code == 401:
            return jsonify({"message":msg}),code
        elif code != 200:
            code =  509
            msg = "参数错误，验证商铺是否存在时返回未知参数。"
            return jsonify({"message":msg}),code

        code, msg = find_book_in_store(book_id=book_id, store_id=store_id)
        if code == 500:
            code = 501
            msg = "商铺ID：" + store_id + "没有图书：" + book_id + "在售，建议改成增加图书函数add_book。"
            return jsonify({"message":msg}),code
        elif code == 401:
            return jsonify({"message":msg}),code
        elif code != 200:
            code =  509
            msg = "参数错误，验证商铺是否拥有图书时返回未知参数。"
            return jsonify({"message":msg}),code

        # 执行插入请求
        code, msg = add_up_book_stock(
            book_id=book_id, store_id=store_id, add_stock_level=add_stock_level)
        return jsonify({"message":msg}),code


def add_up_book_stock(book_id, store_id, add_stock_level):
    # session = db.DBsession()
    element = session.query(db.BookinStore).filter(db.BookinStore.book_id == book_id, db.BookinStore.store_id == store_id).first()
    if element is None:
        code = 501
        msg = "没有这本书"
        return code, msg
    original_stock = element.stock
    try:
        element.stock = original_stock + add_stock_level
        session.commit()
    except ZeroDivisionError as e:
        session.rollback()
        # session.close()
        return 401, "发生错误: " + e
    finally:
        element = session.query(db.BookinStore).filter(
            db.BookinStore.book_id == book_id, db.BookinStore.store_id == store_id).first()
        new_stock = element.stock
        # session.close()
        if new_stock == original_stock + add_stock_level:
            return 200, "在店铺：{}增加图书：{}库存成功".format(store_id, book_id)
        else:
            return 401, "增加书本库存失败，在add_up_book_stock部分发生错误。"


#卖家发货
@seller.route("/send",methods=['POST'])
def send():
    if request.method=='POST':
        #获取用户数据
        user_id = request.json.get("user_id")
        order_id = request.json.get("order_id")
        token = request.headers["token"]
        password = request.json.get("password")
        #检查token是否正确：
        ifVerified = testIfOK(user_id,password)
        if ifVerified:
            code, msg = doSend(user_id,order_id)
        else:
            code = 401
            msg = "登出失败，用户名或者token错误"
        return jsonify( {"msg": msg}),code

def doSend(user_id,order_id):
    #首先判断订单是否存在
    try:
        the_order = session.query(db.order).filter(db.order.order_id==order_id).one()
    except:
        session.rollback()
        code = 501
        msg = "找不到订单"
        return code, msg

    #判断订单状态是否为已支付
    status = the_order.status
    if status != 1:
        code = 502
        msg = "订单状态异常"
        return code, msg

    #判断该订单是否属于该商家
    the_store = the_order.store_id
    the_owner = session.query(db.Market).filter(db.Market.store_id==the_store).first().user_id
    if the_owner != user_id:
        code = 503
        msg = "该订单不属于您"
        return code, msg

    #成功发货
    the_order.status = 2
    code = 200
    msg = "发货成功！"
    session.commit()
    return code, msg