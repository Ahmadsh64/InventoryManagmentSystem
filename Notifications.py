
from tkinter import messagebox
from database import connect_to_database
from inventory import open_update_item_window
from sales import Notification_orders
from ui_utils import create_window_button

def refresh_alerts_only(alerts_label):
    conn = connect_to_database()
    cursor = conn.cursor()

    # עדכון סטטוס זמינות
    cursor.execute("""
        UPDATE inventory
        SET is_active = FALSE
        WHERE quantity = 0 AND is_active = TRUE
    """)

    conn.commit()

    # ספירת פריטים עם חוסר מלאי (מתחת ל-10)
    cursor.execute("""
        SELECT COUNT(*)
        FROM inventory
        WHERE quantity < 10 AND is_active=TRUE
    """)
    alert_count = cursor.fetchone()[0]
    conn.commit()

    cursor.execute("""
    SELECT COUNT(*) 
    FROM (
    SELECT i.sku, i.item_name, b.branch_name, i.quantity, i.received_date, i.is_active,
                   IFNULL(SUM(p.quantity), 0), TIMESTAMPDIFF(MONTH, i.received_date, CURDATE())
            FROM inventory i
            JOIN branches b ON i.branch_id = b.branch_id
            LEFT JOIN purchases p ON i.sku = p.sku AND p.purchase_date >= i.received_date
            GROUP BY i.sku
            HAVING i.quantity > 50 AND i.is_active = TRUE AND SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
    ) AS subquery; 
            """)
    alerts = cursor.fetchone()[0]
    conn.close()

    if alert_count > 0:
        alerts_label.config(text=f"🔴 {alert_count}התראות חוסר מלאי " f"🔴 {alerts} התראות עודף מלאי ")
    else:
        alerts_label.config(text="✔ אין התראות", fg="green")

def open_alerts_window(tree_frame, alerts_label, alerts):
    from datetime import datetime
    import tkinter as tk
    from tkinter import ttk

    for widget in tree_frame.winfo_children():
        widget.destroy()

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
    style.configure("Custom.Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0", foreground="black")
    style.configure("Custom.Treeview", font=("Segoe UI", 10), rowheight=30)
    style.map("Custom.Treeview", background=[("selected", "#d9edf7")])

    # === כפתורי מעבר ===
    switch_frame = tk.Frame(tree_frame, bg="#ffffff")
    switch_frame.pack(fill="x", pady=(5, 10), padx=10)

    create_window_button(switch_frame,"🔴 חוסר מלאי",  command=lambda: show_low_stock_alerts()).pack(side="right", padx=5)
    create_window_button(switch_frame,"🟠 עודף מלאי", command=lambda:  show_overstock_alerts()).pack(side="right", padx=5)
    create_window_button(switch_frame,"🟢 הזמנות לקוחות", command=lambda:  Notification_orders(tree_frame)).pack(side="right", padx=5)

    # === פונקציית חוסר מלאי ===
    def show_low_stock_alerts():
        for widget in tree_frame.winfo_children():
            if widget != switch_frame:
                widget.destroy()

        control_frame = tk.Frame(tree_frame, bg="#f9f9f9", bd=1, relief="solid")
        control_frame.pack(fill="x", padx=10, pady=(0, 10))

        create_window_button(control_frame, text="🔄 רענון", command=show_low_stock_alerts).pack(side="right", padx=10, pady=5)

        selected_item = {}
        tree = ttk.Treeview(tree_frame, columns=("sku", "item", "quantity", "last_updated"), show="headings",
                            style="Custom.Treeview")
        headings = [("sku", "SKU"), ("item", "שם פריט"), ("quantity", "כמות"), ("last_updated", "עודכן לאחרונה")]
        for col, text in headings:
            tree.heading(col, text=text)
            tree.column(col, anchor="center", stretch=True)
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        refresh_low_stock_alerts(tree, selected_item)

        # פעולות נוספות
        action_frame = tk.Frame(tree_frame, bg="#ffffff")
        action_frame.pack(fill="x", padx=10, pady=10)

        create_window_button(action_frame, text="✏️ עדכן פריט",
                   command=lambda: update_selected_item(tree, tree_frame)).pack(side="right", padx=5)
        create_window_button(action_frame, text="🚫 סמן כלא זמין",
                   command=lambda: mark_item_inactive(selected_item)).pack(side="right", padx=5)

        # לחיצה על שורה
        def on_select(event):
            cur_item = tree.focus()
            if cur_item:
                values = tree.item(cur_item)["values"]
                selected_item.update({
                    "sku": values[0],
                    "item_name": values[1],
                    "quantity": values[2],
                    "last_updated": values[3]
                })

        tree.bind("<Double-1>", on_select)

    def refresh_low_stock_alerts(tree=None, selected_item=None):
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("UPDATE inventory SET is_active = FALSE WHERE quantity = 0 AND is_active = TRUE")
        conn.commit()

        cursor.execute("""
            SELECT sku, item_name, quantity, last_updated
            FROM inventory
            WHERE quantity < 10 AND is_active = TRUE
            ORDER BY quantity ASC
        """)
        alerts = cursor.fetchall()
        conn.close()

        if tree:
            for item in tree.get_children():
                tree.delete(item)
            for alert in alerts:
                tree.insert("", "end", values=alert)

        if selected_item is not None:
            selected_item.clear()

    def update_selected_item(tree, tree_frame):
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("שים לב", "בחר פריט לעדכון")
            return

        sku = tree.item(selected)['values'][0]

        # ודא ש-tree_frame נשלח כפרמטר או מוגדר כגלובלי
        try:
            open_update_item_window(tree_frame, sku)
        except NameError:
            messagebox.showerror("שגיאה", "tree_frame לא מוגדר כראוי.")

    def mark_item_inactive(selected_item):
        if not selected_item:
            messagebox.showwarning("אין פריט נבחר", "אנא בחר פריט להפוך ללא זמין.")
            return
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET is_active = FALSE WHERE sku = %s", (selected_item["sku"],))
        conn.commit()
        conn.close()
        messagebox.showinfo("בוצע", "הפריט סומן כלא זמין בהצלחה.")
        show_low_stock_alerts()

    # === פונקציה: הצגת עודף מלאי ===
    # === פונקציית עודף מלאי ===
    def show_overstock_alerts():
        for widget in tree_frame.winfo_children():
            if widget != switch_frame:
                widget.destroy()

        control_frame = tk.Frame(tree_frame, bg="#f9f9f9", bd=1, relief="solid")
        control_frame.pack(fill="x", padx=10, pady=(0, 10))

        create_window_button(control_frame, text="🔄 רענון", command=show_overstock_alerts).pack(side="right", padx=10, pady=5)

        selected_item = {}
        columns = ("sku", "item", "branch", "quantity", "received", "Availability", "purchased", "months")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Custom.Treeview")

        headers = {
            "sku": "SKU",
            "item": "שם פריט",
            "branch": "סניף",
            "quantity": "כמות",
            "received": "התקבל בתאריך",
            "Availability": "זמינות",
            "purchased": "נרכש",
            "months": "חודשים"
        }

        for col in columns:
            tree.heading(col, text=headers[col])
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        refresh_overstock_alerts(tree, selected_item)

        action_frame = tk.Frame(tree_frame, bg="#ffffff")
        action_frame.pack(fill="x", padx=10, pady=10)

        create_window_button(action_frame, text="🏷️ מבצע מחיר",
                   command=lambda: open_discount_item_window(selected_item)).pack(side="right", padx=5)
        create_window_button(action_frame, text="🚚 העבר סניף",
                   command=lambda: open_transfer_item_window(selected_item)).pack(side="right", padx=5)
    def refresh_overstock_alerts(tree=None, selected_item=None):
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT i.sku, i.item_name, b.branch_name, i.quantity, i.received_date, i.is_active,
                   IFNULL(SUM(p.quantity), 0), TIMESTAMPDIFF(MONTH, i.received_date, CURDATE())
            FROM inventory i
            JOIN branches b ON i.branch_id = b.branch_id
            LEFT JOIN purchases p ON i.sku = p.sku AND p.purchase_date >= i.received_date
            GROUP BY i.sku
            HAVING i.quantity > 50 AND i.is_active = TRUE AND SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
        """)
        alerts = cursor.fetchall()
        conn.close()

        if tree:
            for item in tree.get_children():
                tree.delete(item)
            for alert in alerts:
                tree.insert("", "end", values=alert)

        if selected_item is not None:
            selected_item.clear()

    def open_discount_item_window(selected_item):
        if not selected_item:
            messagebox.showwarning("שגיאה", "אין פריט נבחר לעדכון.")
            return

        discount_window = tk.Toplevel()
        discount_window.title("עדכון מחיר למבצע")
        discount_window.geometry("300x200")

        tk.Label(discount_window, text=f"פריט: {selected_item['item_name']}").pack(pady=10)

        tk.Label(discount_window, text="אחוז הנחה (%):").pack()
        discount_entry = ttk.Entry(discount_window)
        discount_entry.pack(pady=5)

        def apply_discount():
            try:
                discount_percent = float(discount_entry.get())
                if not (0 < discount_percent < 100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("שגיאה", "יש להזין מספר בין 1 ל-99.")
                return

            conn = connect_to_database()
            cursor = conn.cursor()

            # מעדכן את אחוז ההנחה והמחיר החדש
            cursor.execute("""
                UPDATE inventory
                SET price = price - (price * %s / 100)
                WHERE sku = %s
            """, (discount_percent, selected_item["sku"]))

            conn.commit()
            conn.close()

            messagebox.showinfo("הצלחה", "המחיר עודכן למבצע בהצלחה.")
            discount_window.destroy()

        create_window_button(discount_window, text="אשר מבצע", command=apply_discount).pack(pady=10)

    def open_transfer_item_window(selected_item):
        if not selected_item:
            messagebox.showwarning("שגיאה", "אין פריט נבחר להעברה.")
            return

        transfer_window = tk.Toplevel()
        transfer_window.title("העברת פריט לסניף אחר")
        transfer_window.geometry("300x250")

        tk.Label(transfer_window, text=f"פריט: {selected_item['item_name']}").pack(pady=10)

        tk.Label(transfer_window, text="בחר סניף יעד:").pack()

        # כאן תמלא את השמות של הסניפים מהרשימה במסד נתונים
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT branch_id, branch_name FROM branches")
        branches = cursor.fetchall()
        conn.close()

        branch_var = tk.StringVar()
        branch_combo = ttk.Combobox(transfer_window, textvariable=branch_var, state="readonly")
        branch_combo["values"] = [f"{branch[0]} - {branch[1]}" for branch in branches]
        branch_combo.pack(pady=5)

        def transfer_item():
            if not branch_var.get():
                messagebox.showerror("שגיאה", "אנא בחר סניף יעד.")
                return

            selected_branch_id = branch_var.get().split(" - ")[0]

            conn = connect_to_database()
            cursor = conn.cursor()

            # מעדכן את הסניף של הפריט
            cursor.execute("""
                UPDATE inventory
                SET branch_id = %s
                WHERE sku = %s
            """, (selected_branch_id, selected_item["sku"]))

            conn.commit()
            conn.close()

            messagebox.showinfo("הצלחה", "הפריט הועבר לסניף החדש בהצלחה.")
            transfer_window.destroy()

        create_window_button(transfer_window, text="אשר העברה", command=transfer_item).pack(pady=10)

    # פתיחה ראשונית על חוסר מלאי
    show_low_stock_alerts()
