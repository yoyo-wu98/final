from flask import Blueprint
from flask import request
from flask import jsonify
import time
import json
# 数据库操作部分
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ini_db import db
import db.auth


# 注：标注有很长的-------------------------------的地方说明还需要修改


# Base = declarative_base()

# engin = create_engine('mysql+pymysql://root:Zhj2323864743@127.0.0.1:3306/final')
# DBsession = sessionmaker(bind=engin)


bp = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp.route("/new_order", methods=['POST'])
# 下单
def new_order():
    if request.method == 'POST':
        # 从post body中获取请求
        data = request.get_data()
        json_data = json.load(data.decode("utf-8"))
        user_id = json_data.get("user_id")
        store_id = json_data.get("store_id")
        books = json_data.get("books")
    code, msg, order_id = do_order(user_id, store_id, books)
    return jsonify({"code": code, "msg": msg, "order_id": order_id})


def do_order(user_id, store_id, books):
    session = DBsession()

    order_id = time.strftime("%d/%m/%Y  %H:%M:%S")
    the_order = order(order_id=order_id, user_id=user_id,
                      store_id=store_id, books=books)
    # 用当前时间作为ID，不可能重复
    try:
        session.add(the_order)
    except:
        # 这里需要加上4个expect，或者改成if-else-------------------------------------------------------------
    code = 200
    msg = "下单成功"
    session.commit()
    session.close()
    return code, msg, order_id


def do_pay(user_id, order_id, password):
    session = DBsession()
    # 这里需要加上token判断是否授权失败-------------------------------------------------------------
    try:
        the_order = session.query(order).filter(order.order_id=order_id)
    except:
        code = 502
        msg = "无效参数"
        session.close()
        return code, msg
    else:
        the_sum = 0
        for i in the_order.books:
            the_store = session.query(order).filter(order.order_id=order_id).first().store_id
            the_value_one = session.query(market).filter(market.store_id=the_store, market.id=i.id).price  # 单个价钱\
            market.price += 1
            the_value = the_value_one * i.count
            the_sum += the_value
        the_user = sessiom.query(db.auth).filter(db.auth.user_id=user_id)
        has_money = the_user.money
        if the_sum > has_money:
            code = 501
            msg = "账户余额不足"
            session.close()
            return code, msg
        else:
            has_money -= the_sum
            code = 200
            msh = "付款成功"
            session.close()
            return code, msg


@bp.route("/payment", methods=['POST'])
# 付款
def payment():
    if request.method == 'POST':
        # 从post body中获取请求
        data = request.get_data()
        json_data = json.load(data.decode("utf-8"))
        user_id = json_data.get("user_id")
        order_id = json_data.get("order_id")
        password = json_data.get("password")
    do_pay(user_id, order_id)
    return jsonify({"code": code, "msg": msg})


@bp.route("/add_funds", methods=['POST'])
# 充钱
def add_funds():
    if request.method == 'POST':
        # 从post body中获取请求
        data = request.get_data()
        json_data = json.load(data.decode("utf-8"))
        user_id = json_data.get("user_id")
        add_value = json_data.get("add_value")
        token = request.headers["token"]
        #判断token是否过期或者错误:
        verified = db.auth.verify_token(user_id,token)
        #token正确:
        if verified:
            code, msg = do_add_funds(user_id, add_value)
            return jsonify({"code": code, "msg": msg})
        #token错误,返回报错
        else:
            code = 401
            msg = "token过期"
            return jsonify({"code": code, "msg": msg})


def do_add_funds(user_id, add_value):
    session = DBsession()
    if(add_value <= 0):  # 判断充值金额是否大于0
        code = 501
        msg = "无效参数"
        return code, msg
    the_user = sessiom.query(db.auth).filter(db.auth.user_id=user_id).first()
    the_user.money += add_value
    code = 200
    msg = "充值成功"
    session.commit()
    session.close()
    return code, msg
