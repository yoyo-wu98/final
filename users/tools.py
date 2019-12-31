#基础操作部件
from ini_db import db
from conf import conf
from ini_db.db import session


#数据操作部件
import pandas as pd
import numpy as np



def insertOneOrder(order_id, store_id, user_id, books, amount, status):
    '''
    在mongoDB中插入一个新的文档
        "order_id" :  订单号
        "store_id" : 店铺号,
        "user_id": 用户信息,
        "books" : 书本信息,是一个json数组，里面由书本id和数量
        "amount" : 交易金额,   
        "status" : 状态， 其中0代表未支付，1代表支付未发货，2代表支付已发货，3代表订单已经完成,-1表示订单被取消,
        "createTime" : 这条订单创建的时间的时间戳
    '''
    newDict = {
        "order_id": order_id,
        "store_id": store_id,
        "user_id": user_id,
        "books": books,
        "amount": amount,
        "status": status,
    }
    db.mongo_order.insert_one(newDict)
    return


def insertOneOderToCheck(order_id, endTime):
    '''
    "order_id" : 订单ID
     "endTime" : 订单结束时间的时间戳
    '''
    newDict = {
        "order_id": order_id,
        "endTime": endTime
    }
    db.orderToCheck.insert_one(newDict)
    return


def calTimeStamp(startTimeStamp):
    '''
    计算时间差：
    timeDiff：时间差，单位为s
    startTimeStamp：开始时的时间戳
    '''
    timeDiff = conf.timeDiff
    return startTimeStamp+timeDiff


def to_dict(self):
    return {c.name : getattr(self, c.name, None) for c in self.__table__.columns}



#用于返回所有可以用于展示的BOOK ID
def getResult(books):
    bookIdList = []
    for i in books:
        bookIdList.append(i.id)
    return bookIdList


def scoreFunc(rank,socre):
    return 10*rank + 0.1*socre

#计算店铺展示的优先级别
def calPriority(storeIdAndBookIdLIst,rankList,salesList):
    theDict = {'key':storeIdAndBookIdLIst,'rank':rankList,'sale':salesList}
    df = pd.DataFrame(theDict)
    df['finalscore'] = []
    df.set_index(['key'],inplace=True)
    df['finalscore'] =  df[scoreFunc(df['rank'],df['sale'])]
    new = df.sort_values(by=['finalscore'],ascending=False)
    return new['key']


def getStoreId(bookIdList):
    if len(bookIdList) ==0:
        return "空的"
    '''
    bookIdList:所有符合搜索要求的书的BOOKID
    根据bookID找出所有出售此书的店铺，并且计算优先级
    '''
    #首先得到所有的符合条件的storeID
    storeIdAndBookIdLIst = []
    salesList = []
    rankList = []
    msg1 = "111"
    for bookId in bookIdList:
        #找到所有符合要求的商家
        stores = session.query(db.BookinStore).filter(db.BookinStore.book_id==bookId).all()
        if len(stores) == 0:
            return "没有商店出售"
        for store in stores:
            #得到这本书在该店的销量
            salesList.append(store.sales)
            #这本书的ID和这家店的ID
            storeIdAndBookIdLIst.append(store.store_id+","+bookId)
            #得到这家店的RANK值
            storeInMarket = session.query(db.Market).filter(db.Market.store_id==store.store_Id).one()
            rankList.append(storeInMarket.rank)
    finalList = calPriority(storeIdAndBookIdLIst,rankList,salesList)
    return finalList
    
    


