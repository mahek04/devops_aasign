from flask import Flask, jsonify, send_from_directory, request
import requests
import os

app = Flask(__name__)

ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order:5001')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/orders', methods=['GET'])
def list_orders():
    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}/api/orders", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id: int):
    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}/api/orders/{order_id}", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)


