#flask 框架部分,用于前段交互
from flask import Blueprint
from flask import request
from flask import jsonify
import json
#数据库操作部分
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine,PrimaryKeyConstraint,and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#多线程
import _thread




Base = declarative_base()

engin = create_engine('mysql+pymysql://root:Zhj2323864743@127.0.0.1:3306/final')
DBsession = sessionmaker(bind=engin)


bp = Blueprint("mul",__name__,url_prefix="auth")


class auth(Base):
    __tablename__ = "user_tbl"

    user_id = Column(String(40),primary_key=True)
    passwd = Column(String(40))
    money = Column(Integer)
    terminal = Column(String(30))

#登陆函数路由
@bp.route("/register",methods=['POST'])
def register():
    if request.method=='POST':
        #从post body中获取请求
        data = request.get_data()
        json_data = json.load(data.decode("utf-8"))
        user_id = json_data.get("user_id")
        password = json_data.get("password")
        #创建线程执行创建用户过程
        try:
            code,msg = _thread.start_new_thread(doRigister,(user_id,password))
        except:
            code = 502
            msg = "创建线程失败"
        return jsonify({"code":code,"message":msg})

'''
登陆函数逻辑:
1.首先判断 用户名或者密码是否为空,如果为空,返回失败(但是作业中没有相应的要求,此处自行定义
status code为101).
2.如果均不为空,则向数据库中插入数据

2.1成功,返回status code 200, 并返回一个成功的消息
2.2失败,返回status code 500, 并返回一个“用户名重复的消息”
'''
def doRigister(user_id,password):
    if user_id=='' or password=='':
        code = 101
        msg = "用户名或密码为空"
        return code, msg
    session = DBsession()
    newUser = auth(user_id=user_id,password=password)
    try:
        session.add(newUser)
    except:
        code = 501
        msg="注册失败,用户名重复"
        session.close()
        return code, msg
    code = 200
    msg = "注册成功"
    session.commit()
    session.close()
    return code, msg

#注销用户路由
@bp.route("/ungrgister",methods=['POST'])
def unregister():
    if request.method=='POST':
        #从post body中获取请求
        data = request.get_data()
        json_data = json.load(data.decode("utf-8"))
        user_id = json_data.get("user_id")
        password = json_data.get("password")
