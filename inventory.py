import os
import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_to_database

def view_inventory(tree_frame):

    for widget in tree_frame.winfo_children():
        widget.destroy()

    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        # שאילתה לשליפת נתונים מהטבלה
        cursor.execute(
            "SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, "
            "branches.branch_id, branches.branch_name, branches.branch_address FROM inventory_system.inventory "
            "INNER JOIN inventory_system.branches "
            "ON inventory.branch_id = branches.branch_id")
        rows = cursor.fetchall()

        # הגדרת Treeview
        tree = ttk.Treeview(
            tree_frame,
            columns=("SKU", "item_name", "category", "quantity", "price", "branch_id", "branch_name", "branch_address"),
            show="headings"
        )
        columns = ["SKU", "item_name", "category", "quantity", "price", "branch_id", "branch_name", "branch_address"]
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        # הוספת נתונים לשורות
        for row in rows:
            tree.insert("", tk.END, values=row)

        search_frame = ttk.LabelFrame(tree_frame, text="חיפוש מלאי")
        search_frame.pack(padx=90, pady=80, fill="both", expand=True)

        ttk.Label(search_frame, text="חפש לפי שם פריט:").grid(row=0, column=0, padx=5, pady=5)
        search_entry = ttk.Entry(search_frame)
        search_entry.grid(row=0, column=1, padx=5, pady=5)

        def filter_inventory():
            search_term = search_entry.get().strip().lower()
            if search_term:
                filtered_rows = [
                    row for row in rows if search_term in str(row[1]).lower()
                ]
                tree.delete(*tree.get_children())
                for row in filtered_rows:
                    tree.insert("", tk.END, values=row)

            else:
                messagebox.showinfo("חיפוש", "אנא הזן מונח לחיפוש")

        ttk.Button(search_frame, text="חפש", command=filter_inventory).grid(row=0, column=2, padx=5, pady=5)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    except mysql.connector.Error as e:
        messagebox.showerror("שגיאה", f"שגיאה בעת שליפת המלאי: {e}")
    finally:
        if connection:
            connection.close()


def open_add_item_window(tree_frame):
    #ניקוי המסך הימני לפני טעינת המסך החדש
    for widget in tree_frame.winfo_children():
        widget.destroy()
    # פונקציה להוספת פריט חדש למלאי
    def add_item():
        name = entry_name.get()
        SKU = entry_SKU.get()
        category = entry_category.get()
        quantity = entry_quantity.get()
        price = entry_price.get()
        branch = entry_branch.get()

        if not (name and SKU and category and quantity.isdigit() and price.replace('.', '', 1).isdigit() and branch):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO inventory (item_name, SKU, category, quantity, price, branch_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, SKU, category, int(quantity), float(price), branch)
            )
            connection.commit()
            messagebox.showinfo("הצלחה", "הפריט נוסף בהצלחה")
            clear_inputs()
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת הוספת הפריט: {e}")
        finally:
            if connection:
                connection.close()

    add_item_frame = ttk.LabelFrame(tree_frame, text="הוספת פריט חדש")
    add_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    fields = [("שם פריט", "name"), ("SKU", "SKU"), ("קטגוריה", "Category"), ("כמות", "Quantity"), ("מחיר", "Price"),
              ("סניף", "branch")]
    global entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch
    entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch = [ttk.Entry(add_item_frame) for _ in fields]
    for i, (label, entry) in enumerate(
            zip(fields, [entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch])):
        ttk.Label(add_item_frame, text=label[0]).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
    ttk.Button(add_item_frame, text="הוסף פריט", command=add_item).grid(row=len(fields), columnspan=2, pady=10)

def open_update_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def update_item():
        name = entry_name.get()
        category = entry_category.get()
        quantity = entry_quantity.get()
        price = entry_price.get()
        branch = entry_branch.get()
        sku = entry_sku.get()

        if not (name and category and quantity.isdigit() and price.replace('.', '', 1).isdigit() and branch and sku):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE inventory SET item_name=%s, category=%s, quantity=%s, price=%s, branch_id=%s WHERE SKU=%s",
                (name, category, int(quantity), float(price), branch, sku)
            )
            connection.commit()
            if cursor.rowcount == 0:
                messagebox.showerror("שגיאה", "לא נמצא פריט עם ה-ID שסיפקת")
            else:
                messagebox.showinfo("הצלחה", "הפריט עודכן בהצלחה")
            clear_inputs()
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת עדכון הפריט: {e}")
        finally:
            if connection:
                connection.close()


    update_item_frame = ttk.LabelFrame(tree_frame, text="פרטי פריט")
    update_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    global entry_sku, entry_name, entry_category, entry_quantity, entry_price, entry_branch
    entry_sku = ttk.Entry(update_item_frame)
    ttk.Label(update_item_frame, text="SKUשל הפריט הקיים:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_sku.grid(row=0, column=1, padx=5, pady=5)

    fields = [("שם פריט", "name"), ("קטגוריה", "category"), ("כמות", "quantity"), ("מחיר", "price"), ("סניף", "branch")]
    entry_name, entry_category, entry_quantity, entry_price, entry_branch = [ttk.Entry(update_item_frame) for _ in fields]

    for i, (label, entry) in enumerate(
            zip(fields, [entry_name, entry_category, entry_quantity, entry_price, entry_branch])):
        ttk.Label(update_item_frame, text=label[0]).grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")
        entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")

    ttk.Button(update_item_frame, text="עדכן פריט", command=update_item).grid(row=len(fields) + 1, columnspan=2, pady=10)
def open_delete_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def delete_item():
        sku = entry_sku.get()

        if not sku:
            messagebox.showerror("שגיאה", "אנא הזן את ה-SKU של הפריט שברצונך למחוק")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("DELETE FROM inventory WHERE SKU = %s", (sku,))
            connection.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("שגיאה", "לא נמצא פריט עם ה-SKU שסיפקת")
            else:
                messagebox.showinfo("הצלחה", "הפריט נמחק בהצלחה")

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת מחיקת הפריט: {e}")
        finally:
            if connection:
                connection.close()

    delete_item_frame = ttk.LabelFrame(tree_frame, text="מחק פריט לפיSKU")
    delete_item_frame.pack(padx=90, pady=80,fill="both", expand=True)

    ttk.Label(delete_item_frame, text="הזן את ה SKU:")
    entry_sku = ttk.Entry(delete_item_frame)
    entry_sku.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ttk.Button(delete_item_frame, text="מחק פריט", command=delete_item).grid(row=1, columnspan=2, pady=10)

def open_search_item_window(tree_frame):

    for widget in tree_frame.winfo_children():
        widget.destroy()

    def search_item():
        sku = entry_sku.get()

        if not sku:
            messagebox.showerror("שגיאה", "אנא הזן SKU לחיפוש")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, "
                           "branches.branch_id, branches.branch_name, branches.branch_address "
                           "FROM inventory_system.inventory "
                           "INNER JOIN inventory_system.branches "
                           "ON inventory.branch_id = branches.branch_id WHERE SKU = %s ",(sku,))
            result = cursor.fetchone()

            tree.delete(*tree.get_children())

            if result:
                tree.insert("", tk.END, values=result)
            else:
                messagebox.showinfo("תוצאה", "לא נמצא פריט עם ה-SKU שסיפקת")

        except mysql.connector.Error as e:
            messagebox.showinfo("שגיאה", f"שגיאה בעת חיפוש הפריט: {e}")
        finally:
            if connection:
                connection.close()

    form_frame = tk.Frame(tree_frame, bg="#f4f4f4")
    form_frame.place(relx=0.5, rely=0.2, anchor="center")

    ttk.Label(form_frame, text="הזן SKU:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_sku = ttk.Entry(form_frame,font=("Arial", 12))
    entry_sku.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ttk.Button(form_frame, text="חפש פריט", command=search_item).grid(row=1, column=0, columnspan=2, pady=10)

    tree = ttk.Treeview(
        tree_frame,
        columns=("SKU", "item_name", "category", "quantity", "price", "branch_id", "branch_name", "branch_address"),
        show="headings"
    )
    columns = ["SKU", "item_name", "category", "quantity", "price", "branch_id", "branch_name", "branch_address"]
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.place(relx=0.5, rely=0.5, anchor="center")

def open_purchase_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def purchase_item():
        item_name = entry_item_name.get().strip()
        quantity = entry_quantity.get().strip()

        if not (item_name and quantity.isdigit()):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return

        quantity = int(quantity)
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            query = "SELECT quantity FROM inventory WHERE item_name = %s"
            cursor.execute(query, (item_name,))
            result = cursor.fetchone()

            if result:
                available_quantity = result[0]
                if quantity > available_quantity:
                    messagebox.showerror("שגיאה", f"הכמות הזמינה אינה מספיקה. כמות זמינה: {available_quantity}")
                else:
                    new_quantity = available_quantity - quantity
                    update_query = "UPDATE inventory SET quantity = %s WHERE item_name = %s"
                    cursor.execute(update_query, (new_quantity, item_name))
                    connection.commit()
                    messagebox.showinfo("הצלחה", "הרכישה בוצעה בהצלחה")

                    entry_item_name.delete(0, tk.END)
                    entry_quantity.delete(0, tk.END)

            else:
                messagebox.showerror("שגיאה", "הפריט לא נמצא במלאי")

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת ביצוע הרכישה: {e}")
        finally:
            if connection:
                connection.close()

    global entry_item_name, entry_quantity

    purchase_item_frame = ttk.LabelFrame(tree_frame, text="פריט רכישה")
    purchase_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    ttk.Label(purchase_item_frame, text="שם פריט:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_item_name = ttk.Entry(purchase_item_frame)
    entry_item_name.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(purchase_item_frame, text="כמות:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_quantity = ttk.Entry(purchase_item_frame)
    entry_quantity.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(purchase_item_frame, text="בצע רכישה", command=purchase_item).grid(row=2, columnspan=2, pady=10)

    purchase_item_frame.place(relx=0.5, rely=0.5, anchor="center")

def open_report_window(tree_frame):

    for widget in tree_frame.winfo_children():
        widget.destroy()

    def generate_report():
        report_type = report_combobox.get()
        if not report_type:
            messagebox.showerror("שגיאה", "אנא בחר סוג דוח")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            if report_type == "דוח מלאי":
                cursor.execute(
                    "SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, "
                    "branches.branch_name, branches.branch_address "
                    "FROM inventory_system.inventory "
                    "INNER JOIN inventory_system.branches ON inventory.branch_id = branches.branch_id"
                )
                rows = cursor.fetchall()

                df = pd.DataFrame(rows, columns=["SKU", "item_name", "category", "quantity", "price", "branch_name", "branch_address"])
                global report_file_name
                report_file_name = "דוח_מלאי.xlsx"
                df.to_excel(report_file_name, index=False)

                messagebox.showinfo("הצלחה", f"הדוח נוצר ונשמר כ-{report_file_name}")

                show_report_Button.config(state=tk.NORMAL)

            elif report_type == "דוח מכירות":
                messagebox.showinfo("מידע", "דוח מכירות עדיין לא זמין במערכת")
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת יצירת הדוח: {e}")
        finally:
            if connection:
                connection.close()

    def show_report():
        if report_file_name and os.path.exists(report_file_name):
            os.system(f'open "{report_file_name}"' if os.name == "posix" else f'start {report_file_name}')
        else:
            messagebox.showerror("שגיאה", "הדוח הזה לא נמצא")

    report_window_frame = tk.LabelFrame(tree_frame, text="בחר סוג דוח")
    report_window_frame.pack(padx=10, pady=10)

    ttk.Label(report_window_frame, text="סוג דוח:").grid(row=0, column=0, padx=5, pady=5)
    report_combobox = ttk.Combobox(report_window_frame, values=["דוח מלאי", "דוח מכירות"], state="readonly")
    report_combobox.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(report_window_frame, text="צור דוח", command=generate_report).grid(row=1, column=0, columnspan=2, pady=10)

    show_report_Button = ttk.Button(tree_frame, text="הצג דוח", command=show_report, state=tk.DISABLED)
    show_report_Button.pack(pady=5)


def clear_inputs():
    for entry in entries:
        entry.delete(0, tk.END)
entries = []
