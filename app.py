import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
from collections import defaultdict
from datetime import datetime
import re
import db.main as db
db.doshidd

app = Flask(__name__)
app.secret_key = "kisan_kart_secret"

# Simple In-Memory Storage
global_products = [
    {
        "_id": "1",
        "name": "Fresh Organic Tomatoes",
        "category": "Vegetables",
        "price": 40.0,
        "qty": 20,
        "area": "Nashik",
        "description": "Farm-fresh ripe tomatoes, perfect for salads and cooking.",
        "image": "background.png",
        "status": "available"
    },
    {
        "_id": "2",
        "name": "Basmati Rice",
        "category": "Grains",
        "price": 120.0,
        "qty": 50,
        "area": "Punjab",
        "description": "Long-grain aromatic basmati rice from the fields of Punjab.",
        "image": "background2.png",
        "status": "available"
    }
]
global_orders = []

@app.context_processor
def inject_globals():
    return dict(is_demo_mode=True, current_user={'name': 'Guest User', 'is_authenticated': True, 'type': 'customer'})

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index(): #home/main page
    return render_template('index.html')

@app.route('/register/farmer')
def register_farmer():
    return render_template('farmerside_login.html')

@app.route('/register', methods=['POST'])
def register():
    user_type = request.form.get('user_type')
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    lat = request.form.get('lat')
    lng = request.form.get('lng')
    if not re.match(r"^[a-zA-Z0-9\s]{2,50}$", name):
        flash("Invalid name Please use 2-50 alphanumeric characters.", "danger")
        return redirect(url_for('register_farmer' if user_type == 'farmer' else 'consumer'))
    if not re.match(r"^\d{10}$", phone):
        flash("Phone number must be exactly 10 digits", "danger")
        return redirect(url_for('register_farmer' if user_type == 'farmer' else 'consumer'))
    if password != confirm_password:
        flash("Passwords do not match", "danger")
        return redirect(url_for('register_farmer' if user_type == 'farmer' else 'consumer'))

    # Add database connection here
    # Implement secure password hashing before saving
    
    flash("Registration successful! Please login.", "success")
    return redirect(url_for('register_farmer' if user_type == 'farmer' else 'consumer'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        phone = request.form.get('phone')
        password = request.form.get('password')

        #Add database connection here
        #Placeholder logic
        if user_type == 'farmer':
            return redirect(url_for('farmer_dashboard'))
        else:
            return redirect(url_for('shop'))
            
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/farmer', methods=['GET', 'POST'])
def farmer():
    if request.method == 'POST':
        name = request.form.get('crop_name')
        price = float(request.form.get('price', 0))
        qty = int(request.form.get('quantity', 0))
        
        new_prod = {
            "_id": str(len(global_products) + 1),
            "name": name,
            "category": "Fresh Produce",
            "price": price,
            "qty": qty,
            "area": request.form.get('area'),
            "description": f"Grown in {request.form.get('area')}",
            "image": "background.png", 
            "status": "available"
        }
        global_products.append(new_prod)
        flash(f"Crop '{name}' added successfully!", "success")
        return redirect(url_for('farmer_dashboard'))

    return render_template('farmerside_login.html')

@app.route('/farmer/dashboard')
def farmer_dashboard():
    return render_template('farmercropstock.html')

@app.route('/consumer')
def consumer():
    return render_template('customerside.html', products=global_products)

@app.route('/shop')
def shop():
    return render_template('shop.html', products=global_products)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = next((p for p in global_products if p["_id"] == product_id), None)
    return render_template('product_detail.html', product=product)

@app.route('/buy/<product_id>', methods=['POST'])
def buy_product(product_id):
    product = next((p for p in global_products if p["_id"] == product_id), None)
    if product and product['qty'] > 0:
        product['qty'] -= 1
        global_orders.append({
            "product_name": product['name'],
            "qty": 1,
            "total_price": product['price'],
            "status": "ordered",
            "created_at": datetime.now()
        })
        flash(f"Bought 1 unit of {product['name']}!", "success")
    else:
        flash("Product not available!", "danger")
    return redirect(url_for('shop'))

@app.route('/orders')
def view_orders():
    return render_template('orders.html', pending_orders=global_orders, successful_orders=[])

@app.route('/complete-order/<order_id>', methods=['POST'])
def complete_order(order_id):
    global global_orders
    global_orders = []
    flash("Order marked as completed!", "success")
    return redirect(url_for('view_orders'))

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    
    session['cart'] = cart
    product = next((p for p in global_products if p["_id"] == product_id), None)
    flash(f"Added {product['name'] if product else 'item'} to cart!", "success")
    return redirect(url_for('shop'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = next((p for p in global_products if p["_id"] == product_id), None)
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'subtotal': item_total
            })
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        flash("Item removed from cart.", "info")
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    # Convert cart to orders
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('shop'))
    
    for product_id, quantity in cart.items():
        product = next((p for p in global_products if p["_id"] == product_id), None)
        if product:
            if product['qty'] >= quantity:
                product['qty'] -= quantity
                global_orders.append({
                    "product_name": product['name'],
                    "qty": quantity,
                    "total_price": product['price'] * quantity,
                    "status": "ordered",
                    "created_at": datetime.now()
                })
            else:
                flash(f"Not enough stock for {product['name']}", "danger")
                return redirect(url_for('view_cart'))
    
    session['cart'] = {}
    flash("Order placed successfully!", "success")
    return redirect(url_for('view_orders'))

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/api/weather')
def weather_api():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "No city provided"}), 400
    
    api_key = "0940f82f8b3d1a696b7afb88cf181c67"
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500
        
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        daily = defaultdict(list)
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            daily[date].append(entry)
            
        forecast = []
        for date, entries in list(daily.items())[:5]: # 5-day forecast
            temps = [e["main"]["temp"] for e in entries]
            desc = entries[0]["weather"][0]["description"]
            icon = entries[0]["weather"][0]["icon"]
            forecast.append({
                "date": date,
                "min": round(min(temps), 1),
                "max": round(max(temps), 1),
                "desc": desc.capitalize(),
                "icon": icon
            })
            
        return jsonify({
            "city": data["city"]["name"],
            "forecast": forecast
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)
    app.run(debug=True)
