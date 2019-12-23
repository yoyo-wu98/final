from ini_db import  db
from conf import conf

def insertOneOrder(order_id,store_id,user_id,books,amount,status):
    '''
    在mongoDB中插入一个新的文档
        "order_id" :  订单号
        "store_id" : 店铺号,
        "user_id": 用户信息,
        "books" : 书本信息,是一个json数组，里面由书本id和数量
        "amount" : 交易金额,   
        "status" : 状态， 其中0代表未支付，1代表支付未发货，2代表支付已发货，3代表订单已经完成，-1表示订单超时，-2表示订单被取消,
        "createTime" : 这条订单创建的时间的时间戳
    '''
    newDict = {
        "order_id" : order_id,
        "store_id" : store_id,
        "user_id": user_id,
        "books" : books,
        "amount" : amount,   
        "status" : status,
    }
    db.order.insert_one(newDict)
    return

def insertOneOderToCheck(order_id, endTime):
    '''
    "order_id" : 订单ID
     "endTime" : 订单结束时间的时间戳
    '''
    newDict = {
        "order_id" : order_id,
        "endTime" : endTime
    }
    db.orderToCheck.insert_one(newDict)
    return
        
            
def calTimeStamp( startTimeStamp):
    '''
    计算时间差：
    timeDiff：时间差，单位为s
    startTimeStamp：开始时的时间戳
    '''
    timeDiff = conf.timeDiff
    return startTimeStamp+timeDiff


