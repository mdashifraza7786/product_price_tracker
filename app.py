from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
from db_setup import get_db
from user_model import User
from werkzeug.security import check_password_hash, generate_password_hash
from scraper import scrape_product_details  
import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Bcrypt and LoginManager
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        existing_user = db['users'].find_one({'email': email})

        if existing_user:
            flash('User already exists!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        db['users'].insert_one({
            'email': email,
            'password': hashed_password
        })
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        user_data = db['users'].find_one({"email": email})
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard route (protected)
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    products = db['products'].find({'user_id': current_user.email})
    return render_template('dashboard.html', email=current_user.email, products=products)

# Add a product (Create)
@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    product_url = request.form.get('product_url')
    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()

    # Scrape product details from the URL
    product_details = scrape_product_details(product_url)
    if product_details:
        db['products'].insert_one({
            'email': current_user.email,
            'product_name': product_details['name'],
            'product_url': product_url,
            'product_old_price': product_details['price'],
            'current_price': product_details['price'],
            'last_checked': formatted_date_time 
        })
        flash('Product added successfully!')
    else:
        flash('Failed to add product. Could not scrape details.')

    return redirect(url_for('dashboard'))

# Update a product (Update)
@app.route('/update_product/<product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    product_url = request.form.get('product_url')

    db = get_db()

    product_details = scrape_product_details(product_url)
    if product_details:
        db['products'].update_one(
            {'_id': ObjectId(product_id), 'user_id': current_user.email},
            {'$set': {
                'product_name': product_details['name'],
                'product_url': product_url,
                'product_old_price': product_details['price'],
                'current_price': product_details['price']
            }}
        )
        flash('Product updated successfully!')
    else:
        flash('Failed to update product. Could not scrape updated details.')

    return redirect(url_for('dashboard'))

# Delete a product (Delete)
@app.route('/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    db = get_db()
    db['products'].delete_one({'_id': ObjectId(product_id), 'user_id': current_user.email})
    flash('Product deleted successfully!')
    return redirect(url_for('dashboard'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    user_data = get_db()['users'].find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

if __name__ == '__main__':
    app.run(debug=True)
