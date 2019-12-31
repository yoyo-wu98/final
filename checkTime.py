import schedule
import time

from ini_db import db
from ini_db.db import session


def checkAndDelete():
    nowTime = (int)(time.time())
    print(nowTime)
    all_item = db.orderToCheck.find({"endTime": {"$lt": nowTime}})

    for i in all_item:
        order_id = i["order_id"]
        print(order_id)
        order = session.query(db.order).filter(
            db.order.order_id == order_id).first()
        status = order.status
        # 如果订单的状态不为0的话，说明已经无法自动取消，pass
        if status:
            db.orderToCheck.delete_one(i)
            pass
        # 订单状态为0， 可以自动取消
        else:
            print("删除成功")
            order.status = -1
            session.commit()
            db.orderToCheck.delete_one(i)


schedule.every(10).seconds.do(checkAndDelete)

while(True):
    schedule.run_pending()
    time.sleep(1)
