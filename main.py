from flask import Flask, g
from endpoints.ei import ei_bp
from db import db

app = Flask(__name__)

@app.before_request
def before_request():
	g.db = db

@app.teardown_request
def teardown_request(exception):
	g.pop('db', None)

app.register_blueprint(ei_bp, url_prefix='/ei')

if __name__ == "__main__":
	app.run(debug=True)