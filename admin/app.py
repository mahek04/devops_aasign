from flask import Flask, jsonify, request, send_from_directory
import os
import requests

app = Flask(__name__)

MENU_SERVICE_URL = os.getenv('MENU_SERVICE_URL', 'http://menu:5000')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    try:
        payload = request.get_json(force=True)
        # pass-through validation could be added here if needed
        resp = requests.post(f"{MENU_SERVICE_URL}/api/menu", json=payload, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.route('/api/menu', methods=['GET'])
def list_menu_items():
    try:
        resp = requests.get(f"{MENU_SERVICE_URL}/api/menu", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)


