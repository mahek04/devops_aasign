from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///orders.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Menu service URL
MENU_SERVICE_URL = os.getenv('MENU_SERVICE_URL', 'http://localhost:5000')

db = SQLAlchemy(app)

# Database Models
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.String(200))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, nullable=False)
    menu_item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item_name,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.quantity * self.price
        }

# Create tables
with app.app_context():
    db.create_all()

# Helper function to fetch menu items
def fetch_menu_items():
    try:
        response = requests.get(f'{MENU_SERVICE_URL}/api/menu', timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching menu: {e}")
        return []

# Helper function to validate menu item
def validate_menu_item(item_id):
    menu_items = fetch_menu_items()
    for item in menu_items:
        if item['id'] == item_id:
            return item
    return None

# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Proxy endpoint to fetch menu from menu service"""
    menu_items = fetch_menu_items()
    return jsonify(menu_items)

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('customer_name'):
            return jsonify({'error': 'Customer name is required'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'Order must contain at least one item'}), 400
        
        # Validate all items exist in menu
        menu_items = fetch_menu_items()
        menu_dict = {item['id']: item for item in menu_items}
        
        total_amount = 0
        order_items = []
        
        for item_data in data['items']:
            item_id = item_data.get('menu_item_id')
            quantity = item_data.get('quantity', 1)
            
            if item_id not in menu_dict:
                return jsonify({'error': f'Menu item with id {item_id} not found'}), 400
            
            menu_item = menu_dict[item_id]
            price = menu_item['price']
            subtotal = price * quantity
            total_amount += subtotal
            
            order_items.append({
                'menu_item_id': item_id,
                'menu_item_name': menu_item['name'],
                'quantity': quantity,
                'price': price
            })
        
        # Create order
        new_order = Order(
            customer_name=data['customer_name'],
            customer_phone=data.get('customer_phone', ''),
            customer_address=data.get('customer_address', ''),
            total_amount=total_amount,
            status='Pending'
        )
        
        db.session.add(new_order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item_data['menu_item_id'],
                menu_item_name=item_data['menu_item_name'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify(new_order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    data = request.json
    
    if 'status' in data:
        order.status = data['status']
        db.session.commit()
    
    return jsonify(order.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

