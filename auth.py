  #flask 框架部分,用于前段交互
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_httpauth import HTTPTokenAuth
import functools

#数据库操作部分
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine,PrimaryKeyConstraint,and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#异常处理部分
import sqlalchemy
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature


Base = declarative_base()

engin = create_engine('mysql+pymysql://root:Zhj2323864743@127.0.0.1:3306/final')
DBsession = sessionmaker(bind=engin)

bp = Blueprint("mul",__name__,url_prefix="/auth")

myauth = HTTPTokenAuth()

class auth(Base):
    __tablename__ = "user_tbl"

    user_id = Column(String(40),primary_key=True)
    passwd = Column(String(40))
    money = Column(Integer)
    terminal = Column(String(30))
    token = Column(String(50))

def createToken(user_id):
    '''
    生成一个token
    para user_id : 用户id
    返回一个token
    '''
    #生成一个6min内都有效的token
    MAX_TOKEN_AGE=3600
    token_generator = Serializer("secret", expires_in=MAX_TOKEN_AGE)
    token = token_generator.dumps({"user_id":user_id})
    return token
def verify_token(user_id ,token):
    '''
    1.首先检查user_id是否有错
    2.其次检查token是否为空,如果为空,则说明已经登出
    3.随后检验token的正确性和已经是否过期
    '''
    session = DBsession()
    user =session.query(auth).filter(auth.user_id==user_id).first()
    #user id是否出错
    if user is None:
        session.close()
        return False
    #是否已经登出
    if user.token=="":
        session.close()
        return False
    s = Serializer("secret",expires_in=3600)
    #判断是否过期或者错误
    try:
        s.loads(token)
    except SignatureExpired:
        #过期
        return False
    except BadSignature:
        #token错误
        return False
    return True

#登陆函数路由
@bp.route("/register",methods=['POST'])
def register():
    if request.method=='POST':
        #从post body中获取请求
        user_id  = request.json.get("user_id")
        password = request.json.get("password")
        #执行插入请求
        code,msg = doRigister(user_id=user_id,password=password)
        return jsonify({"code":code,"message":msg})

def doRigister(user_id,password):
    '''
    登陆函数逻辑:
    1.首先判断 用户名或者密码是否为空,如果为空,返回失败(但是作业中没有相应的要求,此处自行定义
    status code为101).
    2.如果均不为空,则向数据库中插入数据

    2.1成功,返回status code 200, 并返回一个成功的消息
    2.2失败,返回status code 500, 并返回一个“用户名重复的消息”
    '''
    if user_id=='' or password=='':
        code = 101
        msg = "用户名或密码为空"
        return code, msg
    session = DBsession()
    newUser = auth(user_id=user_id,passwd=password,money=0)
    try:
        #向数据控发送回话,commit必须加在try中,因为这一步是真正意义上的修改数据库
        session.add(newUser)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        code = 501
        msg="注册失败,用户名重复"
        session.close()
        return code, msg
    else:
        code = 200
        msg = "注册成功"
        session.close()
        return code, msg

#注销用户路由
@bp.route("/unregister",methods=['POST'])
def unregister():
    if request.method=='POST':
        #从post body中获取请求
        user_id =  request.json.get("user_id")
        password = request.json.get("password")
        code, msg = doUnregister(user_id,password)
        return jsonify({"code":code,"message":msg})


def doUnregister(user_id,password):
    '''
    undo逻辑:
    直接在数据库中查找:
    1. 存在则返回成功
    2. 失败则返回用户名或者密码错误
    '''
    session = DBsession()
    try:
        user = session.query(auth).filter(auth.user_id==user_id,auth.passwd==password).first()
        session.delete(user)
        session.commit()
    except sqlalchemy.orm.exc.UnmappedInstanceError:
        code = 401
        msg = "注销失败，用户名不存在或密码不正确"
        session.close()
        return code, msg
    else:
        code =200
        msg = "注销成功"
        return code, msg


#用户登陆路由
@bp.route("/login",methods=['POST'])
def login():
    if request.method=='POST':
        user_id =  request.json.get("user_id")
        password = request.json.get("password")
        terminal = request.json.get("terminal")
        code,msg,token = doLogin(user_id,password)
        return jsonify({"code":code,"msg":msg,"token":token})

def doLogin(user_id,password):
    '''
    登陆函数逻辑:
    查找在db中是否有匹配的user_id和密码:
    1. 没有, 返回401并报错,token为None型
    2. 有, 返回200并显示成功,创建相应token,并且在后端存储token
    '''
    session = DBsession()
    user = session.query(auth).filter(auth.user_id==user_id,auth.passwd==password).first()
    if user is None:
        code = 401
        msg = "登陆失败,用户名或密码错误"
        session.close()
        return code, msg, None
    else:
        code =200
        msg = "登陆成功"
        token = createToken(user_id=user_id)
        user.token = token
        session.commit()
        session.close()
        return code, msg, token
    


#用户更改密码路由
@bp.route("/password",methods=['POST'])
def password():
    if request.method=='POST':
        user_id =  request.json.get("user_id")
        oldPassword = request.json.get("oldPassword")
        newPassword = request.json.get("newPassword")
        code, msg = doChangePassword(user_id,oldPassword,newPassword)
        return jsonify({"code":code,"msg":msg})

def doChangePassword(user_id,oldPasswd,newPasswd):
    '''
    更改密码逻辑:
    查找是否用户名和账号密码是否匹配且存在
    1.匹配且存在:直接修改,返回200和成功信息
    2.不满足条件:返回401和报错信息
    '''
    session = DBsession()
    try:
        user = session.query(auth).filter(auth.user_id==user_id,auth.passwd==oldPasswd).first()
        user.passwd = newPasswd
        session.commit()
    except AttributeError:
        session.close()
        code = 401
        msg = "更改密码失败,用户名或密码错误"
        return code,msg
    else:
        code = 200
        msg = "更改密码成功"
        session.close()
        return code, msg


#用户登出的路由

@bp.route("/logout",methods=['POST'])
def logout():
    '''
    登出操作逻辑:
    1. 判断token是否过关
    2. 过关则执行退出操作
    '''
    if request.method=='POST':
        user_id = request.json.get("user_id")
        #首先从headers中获取token的值
        token = request.headers["token"]
        #校验token是否正确
        ifVerified = verify_token(user_id,token)
        #如果正确,执行登出操作
        if ifVerified:
            code,msg = doLogout(user_id)
            return jsonify({"code":code,"message":msg})
        #不正确,返回报错
        else:
            code = 401
            msg = "登出失败,用户名或者token错误"
        return jsonify({"code":code,"message":msg})

def doLogout(user_id):
    #将token置为空
    code = 200
    msg = "登出成功"
    session = DBsession()
    user =session.query(auth).filter(auth.user_id==user_id).first()
    user.token = ""
    session.commit()
    session.close()
    return code,msg


