#!/usr/bin/env python3

from flask import Flask
from . import Auth
from .users import *


if __name__== "__main__":
    app = Flask(__name__)
    app.register_blueprint(Auth.bp)
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)