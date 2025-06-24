import hashlib
import os
from datetime import datetime

from flask import Flask, jsonify, request, session, render_template, flash, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="inventory_system"
        )
        return conn
    except Error as e:
        print(f"Error connecting to DB: {e}")
        return None

@app.route("/api/notifications", methods=["GET"])
def get_unread_notifications():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    branch_name = request.args.get("branch_name")
    status = request.args.get("status")
    date = request.args.get("date")
    search = request.args.get("search")

    query = """
        SELECT 
            n.notification_id,
            n.order_id,
            n.created_at,
            p.customer_name,
            o.item_status,
            o.sku,
            o.item_name,
            o.quantity,
            o.color,
            o.size,
            i.image_path,
            p.branch_name
        FROM order_notifications n
        JOIN purchases p ON n.order_id = p.purchase_id
        JOIN order_items o ON n.order_id = o.order_id
        LEFT JOIN inventory i ON o.sku = i.sku
    """

    filters = []
    values = []

    if branch_name:
        filters.append("p.branch_name = %s")
        values.append(branch_name)

    if status:
        filters.append("o.item_status = %s")
        values.append(status)

    if date:
        filters.append("DATE(n.created_at) = %s")
        values.append(date)

    if search:
        filters.append("(p.customer_name LIKE %s OR n.order_id LIKE %s)")
        values.append(f"%{search}%")
        values.append(f"%{search}%")

    if filters:
        query += " AND " + " AND ".join(filters)

    query += " ORDER BY n.created_at DESC"

    cursor.execute(query, values)
    notifications = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notifications)

# === שליפת מפת מחסן כולל מיקום פריטים של הזמנה ===
@app.route('/api/warehouse_map_with_order/<int:order_id>', methods=['GET'])
def warehouse_map_with_order(order_id):
    conn = connect_to_database()
    if not conn:
        return jsonify({"error": "אין חיבור למסד הנתונים"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT o.sku,o.item_name, i.shelf_row, i.shelf_column, i.shelf_zone, i.image_path
            FROM order_items o
            JOIN inventory i ON o.sku = i.sku
            WHERE o.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        return jsonify({"items": items})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
# === שליפת פריטים לפי אזור מדף ===
@app.route('/api/inventory_by_zone/<zone>', methods=['GET'])
def inventory_by_zone(zone):
    conn = connect_to_database()
    if not conn:
        return jsonify({"error": "אין חיבור למסד הנתונים"}), 500
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT sku, item_name, shelf_zone, shelf_row, shelf_column, quantity
            FROM inventory
            WHERE shelf_zone = %s AND is_active = 1
        """, (zone,))
        results = cursor.fetchall()
        return jsonify({"inventory": results})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/order/<int:order_id>", methods=["GET"])
def get_order_details(order_id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT o.sku, o.order_item_id, o.order_id, o.item_name, o.color,
    o.quantity,o.size, o.item_status ,i.image_path
            FROM order_items o
            JOIN inventory i ON o.sku = i.sku
            WHERE o.order_id = %s
                """, (order_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(items)

@app.route("/api/notifications/<int:notification_id>/mark_read", methods=["POST"])
def mark_notification_as_read(notification_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE order_notifications SET is_read = 1 WHERE notification_id = %s
    """, (notification_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/api/order/<int:order_item_id>/start_fulfillment", methods=["POST"])
def start_item_fulfillment(order_item_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE order_items SET item_status = 'התחלת מכלה' 
        WHERE order_id = %s 
    """, (order_item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "started"})

@app.route("/api/item_location/<string:sku>", methods=["GET"])
def get_item_location(sku):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT shelf_zone, shelf_row, shelf_column
        FROM inventory
        WHERE sku = %s
        LIMIT 1
    """, (sku,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(item if item else {})

# === סימון פריט כנלקח במחסן ===
@app.route("/api/mark_item_taken", methods=["POST"])
def mark_item_taken():
    data = request.get_json()
    order_id = data.get("order_id")
    sku = data.get("sku")
    employee_id = data.get("employee_id")  # נוסף

    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE order_items
        SET item_status = 'נלקח',
            fulfilled_at = NOW(),
            processed_by_employee_id = %s
        WHERE order_id = %s AND sku = %s
    """, (employee_id, order_id, sku))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"})


@app.route("/api/order/<int:order_id>/complete_fulfillment", methods=["POST"])
def complete_order_fulfillment(order_id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    # בדיקה אם יש פריטים שלא נאספו
    cursor.execute("""
        SELECT COUNT(*) AS not_taken FROM order_items
        WHERE order_id = %s AND item_status != 'נלקח'
    """, (order_id,))
    if cursor.fetchone()["not_taken"] > 0:
        conn.close()
        return jsonify({"status": "error", "message": "לא כל הפריטים נאספו"}), 400

    # שליפת פריטי ההזמנה כולל פרטי לקוח וסניף
    cursor.execute("""
        SELECT oi.*, i.price, i.branch_id, i.color, i.size,
               b.branch_name, b.branch_address,
               c.customer_id, c.customer_name
        FROM order_items oi
        JOIN inventory i ON oi.sku = i.sku
        JOIN branches b ON i.branch_id = b.branch_id
        JOIN customers c ON c.customer_id = (
            SELECT customer_id FROM purchases
            WHERE order_id = %s LIMIT 1
        )
        WHERE oi.order_id = %s
    """, (order_id, order_id))
    items = cursor.fetchall()

    # הוספת רשומות לטבלת purchases ועדכון מלאי
    for item in items:
        total_price = item["price"] * item["quantity"]

        # הוספה ל-purchases
        cursor.execute("""
            INSERT INTO purchases (
                customer_id, customer_name, sku, item_name, quantity, total_price,
                purchase_date, color, size, branch_name, branch_address, branch_id, order_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s)
        """, (
            item["customer_id"], item["customer_name"], item["sku"], item["item_name"],
            item["quantity"], total_price, item["color"], item["size"],
            item["branch_name"], item["branch_address"], item["branch_id"], 'הושלם'
        ))

        # עדכון המלאי
        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity - %s, last_update = NOW()
            WHERE sku = %s
        """, (item["quantity"], item["sku"]))

    # עדכון סטטוס כל פריטי ההזמנה
    cursor.execute("""
        UPDATE order_items
        SET item_status = 'סיום המכלה'
        WHERE order_id = %s
    """, (order_id,))

    # עדכון ההתראה - סומן כנקרא והוספת שדה זמן סיום
    cursor.execute("""
        UPDATE order_notifications
        SET is_read = 1,
            created_at = created_at,  -- שמירה על השדה המקורי
            completed_at = NOW()      -- תוספת חדשה שנרחיב עליה מטה
        WHERE order_id = %s
    """, (order_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "fulfilled"})


@app.route("/api/purchases")
def get_purchases():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM purchases
        ORDER BY purchase_date DESC
    """)
    purchases = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({"purchases": purchases})

@app.route("/api/branches")
def get_branches():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT branch_id, branch_name FROM branches")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"branches": branches})

@app.before_request
def ensure_favorites_session():
    if 'favorites' not in session:
        session['favorites'] = []

app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
def hash_password(password):
    # פונקציה פשוטה להצפנת סיסמה (SHA256)
    return hashlib.sha256(password.encode()).hexdigest()

# דף הבית - שליפת מלאי, סניפים וקטגוריות
@app.route('/', methods=['GET'])
def index():
    branch_id = request.args.get('branch_id')
    category = request.args.get('category')

    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    # שליפת סניפים
    cursor.execute("SELECT branch_id, branch_name FROM branches")
    branches = cursor.fetchall()

    # שליפת קטגוריות ייחודיות
    cursor.execute("SELECT DISTINCT category FROM inventory WHERE is_active=1")
    categories = [row['category'] for row in cursor.fetchall()]

    # בניית שאילתא עם סינון
    query = """
        SELECT i.sku, i.item_name, i.category, i.quantity, i.price, i.color, i.size,
               i.image_path, b.branch_name
        FROM inventory i
        LEFT JOIN branches b ON i.branch_id = b.branch_id
        WHERE i.is_active = 1
    """
    params = []
    if branch_id:
        query += " AND i.branch_id = %s"
        params.append(branch_id)
    if category:
        query += " AND i.category = %s"
        params.append(category)

    cursor.execute(query, params)
    inventory = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('index.html',
                           customer_name=session.get('customer_name', 'לקוח יקר'),
                           email=session.get('email', ''),
                           phone=session.get('phone', ''),
                           inventory=inventory,
                           branches=branches,
                           categories=categories,
                           selected_branch=int(branch_id) if branch_id else None,
                           selected_category=category)

# הוספה לעגלה
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'customer_id' not in session:
        flash("עליך להתחבר לפני ביצוע רכישה")
        return redirect(url_for('login'))

    sku = request.form.get('sku')
    color = request.form.get('color')
    size = request.form.get('size')
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            raise ValueError()
    except ValueError:
        flash("כמות לא תקינה")
        return redirect(url_for('index'))

    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT quantity, item_name, price, branch_id FROM inventory WHERE sku=%s AND color=%s AND size=%s AND is_active=1", (sku, color, size))
    item = cursor.fetchone()
    cursor.close()
    conn.close()

    if not item:
        flash("הפריט לא נמצא או לא זמין במידה/צבע שבחרת")
        return redirect(url_for('index'))

    if quantity > item['quantity']:
        flash(f"לא קיימת כמות מספקת במלאי. כמות זמינה: {item['quantity']}")
        return redirect(url_for('index'))

    cart = session.get('cart', [])

    # אם הפריט כבר בעגלה, נוסיף כמות אחרת
    for cart_item in cart:
        if cart_item['sku'] == sku and cart_item['color'] == color and cart_item['size'] == size:
            cart_item['quantity'] += quantity
            break
    else:
        cart.append({
            'sku': sku,
            'item_name': item['item_name'],
            'color': color,
            'size': size,
            'quantity': quantity,
            'price': float(item['price']),
            'branch_id': item['branch_id']
        })

    session['cart'] = cart
    flash(f"הפריט נוסף לעגלה בהצלחה")
    return redirect(request.referrer or url_for('index'))

# הסרת פריט מהעגלה
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    sku = request.form.get('sku')
    color = request.form.get('color')
    size = request.form.get('size')

    cart = session.get('cart', [])
    new_cart = [item for item in cart if not (item['sku'] == sku and item['color'] == color and item['size'] == size)]
    session['cart'] = new_cart

    flash("הפריט הוסר מהעגלה בהצלחה")
    return redirect(url_for('cart'))

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    sku = request.form.get('sku')
    color = request.form.get('color')
    size = request.form.get('size')

    favorites = session.get('favorites', [])

    # בדיקה אם הפריט כבר במועדפים
    exists = False
    for item in favorites:
        if item['sku'] == sku and item['color'] == color and item['size'] == size:
            exists = True
            favorites.remove(item)
            break
    if not exists:
        favorites.append({'sku': sku, 'color': color, 'size': size})

    session['favorites'] = favorites
    flash("עודכן במועדפים")
    return redirect(request.referrer or url_for('index'))

# הצגת עגלת הקניות
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)


# ביצוע רכישה
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'customer_id' not in session:
        flash("עליך להתחבר לפני ביצוע רכישה")
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if not cart:
        flash("עגלה ריקה")
        return redirect(url_for('index'))

    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # שליפת כל הסניפים מראש
        cursor.execute("SELECT branch_id, branch_name, branch_address FROM branches")
        branches = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        purchase_date = datetime.now()
        total_order_price = sum(item['price'] * item['quantity'] for item in cart)

        # נשתמש בפריט הראשון כדי לדעת את הסניף
        first_item = cart[0]
        branch_name, branch_address = branches.get(first_item['branch_id'], ('', ''))

        cursor.execute("""
            INSERT INTO purchases (
                customer_id, customer_name, sku, item_name, quantity, total_price,
                purchase_date, color, size, branch_name, branch_address, branch_id, order_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'הזמנה מהירה')
        """, (
            session['customer_id'],
            session.get('customer_name'),
            first_item['sku'],
            first_item['item_name'],
            sum(item['quantity'] for item in cart),
            total_order_price,
            purchase_date,
            first_item['color'],
            first_item['size'],
            branch_name,
            branch_address,
            first_item['branch_id']
        ))

        order_id = cursor.lastrowid

        # הכנסת פריטים לטבלת order_items
        for item in cart:
            cursor.execute("""
                INSERT INTO order_items (order_id, sku, item_name, quantity, color, size, item_status)
                VALUES (%s, %s, %s, %s, %s, %s, 'ממתין')
            """, (
                order_id,
                item['sku'],
                item['item_name'],
                item['quantity'],
                item['color'],
                item['size']
            ))

            # עדכון המלאי
            cursor.execute("""
                UPDATE inventory
                SET quantity = quantity - %s
                WHERE sku = %s AND color = %s AND size = %s
            """, (item['quantity'], item['sku'], item['color'], item['size']))

        # הוספת התראה חדשה
        cursor.execute("""
            INSERT INTO order_notifications (order_id, is_read, created_at)
            VALUES (%s, FALSE, NOW())
        """, (order_id,))

        conn.commit()
        session['cart'] = []
        flash("הרכישה בוצעה בהצלחה!")

    except Exception as e:
        conn.rollback()
        flash(f"שגיאה בהרכישה: {e}")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = hash_password(password)

        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user.get('password_hash') == hashed_pw:
            session['customer_id'] = user['customer_id']
            session['customer_name'] = user['customer_name']
            flash("התחברת בהצלחה!", "success")
            return redirect(url_for('index'))
        else:
            flash("אימייל או סיסמה שגויים", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("הסיסמאות אינן תואמות", "error")
            return render_template('register.html')

        hashed_pw = hash_password(password)

        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("אימייל כבר רשום במערכת", "error")
            cursor.close()
            conn.close()
            return render_template('register.html')

        cursor.execute("""
            INSERT INTO customers (customer_name, phone_number, email, password_hash) 
            VALUES (%s, %s, %s, %s)
        """, (name, phone, email, hashed_pw))
        conn.commit()
        cursor.close()
        conn.close()
        flash("נרשמת בהצלחה! אנא התחבר/י", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        # כאן אפשר להוסיף לוגיקה לשליחת מייל עם קישור איפוס
        flash(f'בקשת איפוס סיסמה נשלחה לכתובת {email} (מדומה)', "info")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("התנתקת מהמערכת", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
