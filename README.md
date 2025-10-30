# Food Ordering System

A microservices-based food ordering system with separate menu and order services.

## Services

### 1. Menu Service (Port 5000)
- View all menu items
- Add new menu items
- SQLite database for menu storage
- Beautiful UI with category filtering

### 2. Order Service (Port 5001)
- Browse menu items from the menu service
- Add items to shopping cart
- Place orders with customer details
- SQLite database for order storage
- Real-time cart updates
- Order confirmation

## Features

✅ **Menu Management**: Browse items by category  
✅ **Shopping Cart**: Add/remove items, adjust quantities  
✅ **Order Validation**: Only items from menu can be ordered  
✅ **Customer Details**: Name, phone, delivery address  
✅ **Order Tracking**: View all orders with status  
✅ **Responsive Design**: Works on desktop and mobile  
✅ **Indian Currency**: All prices in Rupees (₹)  

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the services:
- **Menu Service**: http://localhost:5000
- **Order Service**: http://localhost:5001

### Option 2: Run Locally

#### Menu Service
```bash
cd menu
pip install -r requirements.txt
python app.py
```

#### Order Service (in a new terminal)
```bash
cd order
pip install -r requirements.txt
python app.py
```

## API Endpoints

### Menu Service (http://localhost:5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/menu` | Get all menu items |
| POST | `/api/menu` | Add new menu item |

**Example: Add Menu Item**
```bash
curl -X POST http://localhost:5000/api/menu \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Biryani",
    "description": "Delicious chicken biryani",
    "price": 299.99,
    "category": "Main Course"
  }'
```

### Order Service (http://localhost:5001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/menu` | Get menu items (proxied from menu service) |
| GET | `/api/orders` | Get all orders |
| POST | `/api/orders` | Create new order |
| GET | `/api/orders/:id` | Get specific order |
| PUT | `/api/orders/:id/status` | Update order status |

**Example: Place Order**
```bash
curl -X POST http://localhost:5001/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_phone": "9876543210",
    "customer_address": "123 Main Street",
    "items": [
      {
        "menu_item_id": 1,
        "quantity": 2
      },
      {
        "menu_item_id": 3,
        "quantity": 1
      }
    ]
  }'
```

## Database

Both services use **SQLite** databases:
- Menu Service: `menu/instance/menu.db`
- Order Service: `order/instance/orders.db`

### Sample Data

The menu service automatically creates sample items:
- Burger - ₹9.99 (Main Course)
- Pizza - ₹12.99 (Main Course)
- Salad - ₹6.99 (Appetizer)
- Pasta - ₹11.99 (Main Course)
- Ice Cream - ₹4.99 (Dessert)

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Menu Service   │         │  Order Service  │
│   Port: 5000    │◄────────│   Port: 5001    │
│                 │  HTTP   │                 │
│  ┌───────────┐  │         │  ┌───────────┐  │
│  │ SQLite DB │  │         │  │ SQLite DB │  │
│  │ (menu.db) │  │         │  │(orders.db)│  │
│  └───────────┘  │         │  └───────────┘  │
└─────────────────┘         └─────────────────┘
```

The order service fetches menu items from the menu service to:
1. Display available items to customers
2. Validate orders contain only existing menu items
3. Get current prices for order calculation

## Technologies Used

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite
- **Containerization**: Docker, Docker Compose

## Troubleshooting

### Order service can't connect to menu service

If running locally, make sure:
1. Menu service is running on port 5000
2. Order service environment variable `MENU_SERVICE_URL` is set correctly

Default: `http://localhost:5000`

For Docker: The services communicate via the internal network using service names.

### Port already in use

Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "5002:5000"  # Maps host port 5002 to container port 5000
```

## Future Enhancements

- [ ] User authentication
- [ ] Payment integration
- [ ] Real-time order status updates
- [ ] Admin dashboard
- [ ] PostgreSQL/MySQL support
- [ ] Order history for customers
- [ ] Email notifications

## License

MIT License

