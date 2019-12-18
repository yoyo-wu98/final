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

from .. import Auth as auth

Base = declarative_base()

class Market(Base):
	__tablename__ = 'market'
	owner_id = Column(Integer, ForeignKey(
		'users.username'), nullable=False)
	store_id = Column(Integer, nullable=False, primary_key=True, index =True)
	# __dict__ = {"owner_name": owner_name, "item_id": item_id}

	def __repr__(self):
		return "store_id: %d, owner_id: %d" % (
                            self.store_id, self.owner_id)
	
	# def __init__(self, item_id, owner_name):
	# 	self.item_id = item_id
	# 	self.owner_name = owner_name
	# 	self.__dict__ = {"owner_name": self.owner_name, "item_id": self.item_id}


'''
创建商铺函数逻辑：
1. 判断token是否过期，过期返回失败，否则继续；
2. 查看seller_id和store_id是否已经存在，存在则返回‘失败，已有’，没有则继续
'''
engine = create_engine('mysql+pymysql://root:Zhj2323864743@127.0.0.1:3306/final')
DBsession = sessionmaker(bind=engine)
session_ = DBsession();

bp = Blueprint("seller",__name__,url_prefix="/seller")

def init_market_():
	Base.metadata.create_all(engine)

@seller.route("/create_store", methods=['POST'])
def create_market():
    if auth.verify_token() == False:
        return 
    if request.method=='POST':
        user_id =  request.json.get("user_id")
        store_id = request.json.get("store_id")
        #执行插入请求
        code,msg = find_market(user_id=user_id,store_id=store_id)
        if code == 200:
            return jsonify({"code":501, "message":"商铺ID:" + store_id + "已存在。"})
        elif code == 401:
            return jsonify({"code":code,"message":msg})
        elif code != 500:
            return jsonify({"code":509,"message":"参数错误，查找商铺时返回未知参数。"})
        code,msg = add_market(user_id=user_id,store_id=store_id)
        return jsonify({"code":code,"message":msg})

def find_market(user_id, store_id):
	element = None
	try:
		element = session_.query(Market).filter(
			Market.user_id == user_id, Market.store_id == store_id).one()
	except ZeroDivisionError as e:
		print("发生错误: ", e)
		return 401, "发生错误: " + e
	finally:
		if element != None:
			return 200, element
		else:
			return 500, "用户" + user_id +"没有此商铺"+ store_id + "。"

def add_market(user_id, store_id):
	temp_max = db_init.session_.query(db_init.Items).count()
	for item_name in item_name_list:
		item, ok = find_item_by_name(item_name)
		if ok == False and item == "cannot find the item.":
			temp_max += 1
			i = random.randint(1, 30)
			level = i
			category_ = random.randint(0,1)
			category = category_
			p = random.randint(level, level + 20) # 稍微溢价
			newcolumn = db_init.Items(
				item_id=temp_max, item_name = item_name, price = p, status = 0, item_level = level, category = category, item_owner=None)
			try:
				db_init.session_.add(newcolumn)
				# pdb.set_trace()
				db_init.session_.commit()
			except ZeroDivisionError as e:
				db_init.session_.rollback()
				return "Failed to add the item {}.".format(item_name), False
			finally:
			# flg = db_init.items_col.insert_one({ "name": item_name, "price": p, "status": 0, "owner" : "none", "category":category,"level":level  })
			# if flg.inserted_id != None:
			# 	return 1
			# else:
			# 	return "System Error"
				print("Successfully added.")
		else:
			print("Already have this item in items.")