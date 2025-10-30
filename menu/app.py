from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///menu.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category
        }

# Create tables
with app.app_context():
    db.create_all()
    # Add some sample data if the table is empty
    if MenuItem.query.count() == 0:
        sample_items = [
            MenuItem(name='Burger', description='Delicious beef burger', price=9.99, category='Main Course'),
            MenuItem(name='Pizza', description='Cheese pizza', price=12.99, category='Main Course'),
            MenuItem(name='Salad', description='Fresh garden salad', price=6.99, category='Appetizer'),
            MenuItem(name='Pasta', description='Italian pasta', price=11.99, category='Main Course'),
            MenuItem(name='Ice Cream', description='Vanilla ice cream', price=4.99, category='Dessert'),
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()

# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    new_item = MenuItem(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        category=data.get('category', '')
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
