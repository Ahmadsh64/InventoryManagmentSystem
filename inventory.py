import os
import shutil
from datetime import datetime

import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import connect_to_database
from PIL import Image, ImageTk


def view_inventory(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # שאילתה לשליפת כל הנתונים כולל השדות החדשים
        cursor.execute(
            """SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, 
                      inventory.color, inventory.size, inventory.shelf_row, inventory.shelf_column,
                      branches.branch_id, branches.branch_name, branches.branch_address, inventory.image_path
               FROM inventory_system.inventory
               INNER JOIN inventory_system.branches 
               ON inventory.branch_id = branches.branch_id"""
        )
        rows = cursor.fetchall()

        # הגדרת Treeview כולל השדות החדשים
        tree = ttk.Treeview(
            tree_frame,
            columns=("SKU", "item_name", "category", "quantity", "price", "color", "size", "shelf_row", "shelf_column",
                     "branch_id", "branch_name", "branch_address"),
            show="headings"
        )

        # רשימת העמודות כולל השדות החדשים
        columns = ["SKU", "item_name", "category", "quantity", "price", "color", "size", "shelf_row", "shelf_column",
                   "branch_id", "branch_name", "branch_address"]

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        # הוספת נתונים לטבלה
        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # הצגת תמונה של פריט
        image_label = ttk.Label(tree_frame)
        image_label.pack(pady=10)

        def display_item_image(event):
            selected_item = tree.selection()
            if selected_item:
                item_data = tree.item(selected_item, "values")
                image_path = item_data[-1]  # image_path נמצא בעמודה האחרונה בשאילתה
                if image_path and os.path.exists(image_path):
                    image = Image.open(image_path)
                    image = image.resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    image_label.config(image=photo)
                    image_label.image = photo
                else:
                    image_label.config(image="")
                    messagebox.showinfo("תמונה", "אין תמונה לפריט זה.")

        tree.bind("<<TreeviewSelect>>", display_item_image)

        # מסגרת חיפוש
        search_frame = ttk.LabelFrame(tree_frame, text="חיפוש מלאי")
        search_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(search_frame, text="חפש לפי שם פריט:").grid(row=0, column=0, padx=5, pady=5)
        search_entry = ttk.Entry(search_frame)
        search_entry.grid(row=0, column=1, padx=5, pady=5)

        def filter_inventory():
            search_term = search_entry.get().strip().lower()
            tree.delete(*tree.get_children())
            for row in rows:
                if search_term in row[1].lower():  # חיפוש לפי שם פריט
                    tree.insert("", tk.END, values=row)

        ttk.Button(search_frame, text="חפש", command=filter_inventory).grid(row=0, column=2, padx=5, pady=5)

    except mysql.connector.Error as e:
        messagebox.showerror("שגיאה", f"שגיאה בעת שליפת המלאי: {e}")
    finally:
        if connection:
            connection.close()



def open_add_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def add_item():
        name = entry_name.get()
        SKU = entry_SKU.get()
        category = entry_category.get()
        quantity = entry_quantity.get()
        price = entry_price.get()
        branch = entry_branch.get()
        color = entry_color.get()
        size = entry_size.get()
        shelf_row = entry_shelf_row.get()
        shelf_column = entry_shelf_column.get()

        if not (name and SKU and category and quantity.isdigit() and price.replace('.', '', 1).isdigit() and branch and
                color and size and shelf_row.isdigit() and shelf_column.isdigit() and image_path):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            if not os.path.exists("images"):
                os.makedirs("images")

            image_filename = os.path.join("images", os.path.basename(image_path))
            shutil.copy(image_path, image_filename)

            cursor.execute(
                """INSERT INTO inventory (item_name, SKU, category, quantity, price, branch_id, color, size, shelf_row, shelf_column, image_path) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (name, SKU, category, int(quantity), float(price), branch, color, size, int(shelf_row), int(shelf_column), image_filename)
            )
            connection.commit()

            messagebox.showinfo("הצלחה", "הפריט נוסף בהצלחה")
            clear_inputs()

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת הוספת הפריט: {e}")

        finally:
            if connection:
                connection.close()

    def select_image():
        nonlocal image_path
        image_path = filedialog.askopenfilename(title="בחר תמונה", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if image_path:
            display_image(image_path)
            messagebox.showinfo("תמונה נבחרה", f"תמונה נבחרה: {os.path.basename(image_path)}")

    def display_image(image_file):
        image = Image.open(image_file)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo

    def clear_inputs():
        for entry in entries:
            entry.delete(0, tk.END)
        image_label.config(image="")

    add_item_frame = ttk.LabelFrame(tree_frame, text="הוספת פריט חדש")
    add_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    fields = [
        ("שם פריט", "name"), ("SKU", "SKU"), ("קטגוריה", "category"), ("כמות", "quantity"),
        ("מחיר", "price"), ("סניף", "branch"), ("צבע", "color"), ("מידה", "size"),
        ("שורת מדף", "shelf_row"), ("עמודת מדף", "shelf_column")
    ]

    global entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch, entry_color, entry_size, entry_shelf_row, entry_shelf_column
    entries = [ttk.Entry(add_item_frame) for _ in fields]
    (entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch,
     entry_color, entry_size, entry_shelf_row, entry_shelf_column) = entries

    for i, (label, entry) in enumerate(zip(fields, entries)):
        ttk.Label(add_item_frame, text=label[0]).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")

    image_path = None
    ttk.Button(add_item_frame, text="בחר תמונה", command=select_image).grid(row=len(fields), column=0, columnspan=2, pady=10)

    image_label = ttk.Label(add_item_frame)
    image_label.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

    ttk.Button(add_item_frame, text="הוסף פריט", command=add_item).grid(row=len(fields) + 2, column=0, columnspan=2, pady=10)

    add_item_frame.place(relx=0.5, rely=0.5, anchor="center")


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
        color = entry_color.get()
        size = entry_size.get()
        shelf_row = entry_shelf_row.get()
        shelf_column = entry_shelf_column.get()
        image_path = image_path_var.get()

        if not (name and category and quantity.isdigit() and price.replace('.', '', 1).isdigit() and branch and sku):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # עדכון פריט כולל השדות החדשים
            cursor.execute(
                """UPDATE inventory SET item_name=%s, category=%s, quantity=%s, price=%s, branch_id=%s, 
                           color=%s, size=%s, shelf_row=%s, shelf_column=%s, image_path=%s WHERE SKU=%s""",
                (name, category, int(quantity), float(price), branch, color, size, shelf_row, shelf_column, image_path,
                 sku)
            )
            connection.commit()
            if cursor.rowcount == 0:
                messagebox.showerror("שגיאה", "לא נמצא פריט עם ה-SKU שסיפקת")
            else:
                messagebox.showinfo("הצלחה", "הפריט עודכן בהצלחה")
                clear_inputs()
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת עדכון הפריט: {e}")
        finally:
            if connection:
                connection.close()

    def load_item_details():
        sku = entry_sku.get()
        if not sku:
            messagebox.showerror("שגיאה", "הזן SKU כדי לטעון פריט")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(
                """SELECT item_name, category, quantity, price, branch_id, color, size, shelf_row, shelf_column, image_path 
                   FROM inventory WHERE SKU=%s""",
                (sku,)
            )
            item = cursor.fetchone()
            if item:
                entry_name.delete(0, tk.END)
                entry_category.delete(0, tk.END)
                entry_quantity.delete(0, tk.END)
                entry_price.delete(0, tk.END)
                entry_branch.delete(0, tk.END)
                entry_color.delete(0, tk.END)
                entry_size.delete(0, tk.END)
                entry_shelf_row.delete(0, tk.END)
                entry_shelf_column.delete(0, tk.END)

                entry_name.insert(0, item[0])
                entry_category.insert(0, item[1])
                entry_quantity.insert(0, str(item[2]))
                entry_price.insert(0, str(item[3]))
                entry_branch.insert(0, item[4])
                entry_color.insert(0, item[5])
                entry_size.insert(0, item[6])
                entry_shelf_row.insert(0, str(item[7]))
                entry_shelf_column.insert(0, str(item[8]))
                image_path_var.set(item[9])

                if item[9] and os.path.exists(item[9]):
                    display_image(item[9])
                else:
                    image_label.config(image="")
                    image_label.image = None

            else:
                messagebox.showerror("שגיאה", "פריט לא נמצא")
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת פריט: {e}")
        finally:
            if connection:
                connection.close()

    def select_image():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            image_path_var.set(file_path)
            display_image(file_path)

    def display_image(image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה: {e}")

    update_item_frame = ttk.LabelFrame(tree_frame, text="עדכון פריט")
    update_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    global entry_sku, entry_name, entry_category, entry_quantity, entry_price, entry_branch, entry_color, entry_size, entry_shelf_row, entry_shelf_column
    global image_label, image_path_var

    entry_sku = ttk.Entry(update_item_frame)
    ttk.Label(update_item_frame, text="SKU של הפריט הקיים:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_sku.grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(update_item_frame, text="טען פריט", command=load_item_details).grid(row=0, column=2, padx=5, pady=5)

    fields = [("שם פריט", "name"), ("קטגוריה", "category"), ("כמות", "quantity"), ("מחיר", "price"), ("סניף", "branch"),
              ("צבע", "color"), ("מידה", "size"), ("שורת מדף", "shelf_row"), ("עמודת מדף", "shelf_column")]

    entry_name, entry_category, entry_quantity, entry_price, entry_branch, entry_color, entry_size, entry_shelf_row, entry_shelf_column = \
        [ttk.Entry(update_item_frame) for _ in fields]

    for i, (label, entry) in enumerate(
            zip(fields, [entry_name, entry_category, entry_quantity, entry_price, entry_branch,
                         entry_color, entry_size, entry_shelf_row, entry_shelf_column])):
        ttk.Label(update_item_frame, text=label[0]).grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")
        entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")

    # שדה בחירת תמונה
    image_path_var = tk.StringVar()
    ttk.Label(update_item_frame, text="נתיב תמונה:").grid(row=len(fields) + 1, column=0, padx=5, pady=5, sticky="e")
    ttk.Entry(update_item_frame, textvariable=image_path_var, width=50).grid(row=len(fields) + 1, column=1, padx=5,
                                                                             pady=5, sticky="w")
    ttk.Button(update_item_frame, text="בחר תמונה", command=select_image).grid(row=len(fields) + 1, column=2, padx=5,
                                                                               pady=5)

    # תצוגת תמונה
    image_label = ttk.Label(update_item_frame)
    image_label.grid(row=len(fields) + 2, columnspan=3, pady=10)

    ttk.Button(update_item_frame, text="עדכן פריט", command=update_item).grid(row=len(fields) + 3, columnspan=3,
                                                                              pady=10)


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
        sku = entry_sku.get().strip()
        if not sku:
            messagebox.showerror("שגיאה", "אנא הזן SKU לחיפוש")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, 
                       inventory.price, inventory.color, inventory.size, inventory.shelf_row, inventory.shelf_column, 
                       branches.branch_id, branches.branch_name, branches.branch_address, inventory.image_path
                FROM inventory
                INNER JOIN branches ON inventory.branch_id = branches.branch_id 
                WHERE inventory.sku = %s
            """, (sku,))
            result = cursor.fetchone()

            tree.delete(*tree.get_children())  # ניקוי התצוגה הקודמת

            if result:
                tree.insert("", tk.END, values=result[:-1])  # הכנסת הנתונים ללא נתיב התמונה
                display_image(result[-1])  # הצגת התמונה אם קיימת
            else:
                messagebox.showinfo("תוצאה", "לא נמצא פריט עם ה-SKU שסיפקת")
                image_label.config(image="")  # הסרת התמונה אם לא נמצא

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת חיפוש הפריט: {e}")
        finally:
            if connection:
                connection.close()

    def display_image(image_file):
        try:
            if image_file and os.path.exists(image_file):
                image = Image.open(image_file)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                image_label.config(image=photo)
                image_label.image = photo
            else:
                image_label.config(image="")  # אם אין תמונה, לא להציג כלום
                image_label.image = None
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה: {e}")

    # יצירת מסגרת לחיפוש
    form_frame = ttk.LabelFrame(tree_frame, text="חיפוש פריט לפי SKU")
    form_frame.pack(pady=20, padx=20, fill="x")

    ttk.Label(form_frame, text="הזן SKU:").grid(row=0, column=0, padx=5, pady=5)
    entry_sku = ttk.Entry(form_frame)
    entry_sku.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(form_frame, text="חפש", command=search_item).grid(row=0, column=2, padx=5, pady=5)

    # יצירת עץ להצגת הנתונים כולל השדות החדשים
    columns = (
    "SKU", "שם פריט", "קטגוריה", "כמות", "מחיר", "צבע", "מידה", "שורת מדף", "עמודת מדף", "ID סניף", "שם סניף",
    "כתובת סניף")

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.pack(pady=20, fill="both", expand=True)

    # הצגת תמונה של הפריט
    image_label = ttk.Label(tree_frame)
    image_label.pack(pady=10)


def open_purchase_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    cart = []
    total_amount = tk.DoubleVar(value=0.0)

    def connect_and_get_item(item_name):
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT sku, category, quantity, price, color, size, image_path,
                       branches.branch_name, branches.branch_address
                FROM inventory
                INNER JOIN branches ON inventory.branch_id = branches.branch_id
                WHERE item_name = %s
            """, (item_name,))
            item_data = cursor.fetchone()
            connection.close()
            return item_data
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליפת פריט: {e}")
            return None

    def display_image(image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo
        except Exception as e:
            image_label.config(image="")
            image_label.image = None
            messagebox.showerror("שגיאה", f"שגיאה בטעינת תמונה: {e}")

    def display_item_details():
        item_name = entry_item_name.get().strip()
        if not item_name:
            messagebox.showerror("שגיאה", "אנא הזן שם פריט")
            return

        item_data = connect_and_get_item(item_name)
        if item_data:
            sku, category, quantity, price, color, size, image_path, _, _ = item_data
            item_details_label.config(text=f"שם פריט: {item_name}\n"
                                           f"קטגוריה: {category}\n"
                                           f"מחיר: ₪{price}\n"
                                           f"צבע: {color}\n"
                                           f"מידה: {size}\n"
                                           f"זמינות: {quantity}")
            if image_path and os.path.exists(image_path):
                display_image(image_path)
            else:
                image_label.config(image="")
                image_label.image = None
        else:
            item_details_label.config(text="")
            image_label.config(image="")
            image_label.image = None

    def add_to_cart():
        item_name = entry_item_name.get().strip()
        quantity = entry_quantity.get().strip()

        if not (item_name and quantity.isdigit()):
            messagebox.showerror("שגיאה", "אנא הזן שם פריט וכמות תקינה")
            return

        quantity = int(quantity)
        item_data = connect_and_get_item(item_name)

        if not item_data:
            return

        sku, category, available_quantity, price, color, size, image_path, branch_name, branch_address = item_data

        if quantity > available_quantity:
            messagebox.showerror("שגיאה", f"כמות זמינה: {available_quantity}")
            return

        total_price = price * quantity

        cart.append({
            "item_name": item_name,
            "sku": sku,
            "category": category,
            "quantity": quantity,
            "price": price,
            "total_price": total_price,
            "color": color,
            "size": size,
            "branch_name": branch_name,
            "branch_address": branch_address
        })

        total_amount.set(sum(item["total_price"] for item in cart))
        update_cart_display()
        entry_item_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        item_details_label.config(text="")
        image_label.config(image="")
        image_label.image = None

    def update_cart_display():
        cart_listbox.delete(0, tk.END)
        for item in cart:
            cart_listbox.insert(tk.END, f"{item['item_name']} × {item['quantity']} — ₪{item['total_price']:.2f}")
        total_label.config(text=f"סה\"כ לתשלום: ₪{total_amount.get():.2f}")

    def complete_purchase():
        customer_id = entry_customer_id.get().strip()
        if not customer_id or not cart:
            messagebox.showerror("שגיאה", "יש להזין מזהה לקוח ולבחור פריטים")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT customer_id, customer_name, phone_number, email
                FROM customers
                WHERE customer_id = %s
            """, (customer_id,))
            customer_data = cursor.fetchone()

            if not customer_data:
                messagebox.showerror("שגיאה", "הלקוח לא נמצא")
                return

            customer_id, customer_name, phone_number, email = customer_data

            for item in cart:
                cursor.execute("UPDATE inventory SET quantity = quantity - %s WHERE sku = %s",
                               (item["quantity"], item["sku"]))

                cursor.execute("""
                    INSERT INTO purchases (customer_id, customer_name, sku, item_name, quantity, total_price, purchase_date,
                                           color, size, branch_name, branch_address)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
                """, (customer_id, customer_name, item["sku"], item["item_name"], item["quantity"],
                      item["total_price"], item["color"], item["size"], item["branch_name"], item["branch_address"]))

            connection.commit()
            messagebox.showinfo("הצלחה", "הרכישה בוצעה בהצלחה")

            generate_purchase_report(customer_name, phone_number, email, cart)

            cart.clear()
            total_amount.set(0)
            update_cart_display()

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בביצוע הרכישה: {e}")
        finally:
            if connection:
                connection.close()

    def generate_purchase_report(customer_name, phone_number, email, cart):
        try:
            report_file_name = f"דוח_רכישה_{customer_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"

            data = []
            for item in cart:
                data.append({
                    "Customer Name": customer_name,
                    "Phone Number": phone_number,
                    "Email": email,
                    "SKU": item['sku'],
                    "Item Name": item['item_name'],
                    "Category": item['category'],
                    "Quantity": item['quantity'],
                    "Color": item['color'],
                    "Size": item['size'],
                    "Total Price": item['total_price'],
                    "Purchase Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Branch Name": item['branch_name'],
                    "Branch Address": item['branch_address']
                })

            df = pd.DataFrame(data)
            df.to_excel(report_file_name, index=False)

            messagebox.showinfo("הצלחה", f"דוח הרכישה נשמר כ-{report_file_name}")
            os.system(f'open "{report_file_name}"' if os.name == "posix" else f'start {report_file_name}')

        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בהפקת דוח: {e}")

    # --- UI --- #
    global entry_customer_id, entry_item_name, entry_quantity, image_label, item_details_label

    left_frame = ttk.Frame(tree_frame)
    left_frame.pack(side=tk.LEFT, padx=20, pady=20, fill="both", expand=True)

    ttk.Label(left_frame, text="מספר מזהה של לקוח:").pack(anchor="w")
    entry_customer_id = ttk.Entry(left_frame)
    entry_customer_id.pack(fill="x", pady=5)

    ttk.Label(left_frame, text="שם פריט:").pack(anchor="w")
    entry_item_name = ttk.Entry(left_frame)
    entry_item_name.pack(fill="x", pady=5)

    ttk.Label(left_frame, text="כמות:").pack(anchor="w")
    entry_quantity = ttk.Entry(left_frame)
    entry_quantity.pack(fill="x", pady=5)

    ttk.Button(left_frame, text="הצג פרטי פריט", command=display_item_details).pack(pady=5)
    item_details_label = ttk.Label(left_frame, text="", justify="left")
    item_details_label.pack(pady=5)
    image_label = ttk.Label(left_frame)
    image_label.pack(pady=5)

    ttk.Button(left_frame, text="הוסף לעגלה", command=add_to_cart).pack(pady=10)
    ttk.Button(left_frame, text="סיים רכישה", command=complete_purchase).pack()

    right_frame = ttk.LabelFrame(tree_frame, text="עגלה")
    right_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill="y")

    cart_listbox = tk.Listbox(right_frame, width=40)
    cart_listbox.pack(padx=10, pady=10)

    total_label = ttk.Label(right_frame, text="סה\"כ לתשלום: ₪0.00")
    total_label.pack(pady=5)


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
                cursor.execute("""
                    SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, inventory.color, 
                           inventory.size, inventory.shelf_row, inventory.shelf_column, branches.branch_name, branches.branch_address, 
                           inventory.last_updated 
                    FROM inventory_system.inventory 
                    INNER JOIN inventory_system.branches ON inventory.branch_id = branches.branch_id
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "SKU", "item_name", "category", "quantity", "price", "color", "size",
                    "shelf_row", "shelf_column", "branch_name", "branch_address", "last_updated"
                ])

                global report_file_name
                report_file_name = "דוח_מלאי.xlsx"

                # יצירת קובץ Excel עם גרף
                # יצירת קובץ Excel עם גרף
                with pd.ExcelWriter(report_file_name, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
                    df.to_excel(writer, index=False, sheet_name='מלאי')
                    workbook = writer.book
                    worksheet = writer.sheets['מלאי']

                    # הפיכת עמודת תאריך לעמודת טקסט/תאריך
                    df['last_updated'] = pd.to_datetime(df['last_updated'])

                    # הוספת גרף מסוג עמודות – תאריך מול כמות
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name': 'כמות לפי תאריך',
                        'categories': f'=מלאי!L$2:$L${len(df) + 1}',  # last_updated
                        'values': f'=מלאי!$D$2:$D${len(df) + 1}',  # quantity
                    })
                    chart.set_title({'name': 'גרף כמות לפי תאריך עדכון'})
                    chart.set_x_axis({'name': 'תאריך עדכון'})
                    chart.set_y_axis({'name': 'כמות'})

                    worksheet.insert_chart('N2', chart)


            elif report_type == "דוח רכישות":
                cursor.execute("""
                    SELECT p.customer_id, p.customer_name, c.phone_number, c.email, p.item_name, p.quantity, 
                           p.total_price, p.purchase_date, p.color, p.size, p.branch_name 
                    FROM inventory_system.Purchases p 
                    INNER JOIN inventory_system.Customers c ON p.customer_name = c.customer_name
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "Customer ID", "Customer Name", "Phone Number", "Email", "Item Name",
                    "Quantity", "Total Price", "Purchase Date", "Color", "Size", "Branch Name"
                ])

                report_file_name = "דוח_רכישות.xlsx"
                # המרת תאריך
                df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])

                # שמירת דוח + גרף
                with pd.ExcelWriter(report_file_name, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
                    df.to_excel(writer, index=False, sheet_name='רכישות')
                    workbook = writer.book
                    worksheet = writer.sheets['רכישות']

                    # גרף עמודות לפי תאריך רכישה מול כמות
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name': 'כמות רכישות לפי תאריך',
                        'categories': f'=רכישות!H$2:H${len(df) + 1}',  # Purchase Date
                        'values': f'=רכישות!F$2:F${len(df) + 1}',  # Quantity
                    })

                    chart.set_title({'name': 'כמות רכישות לפי תאריך'})
                    chart.set_x_axis({'name': 'תאריך רכישה'})
                    chart.set_y_axis({'name': 'כמות'})

                    worksheet.insert_chart('L2', chart)

            messagebox.showinfo("הצלחה", f"הדוח נוצר ונשמר כ-{report_file_name}")
            show_report_Button.config(state=tk.NORMAL)

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
    report_combobox = ttk.Combobox(report_window_frame, values=["דוח מלאי", "דוח רכישות"], state="readonly")
    report_combobox.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(report_window_frame, text="צור דוח", command=generate_report).grid(row=1, column=0, columnspan=2, pady=10)

    show_report_Button = ttk.Button(tree_frame, text="הצג דוח", command=show_report, state=tk.DISABLED)
    show_report_Button.pack(pady=5)

def open_alerts_window(tree_frame, alerts_label, main_window):
    for widget in tree_frame.winfo_children():
        widget.destroy()

        # ראש עמודת ההתראות + כפתור עדכון
    top_frame = tk.Frame(tree_frame)
    top_frame.pack(fill="x", pady=(0, 10))

    last_alert_count = {"count": 0}  # עוקב אחרי מספר ההתראות הקודם

    alert_frames = {}  # מיפוי בין סניף למסגרת התצוגה שלו
    alert_trees = {}   # מיפוי בין סניף ל-TreeView שלו

    ttk.Button(top_frame, text="עדכן עכשיו", command=lambda: open_update_item_window(tree_frame)).pack(side="right",
                                                                                                       padx=10)
    ttk.Button(top_frame, text="רענון", command=lambda: refresh_alerts).pack(side="right",
                                                                                                       padx=10)
    def refresh_alerts():
        # ניקוי כל מסגרות הסניפים
        for frame in alert_frames.values():
            frame.destroy()
        alert_frames.clear()
        alert_trees.clear()

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT i.sku, i.branch_id, b.branch_name, b.branch_address, 
                       i.item_name, i.quantity, i.last_updated
                FROM inventory i
                JOIN branches b ON i.branch_id = b.branch_id
                WHERE i.quantity < 10
                ORDER BY i.branch_id
            """)
        alerts = cursor.fetchall()
        conn.close()

        branch_alerts = {}
        for sku, branch_id, branch_name, branch_address, item_name, quantity, last_updated in alerts:
            if branch_id not in branch_alerts:
                branch_alerts[branch_id] = {
                    "name": branch_name,
                    "address": branch_address,
                    "items": []
                }
            branch_alerts[branch_id]["items"].append((sku, item_name, quantity, last_updated))

        total_count = 0
        for i, (branch_id, data) in enumerate(branch_alerts.items()):
            name = data["name"]
            address = data["address"]
            items = data["items"]

            # כותרת עם מספר סניף + שם + כתובת
            branch_frame = ttk.LabelFrame(
                tree_frame,
                text=f"סניף מספר {branch_id} - {name} ({address})",
                padding=10
            )
            branch_frame.pack(fill="both", expand=True, pady=5)
            alert_frames[branch_id] = branch_frame

            tree = ttk.Treeview(branch_frame, columns=("sku", "item", "quantity", "last_updated"), show="headings")
            tree.heading("sku", text="sku")
            tree.heading("item", text="שם פריט")
            tree.heading("quantity", text="כמות נוכחית")
            tree.heading("last_updated", text="עודכן לאחרונה")
            tree.pack(fill="both", expand=True)

            for item in items:
                tree.insert("", "end", values=item)

            alert_trees[branch_id] = tree
            total_count += len(items)

        # הצגת פופ-אפ אם נוספו התראות חדשות
        if total_count > last_alert_count["count"]:
            messagebox.showinfo("התראות חדשות", f"⚠️ נוספו {total_count - last_alert_count['count']} התראות חדשות!")

        last_alert_count["count"] = total_count

        # עדכון תווית
        if total_count > 0:
            alerts_label.config(text=f"🔴 {total_count} התראות", fg="red")
        else:
            alerts_label.config(text="✔ אין התראות", fg="green")

    refresh_alerts()


def clear_inputs():
    for entry in entries:
        entry.delete(0, tk.END)
entries = []
