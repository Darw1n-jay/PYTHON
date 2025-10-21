from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize database
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            sale_date DATETIME,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Insert default users if they don't exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                      ('admin', 'admin123', 'admin'))
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                      ('staff', 'staff123', 'staff'))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('staff_dashboard'))
        else:
            flash('Invalid credentials!')
    
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(total_price) FROM sales WHERE DATE(sale_date) = DATE("now")')
    daily_sales = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "staff"')
    staff_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_products=total_products,
                         daily_sales=daily_sales,
                         staff_count=staff_count)

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(total_price) FROM sales WHERE DATE(sale_date) = DATE("now")')
    daily_sales = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return render_template('staff_dashboard.html',
                         total_products=total_products,
                         daily_sales=daily_sales)

@app.route('/manage_products')
def manage_products():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('manage_products.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    name = request.form['name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
                  (name, price, stock))
    conn.commit()
    conn.close()
    
    flash('Product added successfully!')
    return redirect(url_for('manage_products'))

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    flash('Product deleted successfully!')
    return redirect(url_for('manage_products'))

@app.route('/sales_report')
def sales_report():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Get sales statistics
    cursor.execute('SELECT SUM(total_price) FROM sales WHERE DATE(sale_date) = DATE("now")')
    daily_sales = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(total_price) FROM sales WHERE DATE(sale_date) >= DATE("now", "-7 days")')
    weekly_sales = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(total_price) FROM sales WHERE DATE(sale_date) >= DATE("now", "-30 days")')
    monthly_sales = cursor.fetchone()[0] or 0
    
    # Get recent sales
    cursor.execute('''
        SELECT p.name, s.quantity, s.total_price, s.sale_date 
        FROM sales s 
        JOIN products p ON s.product_id = p.id 
        ORDER BY s.sale_date DESC LIMIT 10
    ''')
    recent_sales = cursor.fetchall()
    
    conn.close()
    
    return render_template('sales_report.html',
                         daily_sales=daily_sales,
                         weekly_sales=weekly_sales,
                         monthly_sales=monthly_sales,
                         recent_sales=recent_sales)

@app.route('/record_sale', methods=['GET', 'POST'])
def record_sale():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # Get product details
        cursor.execute('SELECT price, stock FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        
        if product and product[1] >= quantity:
            price = product[0]
            total_price = price * quantity
            
            # Record sale
            cursor.execute('''
                INSERT INTO sales (product_id, quantity, total_price, sale_date) 
                VALUES (?, ?, ?, ?)
            ''', (product_id, quantity, total_price, datetime.now()))
            
            # Update stock
            cursor.execute('UPDATE products SET stock = stock - ? WHERE id = ?',
                          (quantity, product_id))
            
            conn.commit()
            flash('Sale recorded successfully!')
        else:
            flash('Insufficient stock!')
        
        conn.close()
        return redirect(url_for('record_sale'))
    
    # GET request - show form
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE stock > 0')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('record_sale.html', products=products)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
