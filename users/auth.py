# flask 框架部分,用于前段交互
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import functools

# 数据库操作部分
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_fulltext import FullText, FullTextSearch
# 异常处理部分
import sqlalchemy
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature
from sqlalchemy.exc import IntegrityError
from conf import conf
from ini_db import db
from ini_db.db import session

from users.tools import getStoreId
from users.tools import getResult




# Base = declarative_base()

# engin = create_engine('mysql+pymysql://root:Zhj2323864743@127.0.0.1:3306/final')
# DBsession = sessionmaker(bind=engin)

bp = Blueprint("mul", __name__, url_prefix="/auth")


def createToken(user_id):
    '''
    生成一个token
    para user_id : 用户id
    返回一个token
    '''
    # 生成一个6min内都有效的token
    MAX_TOKEN_AGE = 3600
    token_generator = Serializer(conf.token_key, expires_in=MAX_TOKEN_AGE)
    token = token_generator.dumps({"user_id": user_id})
    return token


def verify_token(user_id, token):
    '''
    1.首先检查user_id是否有错
    2.其次检查token是否为空,如果为空,则说明已经登出
    3.随后检验token的正确性和已经是否过期
    '''
    user = session.query(db.auth).filter(db.auth.user_id == user_id).first()
    # user id是否出错
    if user is None:
        return False
    # 是否已经登出
    if user.token == "":
        return False
    s = Serializer(conf.token_key, expires_in=3600)
    # 判断是否过期或者错误
    try:
        s.loads(token)
    except SignatureExpired:
        # 过期
        return False
    except BadSignature:
        # token错误
        return False
    return True


# 登陆函数路由
@bp.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        # 从post body中获取请求
        user_id = request.json.get("user_id")
        password = request.json.get("password")
        # 执行插入请求
        code, msg = doRigister(user_id=user_id, password=password)

        return jsonify({ "message": msg}),code


def doRigister(user_id, password):
    '''
    登陆函数逻辑:
    1.首先判断 用户名或者密码是否为空,如果为空,返回失败(但是作业中没有相应的要求,此处自行定义
    status code为101).
    2.如果均不为空,则向数据库中插入数据

    2.1成功,返回status code 200, 并返回一个成功的消息
    2.2失败,返回status code 500, 并返回一个“用户名重复的消息”
    '''
    if user_id == '' or password == '':
        code = 101
        msg = "用户名或密码为空"
        return code, msg
    newUser = db.auth(user_id=user_id, passwd=password, money=0)

    try:
        # 向数据控发送回话,commit必须加在try中,因为这一步是真正意义上的修改数据库
        session.add(newUser)
        session.commit()
    except :
        session.rollback()
        code = 502
        msg = "注册失败,用户名重复"
        # session.close()
        return code, msg
    code = 200
    msg = "注册成功"
    # session.close()
    return code, msg

# 注销用户路由
@bp.route("/unregister", methods=['POST'])
def unregister():
    if request.method == 'POST':
        # 从post body中获取请求
        user_id = request.json.get("user_id")
        password = request.json.get("password")
        code, msg = doUnregister(user_id, password)
        return jsonify({"code": code, "message": msg}),code


def doUnregister(user_id, password):
    '''
    undo逻辑:
    直接在数据库中查找:
    1. 存在则返回成功
    2. 失败则返回用户名或者密码错误
    '''
    session = db.DBsession()
    try:
        user = session.query(db.auth).filter(
            db.auth.user_id == user_id, db.auth.passwd == password).first()
        session.delete(user)
        session.commit()
    except sqlalchemy.orm.exc.UnmappedInstanceError:
        session.rollback()
        code = 401
        msg = "注销失败，用户名不存在或密码不正确"
        # session.close()
        return code, msg
    else:
        code = 200
        msg = "注销成功"
        return code, msg


# 用户登陆路由
@bp.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        user_id = request.json.get("user_id")
        password = request.json.get("password")
        terminal = request.json.get("terminal")
        code, msg, token = doLogin(user_id, password)
        return jsonify({"code": code, "msg": msg, "token": token}),code



def doLogin(user_id, password):
    '''
    登陆函数逻辑:
    查找在db中是否有匹配的user_id和密码:
    1. 没有, 返回401并报错,token为None型
    2. 有, 返回200并显示成功,创建相应token,并且在后端存储token
    '''

    # session = db.DBsession()
    user = session.query(db.auth).filter(
        db.auth.user_id == user_id, db.auth.passwd == password).first()

    if user is None:
        code = 401
        msg = "登陆失败,用户名或密码错误"
        # session.close()
        return code, msg, None
    else:
        code = 200
        msg = "登陆成功"
        token = createToken(user_id=user_id)
        user.token = token
        session.commit()
        # session.close()
        return code, msg, token


# 用户更改密码路由
@bp.route("/password", methods=['POST'])
def password():
    if request.method == 'POST':
        user_id = request.json.get("user_id")
        oldPassword = request.json.get("oldPassword")
        newPassword = request.json.get("newPassword")
        code, msg = doChangePassword(user_id, oldPassword, newPassword)
        return jsonify({"code": code, "msg": msg}),code


def doChangePassword(user_id, oldPasswd, newPasswd):
    '''
    更改密码逻辑:
    查找是否用户名和账号密码是否匹配且存在
    1.匹配且存在:直接修改,返回200和成功信息
    2.不满足条件:返回401和报错信息
    '''
    # session = db.DBsession()
    try:

        user = session.query(db.auth).filter(
            db.auth.user_id == user_id, db.auth.passwd == oldPasswd).first()

        user.passwd = newPasswd
        session.commit()
    except AttributeError:
        # session.close()
        session.rollback()
        code = 401
        msg = "更改密码失败,用户名或密码错误"
        return code, msg
    code = 200
    msg = "更改密码成功"
        # session.close()
    return code, msg

# 用户登出的路由


@bp.route("/logout", methods=['POST'])
def logout():
    '''
    登出操作逻辑:
    1. 判断token是否过关
    2. 过关则执行退出操作
    '''
    if request.method == 'POST':
        user_id = request.json.get("user_id")
        # 首先从headers中获取token的值
        token = request.headers["token"]
        # 校验token是否正确
        ifVerified = verify_token(user_id, token)
        # 如果正确,执行登出操作
        if ifVerified:
            code, msg = doLogout(user_id)
            return jsonify({"code": code, "message": msg})
        # 不正确,返回报错
        else:
            code = 401
            msg = "登出失败,用户名或者token错误"
        return jsonify({"code": code, "message": msg}),code


def doLogout(user_id):
    # 将token置为空
    code = 200
    msg = "登出成功"

    # session = db.DBsession()
    try:
        user = session.query(db.auth).filter(db.auth.user_id == user_id).first()
        user.token = ""
        session.commit()
    except:
        session.rollback()
        code=401
        msg= "用户名错误"
        return code, msg
    # session.close()
    return code, msg


# 查询，输入json：
# where：查询的域 （title:标题；author:作者；）
# content：查询信息
# return 查询结果
# TODO:结果分页




@bp.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        option = request.json.get("where")
        keyword = request.json.get("content")

        if keyword == "" or option == "":
            return jsonify({"code": 502, "message": "参数错误，查询域where与查询内容content不能为空。"})
        if option == "title":
            words = keyword.split()
            rule = and_(*[db.Book.title.like('%{keyword}%'.format(keyword=w)) for w in words])
            result = session.query(db.Book).filter(rule).all()
            if result != None:
                code = 200
                result = getResult(result)
                msg = getStoreId(result)
                return jsonify({"msg":msg}),code
        elif option == "author":
            words = keyword.split()
            rule = and_(*[db.Book.author.like('%{keyword}%'.format(keyword=w)) for w in words])
            result = session.query(db.Book).filter(rule).all()
            
            if result != None:
                code = 200
                msg = getStoreId(result)
                return jsonify({"msg":msg}),code
        elif option == "publisher":
            words = keyword.split()
            rule = and_(*[db.Book.publisher.like('%{keyword}%'.format(keyword=w)) for w in words])
            result = session.query(db.Book).filter(rule).all()
            if result != None:
                code = 200
                msg = getStoreId(result)
                return jsonify({"msg":msg}),code
        elif option == "author_intro":
            # session = db.DBsession()
            result = session.query(db.Book).filter(
                FullTextSearch('author_intro', db.Book)).all()
            if result != "":
                code = 200
                msg = getStoreId(result)
                return jsonify({"msg":msg}),code
        elif option == "book_intro":
            # session = db.DBsession()
            result = session.query(db.Book).filter(
                FullTextSearch('book_intro', db.Book)).all()
            if result != None:
                code = 200
                msg = getStoreId(result)
                return jsonify({"msg":msg}),code
        elif option == "content":
            # session = db.DBsession()
            result = session.query(db.Book).filter(
                FullTextSearch('content', db.Book)).all()
            if result != None:
                code = 200
                msg = getStoreId(result)
                return jsonify({"msg":msg}),code
        else:
            code = 502
            return jsonify({ "message": "参数错误，查询域where不适宜查询。"}),code
        code = 501
        return jsonify({"code": 501, "message": "查询不到结果。"}),code
