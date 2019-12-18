from flask import Flask
import Auth

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(Auth.bp)
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
