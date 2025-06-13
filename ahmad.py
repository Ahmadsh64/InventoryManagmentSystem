from flask import Flask, jsonify, request
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

    cursor.execute("""
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
            i.image_path
        FROM order_notifications n
        JOIN purchases p ON n.order_id = p.purchase_id
        JOIN order_items o ON n.order_id = o.order_id
        LEFT JOIN inventory i ON o.sku = i.sku
        WHERE n.is_read = 1
        ORDER BY n.created_at DESC
    """)

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
@app.route('/api/mark_item_taken', methods=['POST'])
def mark_item_taken():
    data = request.json
    order_id = data.get("order_id")
    sku = data.get("sku")

    if not order_id or not sku:
        return jsonify({"error": "חסרים נתונים"}), 400

    conn = connect_to_database()
    if not conn:
        return jsonify({"error": "אין חיבור למסד הנתונים"}), 500
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE order_items SET item_status = 'נלקח'
            WHERE order_id = %s AND sku = %s
        """, (order_id, sku))
        conn.commit()
        return jsonify({"message": "הפריט סומן כנלקח"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/order/<int:order_id>/complete_fulfillment", methods=["POST"])
def complete_order_fulfillment(order_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    # בודק שכל הפריטים נאספו
    cursor.execute("""
        SELECT COUNT(*) FROM order_items
        WHERE order_id = %s AND item_status != 'נלקח'
    """, (order_id,))
    not_ready_count = cursor.fetchone()[0]

    if not_ready_count > 0:
        conn.close()
        return jsonify({"status": "error", "message": "לא כל הפריטים נאספו"}), 400

    # עדכון סטטוס ההזמנה
    cursor.execute("""
        UPDATE order_items SET item_status = 'סיום המכלה'
            WHERE order_id = %s 
    """, (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "fulfilled"})

if __name__ == "__main__":
    app.run(debug=True)
