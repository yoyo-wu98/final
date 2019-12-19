from flask import Flask
from users import db.auth
from .ini_db import db
from users import seller

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(db.auth.bp)
    app.register_blueprint(seller.seller)
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
