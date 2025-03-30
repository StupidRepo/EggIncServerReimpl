from flask import Flask, g, jsonify
from pymongo.errors import ConnectionFailure

from endpoints.ei import ei_bp
from db import db
from endpoints.ei_afx import ei_afx_bp

app = Flask(__name__)

def check_db_connection():
	try:
		db.command("ping")
		# print("Database connection is successful.")
	except ConnectionFailure as e:
		print(f"Database connection failed: {e}")
		raise Exception("Database connection failed!")

@app.errorhandler(Exception)
def handle_exception(error):
	response = {
		'type': type(error).__name__,
		'message': str(error)
	}
	return jsonify(response), 500

@app.before_request
def before_request():
	check_db_connection()
	g.db = db

@app.teardown_request
def teardown_request(_):
	g.pop("db", None)

app.register_blueprint(ei_bp, url_prefix='/ei')
app.register_blueprint(ei_afx_bp, url_prefix='/ei_afx')

if __name__ == "__main__":
	check_db_connection()
	app.run(debug=True)