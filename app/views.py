from app import app, send_from_directory
import os

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

@app.route('/<path:my_path>', methods=['GET'])
def serve_static_path(my_path):
	return send_from_directory(root, my_path)

@app.route('/', methods=['GET'])
def serve_static_check():
	return send_from_directory(root, "check.xml")
