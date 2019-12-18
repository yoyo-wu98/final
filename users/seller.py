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

from ..ini_db import db
from .. import Auth as auth
from .. import config

bp = Blueprint("seller", __name__, url_prefix="/seller")


'''
创建商铺函数逻辑：
1. 判断token是否过期，过期返回失败，否则继续；
2. 查看seller_id和store_id是否已经存在，存在则返回‘失败，已有’，没有则继续；
'''


@seller.route("/create_store", methods=['POST'])
def create_market():
    if auth.verify_token() == False:
        return
    if request.method == 'POST':
        # data = request.get_data()
        # data = json.loads(data)  # TODO: verify whether this work - doesn't work
        # user_id = data['user_id']
        # store_id = data['store_id']
        user_id = request.json.get("user_id")
        store_id = request.json.get("store_id")

        if user_id == "" or store_id == "":
            return jsonify({"code": 502, "message": "参数错误，user_id和store_id不能为空。"})
        code, msg = find_market(user_id=user_id, store_id=store_id)
        if code == 200:
            return jsonify({"code": 501, "message": "商铺ID:" + store_id + "已存在。"})
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
    newcolumn = db.Market(
        user_id=user_id, store_id=store_id)
    try:
        session_.add(newcolumn)
        session_.commit()
    except ZeroDivisionError as e:
        session_.rollback()
        return 401, "发生错误: " + e
    finally:
        code, msg = find_market(user_id, store_id)
        if code == 200:
            return code, "创建商铺成功"
        elif code == 500:
            return code, "创建商铺失败，在add_market部分发生错误。"
        else:
            return code, msg

# TODO: Need to initialize the book table


@seller.route("/add_book", methods=['POST'])
def add_book():
    return
