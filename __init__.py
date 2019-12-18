from flask import Flask
import Auth
from .ini_db import db
from .users import seller

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(Auth.bp)
    app.register_blueprint(seller.bp)
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
