from flask import request,jsonify,current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


s = Serializer(current_app["SECRET_KEY"],expires_in=3600)
print(s)