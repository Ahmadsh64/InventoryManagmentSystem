import os
import shutil
from datetime import datetime

import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import connect_to_database
from PIL import Image, ImageTk, ImageDraw
from inventory import open_update_item_window
from sales import Notification_orders
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

    # ספירת פריטים עם עודף מלאי (מתחת ל-10)
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
    SELECT i.sku, i.item_name, b.branch_name, i.quantity, i.received_date
    FROM inventory i
    JOIN branches b ON i.branch_id = b.branch_id
    LEFT JOIN purchases p ON i.sku = p.sku AND p.purchase_date >= i.received_date
    GROUP BY i.sku
    HAVING SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
    ) AS subquery; 
            """)
    alerts = cursor.fetchone()[0]
    conn.close()

    if alert_count > 0:
        alerts_label.config(text=f"🔴 {alert_count}התראות חוסר מלאי " f"🔴 {alerts} התראות עודף מלאי ")
    else:
        alerts_label.config(text="✔ אין התראות", fg="green")

def open_alerts_window(tree_frame, alerts_label,alerts):
    from datetime import datetime
    for widget in tree_frame.winfo_children():
        widget.destroy()

    # === מסגרת כפתורי מעבר ===
    switch_frame = tk.Frame(tree_frame)
    switch_frame.pack(fill="x", pady=(0, 10))

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 12), padding=10,bg="",fg="red")
    style.map("TButton",
              background=[("active", "#ececec")],
              foreground=[("active", "#000")])

    btn_low_stock = ttk.Button(switch_frame, text="🔴 חוסר מלאי", style="TButton",
                               command=lambda: show_low_stock_alerts())
    btn_low_stock.pack(side="right", padx=10, ipadx=10)

    btn_overstock = ttk.Button(switch_frame, text="🟠 עודף מלאי", style="TButton",
                               command=lambda: show_overstock_alerts())
    btn_overstock.pack(side="right", padx=10, ipadx=10)
    btn_overstock = ttk.Button(switch_frame, text="🟠 הזמנות לקוחות ", style="TButton",
                               command=lambda: Notification_orders(tree_frame))
    btn_overstock.pack(side="right", padx=10, ipadx=10)


    # === פונקציה: הצגת חוסר מלאי ===
    def show_low_stock_alerts():
        for widget in tree_frame.winfo_children():
            if widget != switch_frame:
                widget.destroy()

        control_frame = tk.Frame(tree_frame, bg="#f8f9fa", bd=2, relief="groove")
        control_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(control_frame, text="🔄 רענן רשימה",command=lambda: show_low_stock_alerts()).pack(side="right", padx=10, pady=5)

        # פקד עזר לשמירת הפריט הנבחר
        selected_item = {}

        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0",
                        foreground="black")
        style.configure("Custom.Treeview", font=("Segoe UI", 11), rowheight=30)
        style.map("Custom.Treeview", background=[("selected", "#cce5ff")])

        tree = ttk.Treeview(tree_frame, columns=("sku", "item", "quantity", "last_updated"), show="headings",
                            style="Custom.Treeview")
        tree.heading("sku", text="sku")
        tree.heading("item", text="שם פריט")
        tree.heading("quantity", text="כמות נוכחית")
        tree.heading("last_updated", text="עודכן לאחרונה")
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        # מילוי הנתונים
        refresh_low_stock_alerts(tree, selected_item)

        # פעולות נוספות
        action_frame = tk.Frame(tree_frame)
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="✏️ עדכן פריט",
                   command=lambda: update_selected_item(tree, tree_frame)).pack(
            side="right", padx=5)

        ttk.Button(action_frame, text="🚫 סמן כלא זמין", command=lambda: mark_item_inactive(selected_item)).pack(
            side="right", padx=5)

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
    def show_overstock_alerts():
        for widget in tree_frame.winfo_children():
            if widget != switch_frame:
                widget.destroy()

        control_frame = tk.Frame(tree_frame)
        control_frame.pack(fill="x", pady=(0, 10))

        selected_item = {}
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0",
                        foreground="black")
        style.configure("Custom.Treeview", font=("Segoe UI", 11), rowheight=30)
        style.map("Custom.Treeview", background=[("selected", "#cce5ff")])
        tree = ttk.Treeview(tree_frame,
                            columns=("sku", "item", "branch", "quantity", "received","Availability", "purchased", "months"),
                            show="headings")
        tree.heading("sku",text="SKU")
        tree.heading("item", text="item_name")
        tree.heading("branch", text="branch")
        tree.heading("quantity", text="quantity")
        tree.heading("received", text="Date_received")
        tree.heading("Availability", text="Availability")
        tree.heading("purchased", text="Purchased")
        tree.heading("months", text="Months")

        tree.pack(fill="both", expand=True, padx=10, pady=5)

        refresh_overstock_alerts(tree, selected_item)

        action_frame = tk.Frame(tree_frame)
        action_frame.pack(fill="x", pady=10)

        ttk.Button(action_frame, text="🏷️ מבצע מחיר", command=lambda: open_discount_item_window(selected_item)).pack(side="right", padx=10)
        ttk.Button(action_frame, text="🚚 העבר סניף", command=lambda: open_transfer_item_window(selected_item)).pack(side="right", padx=10)
        ttk.Button(control_frame, text="🔄 רענן רשימה",command=lambda: show_overstock_alerts()).pack(side="right", padx=10, pady=5)


        def on_select(event):
            cur_item = tree.focus()
            if cur_item:
                values = tree.item(cur_item)["values"]
                selected_item.update({
                    "sku": values[0],
                    "item_name": values[1],
                    "branch": values[2],
                    "quantity": values[3],
                    "received": values[4],
                    "Availability":values[5],
                    "purchased": values[6],
                    "months": values[7]
                })

        tree.bind("<Double-1>", on_select)

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
            HAVING SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
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

        ttk.Button(discount_window, text="אשר מבצע", command=apply_discount).pack(pady=10)

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

        ttk.Button(transfer_window, text="אשר העברה", command=transfer_item).pack(pady=10)

    # פתיחה ראשונית על חוסר מלאי
    show_low_stock_alerts()



