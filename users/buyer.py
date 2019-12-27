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
from users import auth


from users import tools
import time

# 注：标注有很长的-------------------------------的地方说明还需要修改


# Base = declarative_base()

# engin = create_engine('mysql+pymysql://root:Zhj2323864743@127.0.0.1:3306/final')
session = db.DBsession()


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
    order_id = time.strftime("%d/%m/%Y  %H:%M:%S")
    # 用当前时间作为ID，不可能重复
    theSum = 0 #表示需要支付的钱
    try:
        session.query(db.auth).filter(db.auth.user_id==user_id).one()
    except:
        code = 501
        msg = "买家用户ID不存在"
        session.close()
        return code, msg
    try:
        session.query(db.Market).filter(db.Market.store_id==store_id).one()
    except:
        code = 502
        msg = "商铺ID不存在"
        session.close()
        return code, msg
    try:
        for i in books:
            the_book = session.query(db.BookinStore).filter(db.BookinStore.store_id==store_id, db.BookinStore.book_id == i.id).one()
            if(i.count > the_book.stock):
                code = 504
                msg = "商品库存不足"
                session.close()
                return code, msg
            theSum += i.count * the_book.price
    except:
        code = 503
        msg = "购买的图书不存在"
        session.close()
        return code, msg
    
    #增加一个SQL表存储订单信息
    temp = db.order(order_id, user_id, store_id, theSum)
    session.add(temp)

    '''
    创建新的订单
    默认状态为0（未支付）
    '''
    status = 0
    amount=theSum
    tools.insertOneOrder(order_id=order_id,store_id=store_id,user_id=user_id,books=books,
                                            amount=amount,status=status)
    timeStamp = int(time.time())
    '''
    创建一个待删除的表
    '''
    endTime = tools.calTimeStamp(startTimeStamp=timeStamp)
    tools.insertOneOderToCheck(order_id=order_id,endTime=endTime)                                        
    code = 200
    msg = "下单成功"
    session.commit()
    session.close()
    return code, msg, order_id



@bp.route("/payment", methods=['POST'])
# 付款
def payment():
    if request.method == 'POST':
        # 从post body中获取请求
        data = request.get_data()
        json_data = json.load(data.decode("utf-8"))
        user_id = json_data.get("user_id")
        order_id = json_data.get("order_id")
        token = request.headers["token"]
        verified = auth.verify_token(user_id, token)
        if verified:
            code, msg = do_pay(user_id, order_id)
        else:
            code = 401
            msg = "token错误"
        return jsonify({"code": code, "msg": msg})

    
def do_pay(user_id, order_id):
    try:
        the_order = session.query(db.order).filter(db.order.order_id==order_id).one
    except:
        code = 502
        msg = "无效参数"
        session.close()
        return code, msg
    else:
        the_sum = 0
        #----------------------------------------------------------------------------------------------------------------
        #直接调用oder表中的数据，需要修改
        #----------------------------------------------------------------------------------------------------------------
        for i in the_order.books:
            the_store = session.query(db.order).filter(db.order.order_id==order_id).first().store_id
            the_value_one = session.query(db.market).filter(db.market.store_id==the_store, db.market.id==i.id).price  # 单个价钱\
            market.price += 1
            the_value = the_value_one * i.count
            the_sum += the_value
        the_user = sessiom.query(db.auth).filter(db.auth.user_id==user_id)
        has_money = the_user.money
        if the_sum > has_money:
            code = 501
            msg = "账户余额不足"
            session.close()
            return code, msg
        else:
            has_money -= the_sum
            code = 200
            msg = "付款成功"
            session.close()
            return code, msg

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
        # 判断token是否过期或者错误:
        verified = auth.verify_token(user_id, token)
        # token正确:
        if verified:
            code, msg = do_add_funds(user_id, add_value)
        # token错误,返回报错
        else:
            code = 401
            msg = "token过期"
        return jsonify({"code": code, "msg": msg})


def do_add_funds(user_id, add_value):
    if(add_value <= 0):  # 判断充值金额是否大于0
        code = 501
        msg = "无效参数"
        return code, msg
    the_user = session.query(db.auth).filter(db.auth.user_id==user_id).first()
    the_user.money += add_value
    code = 200
    msg = "充值成功"
    session.commit()
    session.close()
    return code, msg

#取消订单路由函数
@bp.route("/cancel",methods=['POST'])
def cancel():
    '''
    取消订单逻辑：
    1.判断token是否过关
    2.执行cancel操作
    '''
    if request.method=='POST':
        #获取用户数据
        user_id = request.json.get("user_id")
        order_id = request.json.get("order_id")
        token = request.headers["token"]
        #检查token是否正确：
        ifVerified = auth.verify_token(user_id,token)
        if ifVerified:
            code, msg = doCancel(user_id,order_id)
        else:
            code = 401
            msg = "登出失败，用户名或者token错误"
        return jsonify({"code": code, "msg": msg})

def doCancel(user_id,order_id):
    '''
    doCancel逻辑：
    1.检查orderid和用户名是否错误
    2.检查status 是否为0或1
        2.1 如果是0或1，则修改为-2，返回成功
        2.2如果是2或3，订单已经发出，返回失败
        2.3其他情况则说明订单已经被取消，返回失败
    '''
    # myQuery = {
    #         "order_id": order_id,
    #         "user_id":user_id
    #     }
    # myDoc = db.order.find_one(myQuery)

    myDoc = session.query(db.order).filter(db.order.order_id==order_id, db.user_id == user_id).first()

    if myDoc is None:
        code = 401
        msg = "用户名或订单号错误"
    else:
        # status = myDoc["status"]
        status = myDoc.status
        if status==0 or status==1:
            # action = {"$set":{"status":-2}}
            # db.order.update_one(myQuery,action)
            status = -2
            session.commit()
            code = 200
            msg = "取消订单成功"
        elif status==2 or status==3:
            code = 402
            msg = "订单已经发出"
        else:
            code = 403
            msg = "订单已无效"
        return code, msg
