from flask import Flask


if __name__=="__main__":
    app = Flask(__name__)
    app.register_blueprint()
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)