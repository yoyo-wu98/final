from flask import Flask
from users import auth
from ini_db import db
from users import seller
from users import buyer

if __name__ == "__main__":
    db.initDB()
    app = Flask(__name__)
    app.register_blueprint(auth.bp)
    app.register_blueprint(seller.seller)
    app.register_blueprint(buyer.bp)
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
