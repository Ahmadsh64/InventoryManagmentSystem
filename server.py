
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  # נדרש לניהול session

# ---------- חיבור לבסיס נתונים ----------
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="inventory_system"
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        idnumber = request.form['idnumber']
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE customer_name = %s AND customer_id = %s", (username, idnumber))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            session['user'] = user
            return redirect(url_for('index'))
        else:
            message = "שם המשתמש או תעודת הזהות שגויים, נסה שוב."
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    db = connect_to_database()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory WHERE is_active = 1")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', items=items)

@app.route('/get_item', methods=['POST'])
def get_item():
    data = request.json
    item_name = data.get('item_name')
    if not item_name:
        return jsonify({'error': 'נא להזין שם פריט'}), 400

    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    query = '''
        SELECT i.sku, i.item_name, i.category, i.quantity, i.price, i.color, i.size, i.image_path,
               b.branch_name, b.branch_address
        FROM inventory i
        JOIN branches b ON i.branch_id = b.branch_id
        WHERE i.item_name = %s AND i.is_active = 1
    '''
    cursor.execute(query, (item_name,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()

    if not item:
        return jsonify({'error': 'פריט לא נמצא במלאי'}), 404

    return render_template('cart.html', items=item)

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['total_price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.json
    cart = session.get('cart', [])
    for cart_item in cart:
        if cart_item['sku'] == item['sku']:
            cart_item['quantity'] += item['quantity']
            cart_item['total_price'] = round(cart_item['quantity'] * cart_item['price'], 2)
            break
    else:
        item['total_price'] = round(item['price'] * item['quantity'], 2)
        cart.append(item)
    session['cart'] = cart
    return jsonify({'message': 'הפריט נוסף לעגלה'})

@app.route('/purchase', methods=['POST'])
def purchase():
    cart = session.get('cart', [])
    if not cart or 'user' not in session:
        return jsonify({'error': 'אין עגלה או משתמש מחובר'}), 400

    customer = session['user']
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        for item in cart:
            cursor.execute("""
                INSERT INTO purchases (customer_id, customer_name, sku, item_name, quantity, total_price, purchase_date,
                color, size, branch_name, branch_address, branch_id)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)
            """, (
                customer['customer_id'], customer['customer_name'], item['sku'], item['item_name'],
                item['quantity'], item['total_price'], item['color'], item['size'],
                item.get('branch_name'), item.get('branch_address'), item.get('branch_id')
            ))

            cursor.execute("UPDATE inventory SET quantity = quantity - %s WHERE sku = %s",
                           (item['quantity'], item['sku']))
        conn.commit()
        session['cart'] = []
        return jsonify({'message': 'הרכישה הושלמה בהצלחה!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
