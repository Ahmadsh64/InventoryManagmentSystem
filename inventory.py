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
        # שאילתה לשליפת נתונים מהטבלה
        cursor.execute(
            "SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, "
            "branches.branch_id, branches.branch_name, branches.branch_address , inventory.image_path "
            "FROM inventory_system.inventory "
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
            tree.column(col, anchor="center", width=120)

        # הוספת נתונים לשורות
        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #הצגת תמונה של פריט
        image_label = ttk.Label(tree_frame)
        image_label.pack(pady=10)

        def display_item_iamge(event):
            selected_item = tree.selection()
            if selected_item:
                item_data = tree.item(selected_item, "values")
                image_path = item_data[8]
                if image_path and os.path.exists(image_path):
                    image = Image.open(image_path)
                    image = image.resize((150,150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    image_label.config(image=photo)
                    image_label.image= photo
                else:
                    image_label.config(image="")
                    messagebox.showinfo("תמונה", "אין תמונה לפריט זה.")

        tree.bind("<<TreeviewSelect>>", display_item_iamge)

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
                if search_term in row[1].lower():
                    tree.insert("", tk.END, values=row)

        ttk.Button(search_frame, text="חפש", command=filter_inventory).grid(row=0, column=2, padx=5, pady=5)

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

        if not (name and SKU and category and quantity.isdigit() and price.replace('.', '', 1).isdigit() and branch and image_path):
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
                "INSERT INTO inventory (item_name, SKU, category, quantity, price, branch_id, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, SKU, category, int(quantity), float(price), branch , image_filename)
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
        image_path = filedialog.askopenfilename(
            title="בחר תמונה",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if image_path:
            display_image(image_path)
            messagebox.showinfo("תמונה נבחרה", f"תמונה נבחרה: {os.path.basename(image_path)}")

    def display_image(image_file):
        #(thumbnail)הצגת תמונה בגודל קטן
        image = Image.open(image_file)
        image = image.resize((150,150), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        image_label.config(image=photo)
        image_label.image = photo

    def clear_inputs():
        for entry in entries:
            entry.delete(0, tk.END)
        image_label.config(image="")

    add_item_frame = ttk.LabelFrame(tree_frame, text="הוספת פריט חדש")
    add_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    fields = [("שם פריט", "name"), ("SKU", "SKU"), ("קטגוריה", "Category"), ("כמות", "Quantity"), ("מחיר", "Price"),
              ("סניף", "branch")]
    global entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch
    entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch = [ttk.Entry(add_item_frame) for _ in fields]

    entries = [entry_name, entry_SKU, entry_category, entry_quantity, entry_price, entry_branch]

    for i, (label, entry) in enumerate(zip(fields, entries)):
        ttk.Label(add_item_frame, text=label[0]).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")

    #כפתור להעלאת תמונה
    image_path = None
    ttk.Button(add_item_frame, text="בחר תמונה", command=select_image).grid(row=len(fields), column=0, columnspan=2, pady=10)

    #תווית להצגת תמונה
    image_label = ttk.Label(add_item_frame)
    image_label.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

    #כפתור להוספת הפריט
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
        image_path = image_path_var.get()

        if not (name and category and quantity.isdigit() and price.replace('.', '', 1).isdigit() and branch and sku):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE inventory SET item_name=%s, category=%s, quantity=%s, price=%s, branch_id=%s, image_path=%s WHERE SKU=%s",
                (name, category, int(quantity), float(price), branch, image_path,sku)
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

    def load_item_details():
        sku = entry_sku.get()
        if not sku:
            messagebox.showerror("שגיאה", "הזן SKU כדי לטעון פריט")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT item_name, category, quantity, price, branch_id, image_path FROM inventory WHERE SKU=%s",
                (sku,)
            )
            item = cursor.fetchone()
            if item:
                entry_name.delete(0, tk.END)
                entry_category.delete(0, tk.END)
                entry_quantity.delete(0, tk.END)
                entry_price.delete(0, tk.END)
                entry_branch.delete(0, tk.END)

                entry_name.insert(0, item[0])
                entry_category.insert(0, item[1])
                entry_quantity.insert(0, str(item[2]))
                entry_price.insert(0, str(item[3]))
                entry_branch.insert(0, str(item[4]))
                image_path_var.set(item[5])

                if item[5] and os.path.exists(item[5]):
                    display_image(item[5])
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
            image = image.resize((150,150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה: {e}")


    update_item_frame = ttk.LabelFrame(tree_frame, text="פרטי פריט")
    update_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    global entry_sku, entry_name, entry_category, entry_quantity, entry_price, entry_branch, image_label, image_path_var
    entry_sku = ttk.Entry(update_item_frame)
    ttk.Label(update_item_frame, text="SKUשל הפריט הקיים:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_sku.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(update_item_frame, text="טען פריט", command=load_item_details).grid(row=0, column=2, padx=5, pady=5)


    fields = [("שם פריט", "name"), ("קטגוריה", "category"), ("כמות", "quantity"), ("מחיר", "price"), ("סניף", "branch")]
    entry_name, entry_category, entry_quantity, entry_price, entry_branch = [ttk.Entry(update_item_frame) for _ in fields]

    for i, (label, entry) in enumerate(
            zip(fields, [entry_name, entry_category, entry_quantity, entry_price, entry_branch])):
        ttk.Label(update_item_frame, text=label[0]).grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")
        entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")

    image_path_var = tk.StringVar()
    ttk.Label(update_item_frame, text="נתיב תמונה:").grid(row=len(fields) + 1, column=0, padx=5, pady=5, sticky="e")
    ttk.Entry(update_item_frame, textvariable=image_path_var, width=50).grid(row=len(fields) + 1, column=1, padx=5, pady=5, sticky="w")
    ttk.Button(update_item_frame, text="בחר תמונה", command=select_image).grid(row=len(fields) + 1, column=2, padx=5, pady=5)

    image_label = ttk.Label(update_item_frame)
    image_label.grid(row=len(fields) + 2, columnspan=3, pady=10)

    ttk.Button(update_item_frame, text="עדכן פריט", command=update_item).grid(row=len(fields) + 3, columnspan=3, pady=10)


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
                           "branches.branch_id, branches.branch_name, branches.branch_address, inventory.image_path "
                           "FROM inventory_system.inventory "
                           "INNER JOIN inventory_system.branches "
                           "ON inventory.branch_id = branches.branch_id WHERE inventory.sku = %s ",(sku,))
            result = cursor.fetchone()

            tree.delete(*tree.get_children()) #ניקוי התצוגה הקודמת

            if result:
                tree.insert("", tk.END, values=result[:-1]) #ללא נתיב
                display_image(result[-1])
            else:
                messagebox.showinfo("תוצאה", "לא נמצא פריט עם ה-SKU שסיפקת")
                image_label.config(image="")  #הסרת התמונה אם לא נמצא

        except mysql.connector.Error as e:
            messagebox.showinfo("שגיאה", f"שגיאה בעת חיפוש הפריט: {e}")
        finally:
            if connection:
                connection.close()

    def display_image(image_file):
        # הצגת תמונה בגודל קטן (thumbnail)
        image = Image.open(image_file)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        image_label.config(image=photo)
        image_label.image = photo

    # יצירת מסגרת לחיפוש
    form_frame = ttk.LabelFrame(tree_frame, text="חיפוש פריט לפי SKU")
    form_frame.pack(pady=20, padx=20, fill="x")

    ttk.Label(form_frame, text="הזן SKU:").grid(row=0, column=0, padx=5, pady=5)
    entry_sku = ttk.Entry(form_frame)
    entry_sku.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(form_frame, text="חפש פריט", command=search_item).grid(row=0, column=2, padx=5, pady=5)

    # יצירת עץ להצגת הנתונים
    tree = ttk.Treeview(
        tree_frame,
        columns=("SKU", "item_name", "category", "quantity", "price", "branch_id", "branch_name", "branch_address"),
        show="headings"
    )
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    tree.pack(pady=20, fill="both", expand=True)

    #הצגת תמונה של הפריט
    image_label = ttk.Label(tree_frame)
    image_label.pack(pady=10)


def open_purchase_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def purchase_item():
        item_name = entry_item_name.get().strip()
        quantity = entry_quantity.get().strip()
        customer_id = entry_customer_id.get().strip()


        if not (customer_id and item_name and quantity.isdigit()):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות בצורה נכונה")
            return

        quantity = int(quantity)

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # שליפת נתוני הלקוח
            cursor.execute("""
                SELECT customer_name, phone_number, email
                FROM customers
                WHERE customer_name = %s
            """, (customer_id,))
            customer_data = cursor.fetchone()

            if not customer_data:
                messagebox.showerror("שגיאה", "לקוח לא נמצא")
                return

            customer_name, phone_number, email = customer_data

            # שליפת נתוני הפריט כולל התמונה
            cursor.execute("""
                SELECT inventory.sku, inventory.category, inventory.quantity, inventory.price, inventory.branch_id, 
                       branches.branch_name, branches.branch_address, inventory.image_path
                FROM inventory
                INNER JOIN branches ON inventory.branch_id = branches.branch_id
                WHERE inventory.item_name = %s
            """, (item_name,))
            item_data = cursor.fetchone()

            if not item_data:
                messagebox.showerror("שגיאה", "הפריט לא נמצא במלאי")
                return

            sku, category, available_quantity, price, branch_id, branch_name , branch_address, image_path = item_data

            if quantity > available_quantity:
                messagebox.showerror("שגיאה", f"הכמות הזמינה אינה מספיקה. כמות זמינה: {available_quantity}")
                return

            # עדכון מלאי
            new_quantity = available_quantity - quantity
            cursor.execute("UPDATE inventory SET quantity = %s WHERE item_name = %s", (new_quantity, item_name))
            connection.commit()

            # חישוב סכום הרכישה
            total_price = price * quantity

            # שמירת רכישה בטבלת Purchases
            cursor.execute("""
                INSERT INTO Purchases (customer_name, item_name, quantity, total_price, purchase_date, branch_name, branch_address)
                VALUES (%s, %s, %s, %s, NOW(), %s, %s)
            """, (customer_name, item_name, quantity, total_price, branch_name ,branch_address))
            connection.commit()

            messagebox.showinfo("הצלחה", "הרכישה בוצעה בהצלחה")

            # יצירת דוח רכישה
            generate_purchase_report(customer_name, phone_number, email,
                                     sku, item_name, category, quantity, total_price, branch_name, branch_address)

            # ניקוי שדות
            entry_customer_id.delete(0, tk.END)
            entry_item_name.delete(0, tk.END)
            entry_quantity.delete(0, tk.END)

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת ביצוע הרכישה: {e}")
        finally:
            if connection:
                connection.close()

    def generate_purchase_report(customer_name, phone_number, email,
                                 sku, item_name, category, quantity,
                                 total_price, branch_name , branch_address):
        try:
            report_file_name = f"דוח_רכישה_{customer_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

            data = {
                "Customer Name": [customer_name],
                "Phone Number": [phone_number],
                "Email": [email],
                "SKU": [sku],
                "Item Name": [item_name],
                "Category": [category],
                "Quantity": [quantity],
                "Total Price": [total_price],
                "Purchase Date": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                "Branch Name": [branch_name],
                "Branch Address": [branch_address]

            }

            df = pd.DataFrame(data)
            df.to_excel(report_file_name, index=False)

            messagebox.showinfo("הצלחה", f"דוח הרכישה נשמר כ-{report_file_name}")

            # פתיחת הדוח
            if os.name == "posix":
                os.system(f'open "{report_file_name}"')  # macOS/Linux
            else:
                os.system(f'start {report_file_name}')  # Windows

        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בהפקת דוח הרכישה: {e}")

    def display_item_details():
        item_name = entry_item_name.get().strip()
        if not item_name:
            messagebox.showerror("שגיאה", "אנא הזן שם פריט לחיפוש")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT item_name, category, price, image_path 
                FROM inventory
                WHERE item_name = %s
            """, (item_name,))
            item_data = cursor.fetchone()

            if item_data:
                item_name, category, price, image_path = item_data

                item_details_label.config(text=f"שם פריט: {item_name}\nקטגוריה: {category}\nמחיר: {price} ₪")

                if image_path and os.path.exists(image_path):
                    display_image(image_path)
                else:
                    image_label.config(image="")
                    image_label.image = None
            else:
                messagebox.showerror("שגיאה", "הפריט לא נמצא במלאי")

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליפת מידע מהמאגר: {e}")
        finally:
            if connection:
                connection.close()

    def display_image(image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן להציג את התמונה: {e}")

    global entry_customer_id, entry_item_name, entry_quantity, image_label, item_details_label

    purchase_item_frame = ttk.LabelFrame(tree_frame, text="פרטי רכישה")
    purchase_item_frame.pack(padx=90, pady=80, fill="both", expand=True)

    ttk.Label(purchase_item_frame, text="מספר מזהה של לקוח:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_customer_id = ttk.Entry(purchase_item_frame)
    entry_customer_id.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(purchase_item_frame, text="שם פריט:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_item_name = ttk.Entry(purchase_item_frame)
    entry_item_name.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(purchase_item_frame, text="הצג פרטי פריט", command=display_item_details).grid(row=2, columnspan=2, pady=10)
    # תצוגת פרטי הפריט
    item_details_label = ttk.Label(purchase_item_frame, text="", justify=tk.LEFT)
    item_details_label.grid(row=3, columnspan=2, pady=10)
    # תצוגת התמונה
    image_label = ttk.Label(purchase_item_frame)
    image_label.grid(row=4, columnspan=2, pady=10)

    ttk.Label(purchase_item_frame, text="כמות:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
    entry_quantity = ttk.Entry(purchase_item_frame)
    entry_quantity.grid(row=5, column=1, padx=5, pady=5)

    ttk.Button(purchase_item_frame, text="בצע רכישה", command=purchase_item).grid(row=6, columnspan=2, pady=10)

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

            elif report_type == "דוח רכישות":
                cursor.execute(
                    "SELECT p.customer_name, c.phone_number, c.email, p.item_name, p.quantity, p.total_price, p.purchase_date, p.branch_name "
                    "FROM inventory_system.Purchases p "
                    "INNER JOIN inventory_system.Customers c ON p.customer_name = c.customer_name"
                )
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=["Customer Name", "Phone Number", "Email", "Item Name", "Quantity", "Total Price", "Purchase Date", "Branch Name"])
                report_file_name = "דוח_רכישות.xlsx"

            df.to_excel(report_file_name, index=False)
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



def clear_inputs():
    for entry in entries:
        entry.delete(0, tk.END)
entries = []
