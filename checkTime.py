import  schedule
import time

from ini_db import db

'''
这里可以维护一个本地的字典，或者再在mongoDB里面建立一个collection
'''




def checkAndDelete():
    nowTime = (int)time.time()
    all = db.orderToCheck.find({"endTine":{"$lt":nowTime}})
    
    for i in all:
        order_id = i[id]
        myQuery = {
            "order_id":order_id
        }
        order = db.order.find_one(myQuery)
        status = order["status"]
        if status:
            pass
        else:
            action = {"$set":{"status":-1}}
            db.order.update_one(myQuery,action)

        db.orderToCheck.delete_many(all)
    

    while(True):
        schedule.run_pending()
        time.sleep(5)
