import os
import shutil
from datetime import datetime
import mysql.connector
import pandas as pd
from tkinter import ttk, messagebox, filedialog
from database import connect_to_database
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk, messagebox

# פונקציה לעדכון מפת המחסן לפי סניף
def update_warehouse_map(parent_frame, branch_id, select_shelf, item_sku=None):
    # ניקוי המדפים הקודמים
    for widget in parent_frame.winfo_children():
        widget.destroy()

    shelf_rows, shelf_cols = 9, 9
    occupied_slots = set()  # סט המיקומים תפוסים
    selected_shelf = None  # משתנה לזיהוי מדף הפריט

    try:
        # שליפת המדפים תפוסים מתוך מסד הנתונים לפי branch_id
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("""
             SELECT shelf_row, shelf_column FROM inventory
             WHERE branch_id = %s
         """, (branch_id,))
        occupied_slots = set((r, c) for r, c in cur.fetchall())

        # אם הוזן SKU של פריט, נסה לשלוף את המיקום שלו
        if item_sku:
            cur.execute("""
                SELECT shelf_row, shelf_column FROM inventory
                WHERE branch_id = %s AND SKU = %s
            """, (branch_id, item_sku))
            selected_shelf = cur.fetchone()

        conn.close()
    except Exception as e:
        messagebox.showerror("שגיאה", f"שגיאה בטעינת המדפים: {e}")
        return

    # יצירת רשת המדפים
    for r in range(1, shelf_rows + 1):
        for c in range(1, shelf_cols + 1):
            status = (r, c) in occupied_slots  # האם המדף תפוס
            color = "#e74c3c" if status else "#2ecc71"  # אדום = תפוס, ירוק = פנוי

            # אם יש מיקום ספציפי לפריט, סמן אותו בצבע שונה
            if selected_shelf and (r, c) == selected_shelf:
                color = "#f39c12"  # צבע צהוב לפריט שנמצא במיקום הזה

            btn = tk.Button(
                parent_frame, text=f"{r},{c}", width=4, height=2,
                bg=color, fg="white", relief="raised",
                state="disabled" if status else "normal",  # לא ניתן לבחור אם תפוס
                command=lambda row=r, col=c: select_shelf(row, col)
            )
            btn.grid(row=r, column=c, padx=1, pady=1)

def view_inventory(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, 
                   inventory.color, inventory.size, inventory.shelf_row, inventory.shelf_column,
                   branches.branch_id, branches.branch_name, branches.branch_address, inventory.image_path
            FROM inventory_system.inventory
            INNER JOIN inventory_system.branches 
            ON inventory.branch_id = branches.branch_id
        """)
        rows = cursor.fetchall()

        # ===== מסגרת ראשית =====
        main_frame = tk.Frame(tree_frame, bg="#f4f6f7")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== מסגרת חיפוש =====
        search_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        search_frame.pack(fill="x", pady=(0, 10))

        title_label = tk.Label(
            search_frame, text="Inventory Search 🔍",
            font=("Segoe UI", 24, "bold"), bg="#ffffff", fg="#2f3640"
        )
        title_label.grid(row=0, column=0, columnspan=10, pady=20)

        # שדות חיפוש
        fields = [
            ("Item Name:", 1, 0),
            ("Branch:", 1, 2),
            ("Category:", 1, 4),
            ("Color:", 1, 6)
        ]

        entries = {}

        for text, r, c in fields:
            label = tk.Label(search_frame, text=text, font=("Segoe UI", 16), bg="#ffffff")
            label.grid(row=r, column=c, padx=10, pady=10, sticky="w")

            if text == "Branch:":
                branch_names = list(set([row[11] for row in rows]))
                branch_names.sort()
                branch_names.insert(0, "")
                entry = ttk.Combobox(search_frame, values=branch_names, font=("Segoe UI", 14), state="readonly")
                entry.current(0)
            else:
                entry = tk.Entry(search_frame, font=("Segoe UI", 14))

            entry.grid(row=r, column=c + 1, padx=10, pady=10, sticky="ew")
            entries[text] = entry

        search_frame.grid_columnconfigure((1, 3, 5, 7), weight=1)

        # ===== פונקציות סינון ורענון =====
        def filter_inventory_advanced():
            name = entries["Item Name:"].get().strip().lower()
            branch = entries["Branch:"].get().strip().lower()
            category = entries["Category:"].get().strip().lower()
            color = entries["Color:"].get().strip().lower()

            tree.delete(*tree.get_children())
            for row in rows:
                if (not name or name in row[1].lower()) and \
                   (not category or category in row[2].lower()) and \
                   (not color or color in row[5].lower()) and \
                   (not branch or branch in row[11].lower()):
                    tree.insert("", tk.END, values=row)

        def reset_inventory():
            for entry in entries.values():
                if isinstance(entry, ttk.Combobox):
                    entry.set("")
                else:
                    entry.delete(0, tk.END)
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", tk.END, values=row)

        # ===== כפתורי חיפוש =====
        button_frame = tk.Frame(search_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=10, pady=10)

        search_button = tk.Button(button_frame, text="Search", command=filter_inventory_advanced,
                                  font=("Segoe UI", 16, "bold"), bg="#3498db", fg="white",
                                  activebackground="#2980b9", relief="flat", padx=20, pady=5)
        search_button.pack(side="left", padx=10)

        refresh_button = tk.Button(button_frame, text="Reset", command=reset_inventory,
                                   font=("Segoe UI", 16, "bold"), bg="#95a5a6", fg="white",
                                   activebackground="#7f8c8d", relief="flat", padx=20, pady=5)
        refresh_button.pack(side="left", padx=10)

        # ===== טבלת תוצאות =====
        table_frame = tk.Frame(main_frame, bg="#f4f6f7")
        table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background="#ffffff",
                        foreground="#2c3e50",
                        fieldbackground="#ffffff",
                        rowheight=35,
                        font=("Segoe UI", 11))
        style.configure("Custom.Treeview.Heading",
                        background="#34495e",
                        foreground="white",
                        font=("Segoe UI", 18, "bold"))
        style.map("Custom.Treeview", background=[("selected", "#d0ebff")])

        tree = ttk.Treeview(table_frame,
                            columns=("SKU", "item_name", "category", "quantity", "price", "color", "size", "shelf_row", "shelf_column",
                                     "branch_id", "branch_name", "branch_address"),
                            show="headings",
                            style="Custom.Treeview")

        columns = ["SKU", "item_name", "category", "quantity", "price", "color", "size", "shelf_row", "shelf_column",
                   "branch_id", "branch_name", "branch_address"]

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== הצגת תמונה =====
        def display_item_image(event):
            selected_item = tree.selection()
            if selected_item:
                item_data = tree.item(selected_item, "values")
                image_path = item_data[-1]
                if image_path and os.path.exists(image_path):
                    try:
                        image = Image.open(image_path)
                        image = image.resize((180, 180), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        image_label.config(image=photo)
                        image_label.image = photo
                    except Exception:
                        image_label.config(image="")
                else:
                    image_label.config(image="")

        tree.bind("<<TreeviewSelect>>", display_item_image)

        image_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        image_frame.pack(fill="x", pady=10)

        image_label = tk.Label(image_frame, bg="#ffffff")
        image_label.pack(pady=15)

    except mysql.connector.Error as e:
        messagebox.showerror("שגיאה", f"שגיאה בעת שליפת המלאי: {e}")
    finally:
        if connection:
            connection.close()

def open_add_item_window(tree_frame):
    # ניקוי המסגרת הקודמת
    for widget in tree_frame.winfo_children():
        widget.destroy()

    # שליפת סניפים מתוך DB
    try:
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("SELECT branch_id, branch_name FROM branches")
        branch_data = cur.fetchall()
        conn.close()
    except Exception as e:
        messagebox.showerror("שגיאה", f"לא ניתן לטעון סניפים: {e}")
        branch_data = []

    branch_dict = {name: bid for bid, name in branch_data}
    branch_names = [""] + sorted(branch_dict.keys())


     # פונקציה לבחירת מיקום מדף
    def select_shelf(row, col):
        entries["shelf_row"].delete(0, tk.END)
        entries["shelf_row"].insert(0, str(row))
        entries["shelf_column"].delete(0, tk.END)
        entries["shelf_column"].insert(0, str(col))

    def refresh_map():
        branch_name = entries["branch"].get()
        branch_id = branch_dict.get(branch_name, -1)
        if branch_id != -1:
            update_warehouse_map(warehouse_frame, branch_id, select_shelf)

    # פונקציות עזר
    image_path = {"val": None}  # משתמש במילון כדי לעדכן מתוך nested

    def display_image(image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo

            def zoom_image():
                top = tk.Toplevel()
                top.title("תצוגת תמונה")
                big_img = Image.open(image_path)
                big_photo = ImageTk.PhotoImage(big_img)
                label = tk.Label(top, image=big_photo)
                label.image = big_photo
                label.pack()

            image_label.bind("<Button-1>", lambda e: zoom_image())

        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה: {e}")

    def select_image():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            image_path_var.set(file_path)
            image_path["val"] = image_path_var  # תעדכן גם את המילון
            display_image(file_path)

    def clear_inputs():
        for w in entries.values():
            if isinstance(w, ttk.Entry):
                w.delete(0, tk.END)
            elif isinstance(w, ttk.Combobox):
                w.set("")
        image_label.config(image="")
        image_label.image = None
        image_path["val"] = None

    def add_item():
        # קריאת ערכים
        name     = entries["name"].get().strip()
        sku      = entries["SKU"].get().strip()
        category = entries["category"].get().strip()
        qty      = entries["quantity"].get().strip()
        price    = entries["price"].get().strip()
        branch_n = entries["branch"].get().strip()
        color    = entries["color"].get().strip()
        size     = entries["size"].get().strip()
        row      = entries["shelf_row"].get().strip()
        col      = entries["shelf_column"].get().strip()
        img_p    = image_path["val"].get()

        # ולידציה
        if not (name and sku and category and qty.isdigit()
                and price.replace('.', '', 1).isdigit()
                and branch_n in branch_dict
                and color and size and row.isdigit() and col.isdigit()
                and img_p):
            messagebox.showerror("שגיאה", "אנא מלא/י את השדות כראוי כולל תמונה")
            return

        # שמירת תמונה בתיקיה המקומית
        os.makedirs("images", exist_ok=True)
        img_p = os.path.join("images", os.path.basename(img_p))
        dest_path = os.path.join("images", os.path.basename(img_p))
        shutil.copy(image_path["val"].get(), dest_path)

        # הוספה למסד
        try:
            conn = connect_to_database()
            cur  = conn.cursor()
            cur.execute(
                """INSERT INTO inventory
                   (item_name, SKU, category, quantity, price, branch_id, color, size, shelf_row, shelf_column, image_path)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    name, sku, category, int(qty), float(price),
                    branch_dict[branch_n], color, size,
                    int(row), int(col), img_p
                )
            )
            conn.commit()
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן להוסיף פריט: {e}")
            return
        finally:
            conn.close()

        # תעודת קבלה מעוצבת
        receipt = tk.Toplevel()
        receipt.title("🧾 תעודת קבלת סחורה")
        receipt.configure(bg="#ffffff")
        txt = (
            f"🧾 תעודת קבלה\n\n"
            f"פריט: {name}\n"
            f"SKU: {sku}\n"
            f"כמות: {qty}\n"
            f"מחיר יחידה: ₪{price}\n"
            f"סניף: {branch_n}\n"
            f"תאריך: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        tk.Label(
            receipt, text=txt,
            font=("Segoe UI", 13), justify="right",
            bg="#ffffff", fg="#333"
        ).pack(padx=40, pady=30)

        messagebox.showinfo("הצלחה", "הפריט נוסף בהצלחה!")

    # שדות ומילון תואם
    labels = {
        "SKU": "SKU 🔎",
        "name": "שם פריט ✏️",
        "category": "קטגוריה 🏷️",
        "quantity": "כמות 📦",
        "price": "מחיר 💲",
        "branch": "סניף 🏬",
        "color": "צבע 🎨",
        "size": "מידה 📏",
        "shelf_row": "שורה במדף 🛒",
        "shelf_column": "טור במדף 🛒",
        "val" : "נתיב תמונה 📷"
    }

    entries = {}


    add_frame = tk.Frame(tree_frame, bg="#ffffff", width=1000, height=1000)
    add_frame.pack(fill="both", expand=True, padx=2, pady=2)
    add_frame.pack_propagate(0)  # חשוב כדי למנוע שינוי אוטומטי של הגודל

    for idx, (key, label_text) in enumerate(labels.items()):
        tk.Label(add_frame, text=label_text, bg="#ffffff", anchor="w", font=("Segoe UI", 16)) \
            .grid(row=idx + 1, column=0, padx=15, pady=15, sticky="w")

        if key == "branch":
            entry = ttk.Combobox(add_frame, values=branch_names, width=28, state="readonly")
            entry.bind("<<ComboboxSelected>>", lambda e: refresh_map())
        else:
            entry = ttk.Entry(add_frame, width=30)

        entry.grid(row=idx + 1, column=1, padx=15, pady=15, sticky="w")
        entries[key] = entry

    # כפתור בחירת תמונה + תצוגה
    # כותרת
    tk.Label(
        add_frame, text="🆕 הוספת פריט חדש", font = ("Segoe UI", 25, "bold"),bg = "#ffffff",
        fg = "#2f3640").grid(row=0, column=2, columnspan=4, pady=5, sticky="e")

    # --- תצוגת מפת מחסן ---
    warehouse_frame = tk.Frame(add_frame, bg="#ffffff")
    warehouse_frame.grid(row=2, column=8, rowspan=12, padx=(40, 0), sticky="e")

    # כותרת מפת המחסן
    tk.Label(
        add_frame, text="📦 מפת המחסן", font=("Segoe UI", 25, "bold"),
        bg="#ffffff", fg="#2f3640"
    ).grid(row=1, column=8, columnspan=4, pady=5, sticky="e")

    image_path_var = tk.StringVar()
    image_entry = ttk.Entry(add_frame, textvariable=image_path_var, width=30)
    image_entry.grid(row=11, column=1, padx=10, pady=10, sticky="w")


    image_label = tk.Label(add_frame, bg="#ffffff")
    image_label.grid(row=2, column=2, rowspan=4, padx=10, pady=10)

    # כפתורים
    tk.Button(add_frame, text="בחר תמונה 📷", command=select_image,
              bg="#3498db", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=11, column=2, padx=10, pady=10)


    tk.Button(add_frame, text="add ✔️", command=add_item,
              bg="#27ae60", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=12, column=2, padx=10, pady=10)

    # כפתור רענון מפת המחסן
    btn_refresh = tk.Button(
        add_frame, text="🔄 טען מדפים",
        bg="#3498db", fg="white", font=("Segoe UI", 16), relief="flat",
        command= refresh_map)
    btn_refresh.grid(row=12, column=3, padx=10, pady=10)

    tk.Button(add_frame, text="נקה 🧹", command=clear_inputs,
              bg="#e67e22", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=12, column=4, padx=10, pady=10)

def open_update_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def update_item():
        name = entry_name.get()
        category = entry_category.get()
        quantity = entry_quantity.get()
        add_quantity = entry_add_quantity.get()
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

            # אם הוזנה כמות להוספה
            add_qty = int(add_quantity) if add_quantity and add_quantity.isdigit() else 0
            new_quantity = int(quantity) + add_qty

            # עדכון הפריט עם כמות חדשה
            cursor.execute(
                """UPDATE inventory SET item_name=%s, category=%s, quantity=%s, price=%s, branch_id=%s, 
                   color=%s, size=%s, shelf_row=%s, shelf_column=%s, image_path=%s WHERE SKU=%s""",
                (name, category, new_quantity, float(price), branch, color, size, shelf_row, shelf_column, image_path,
                 sku)
            )

            # רישום הוצאה רק אם נוספה כמות
            if add_qty > 0:
                total_cost = add_qty * float(price)
                cursor.execute(""" 
                        INSERT INTO expenses (branch_id, sku, item_name, quantity_added, unit_price, total_cost)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (branch, sku, name, add_qty, float(price), total_cost))

            connection.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("שגיאה", "לא נמצא פריט עם ה-SKU שסיפקת")
            else:
                messagebox.showinfo("הצלחה", "הפריט עודכן בהצלחה")

                popup = tk.Toplevel()
                popup.title("תעודת קבלת סחורה")
                popup.configure(bg="#ffffff")
                total_cost = price * add_qty

                fields = [
                    ("שם פריט:", name),
                    ("SKU:", sku),
                    ("כמות נוספת:", add_qty),
                    ("מחיר ליחידה:", f"₪{price}"),
                    ("סכום כולל:", f"₪{total_cost}"),
                    ("סניף:", branch),
                    ("תאריך:", datetime.now().strftime('%Y-%m-%d %H:%M'))
                ]

                for i, (label, value) in enumerate(fields):
                    ttk.Label(popup, text=label, font=("Arial", 11, "bold")).grid(row=i, column=0, sticky="e", padx=10,
                                                                                  pady=5)
                    ttk.Label(popup, text=value, font=("Arial", 11)).grid(row=i, column=1, sticky="w", padx=10, pady=5)

                ttk.Button(popup, text="סגור", command=popup.destroy).grid(row=len(fields), columnspan=2, pady=20)

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

                # פונקציה שתתעדכן בעת לחיצה על מדף במפה
                def select_shelf(row, column):
                    entry_shelf_row.delete(0, tk.END)
                    entry_shelf_column.delete(0, tk.END)
                    entry_shelf_row.insert(0, str(row))
                    entry_shelf_column.insert(0, str(column))

                # עדכון מפת המחסן לפי הסניף של הפריט
                update_warehouse_map(warehouse_map_frame, item[4], select_shelf)

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
            image.thumbnail((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo

            def zoom_image():
                top = tk.Toplevel()
                top.title("תצוגת תמונה")
                big_img = Image.open(image_path)
                big_photo = ImageTk.PhotoImage(big_img)
                label = tk.Label(top, image=big_photo)
                label.image = big_photo
                label.pack()

            image_label.bind("<Button-1>", lambda e: zoom_image())

        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה: {e}")

    image_path = {"val": None}  # משתמש במילון כדי לעדכן מתוך nested

    def clear_inputs():
        for w in entries:
            if isinstance(w, ttk.Entry):
                w.delete(0, tk.END)
            elif isinstance(w, ttk.Combobox):
                w.set("")
        image_label.config(image="")
        image_label.image = None
        image_path["val"] = None

    global entry_sku, entry_name, entry_category, entry_quantity, entry_price, entry_branch, entry_color, entry_size, entry_shelf_row, entry_shelf_column
    global image_label, image_path_var, warehouse_map_frame

    # מסגרת ראשית
    update_item_frame = tk.Frame(tree_frame, bg="#ffffff")
    update_item_frame.pack(fill="both", expand=True, padx=2, pady=2)

    # כותרת
    tk.Label(update_item_frame, text="🆕 Update Item", font=("Segoe UI", 25, "bold"),
             bg="#ffffff", fg="#2f3640").grid(row=0, column=8, columnspan=4, pady=5)

    # שדות טקסט
    labels = ["SKU 🔎", "שם פריט ✏️", "קטגוריה 🏷️", "כמות 📦", "הוספת כמות ➕",
              "מחיר 💲", "סניף 🏬", "צבע 🎨", "מידה 📏", "שורה במדף 🛒", "טור במדף 🛒", "נתיב תמונה 📷"]
    entries = []
    for idx, text in enumerate(labels):
        tk.Label(update_item_frame, text=text, bg="#ffffff", anchor="w", font=("Segoe UI", 16)) \
            .grid(row=idx + 1, column=0, padx=15, pady=15, sticky="w")
        entry = ttk.Entry(update_item_frame, width=30)
        entry.grid(row=idx + 1, column=1, padx=15, pady=15, sticky="w")
        entries.append(entry)

    (entry_sku, entry_name, entry_category, entry_quantity, entry_add_quantity,
     entry_price, entry_branch, entry_color, entry_size, entry_shelf_row,
     entry_shelf_column) = entries[:11]

    image_path_var = tk.StringVar()
    image_entry = ttk.Entry(update_item_frame, textvariable=image_path_var, width=30)
    image_entry.grid(row=12, column=1, padx=10, pady=10, sticky="w")

    # תמונה
    image_label = tk.Label(update_item_frame)
    image_label.grid(row=1, column=2, rowspan=8, padx=30, pady=30)

    # כפתורים
    tk.Button(update_item_frame, text="בחר תמונה 📷", command=select_image,
              bg="#3498db", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=12, column=2, padx=10, pady=10)

    tk.Button(update_item_frame, text="טען פריט 🔎", command=load_item_details,
              bg="#2ecc71", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=1, column=2, padx=10, pady=10)

    tk.Button(update_item_frame, text="עדכן פריט ✔️", command=update_item,
              bg="#27ae60", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=12, column=3, padx=10, pady=10)

    tk.Button(update_item_frame, text="נקה 🧹", command=clear_inputs,
              bg="#e67e22", fg="white", font=("Segoe UI", 16), relief="flat") \
        .grid(row=12, column=4, padx=10, pady=10)

    # הוספת מפת מחסן
    warehouse_map_frame = tk.Frame(update_item_frame, bg="#ffffff")
    warehouse_map_frame.grid(row=2, column=5, rowspan=8, padx=10, pady=10,sticky="e")


def open_delete_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def update_item_visibility():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("שים לב", "אנא בחר פריט מתוך הרשימה")
            return

        sku = tree.item(selected_item)['values'][0]

        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("UPDATE inventory SET is_active = FALSE WHERE sku = %s", (sku,))
            connection.commit()


            messagebox.showinfo("הצלחה", "הפריט סומן כלא זמין")
            refresh_items_table()

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעדכון הפריט: {e}")
        finally:
            if connection:
                connection.close()

    def refresh_items_table():
        for row in tree.get_children():
            tree.delete(row)

        #עדכון סטטוס אוטומטי לפי כמות
        try:
            connection = connect_to_database()
            curses = connection.cursor()
            curses.execute("UPDATE inventory SET is_active = FALSE WHERE quantity = 0 AND is_active = TRUE")
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעדכון סטטוס פריטים: {e}")
        finally:
            if connection:
                connection.close()

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # שליפת הפריטים
            query = "SELECT sku, item_name, quantity, is_active FROM inventory"
            if not show_hidden_var.get():
                query += " WHERE is_active = TRUE"

            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                sku, name, qty, active = row
                status = "זמין" if active else "לא-זמין"
                tag = "active" if active else "inactive"
                tree.insert("", "end", values=(sku, name, qty, status), tags=(tag,))

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליפת פריטים: {e}")
        finally:
            if connection:
                connection.close()

    def restore_selected_item():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("שים לב", "אנא בחר פריט מתוך הרשימה")
            return

        sku = tree.item(selected_item)['values'][0]
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("UPDATE inventory SET is_active = TRUE WHERE sku = %s", (sku,))
            connection.commit()
            messagebox.showinfo("הצלחה", "הפריט הוחזר לרשימת המלאי הפעילה")
            refresh_items_table()

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בהחזרת פריט: {e}")
        finally:
            if connection:
                connection.close()


    # כותרת
    delete_item_frame=tk.LabelFrame(tree_frame, text="🗑️ ניהול זמינות פריטים",font=("Segoe UI", 24, "bold"), bg="#ffffff", fg="#2c3e50")
    delete_item_frame.pack(fill="both", padx=20, pady=(10, 20))

    tk.Label(delete_item_frame, text="🔎Enter The SKU:", font=("Segoe UI", 18, "bold"),
        bg="#ffffff", fg="#34495e").grid(row=0, column=0, padx=5, pady=5)

    entry_sku = ttk.Entry(delete_item_frame, font=("Segoe UI", 11), width=25)
    entry_sku.grid(row=0, column=1, padx=10, pady=8)

    btn_hide = tk.Button(
        delete_item_frame, text="🚫 הסתר פריט", font=("Segoe UI", 12, "bold"),
        bg="#e74c3c", fg="white", activebackground="#c0392b",
        relief="flat", padx=15, pady=6, command=update_item_visibility
    )
    btn_hide.grid(row=0, column=2, padx=10, pady=8)

    # כפתור החזרת פריט
    btn_restore = tk.Button(
        delete_item_frame, text="♻️ החזר פריט פעיל", font=("Segoe UI", 12, "bold"),
        bg="#2ecc71", fg="white", activebackground="#27ae60",
        relief="flat", padx=20, pady=8, command=restore_selected_item
    )
    btn_restore.grid(row=0, column=3, padx=10, pady=8)

    # צ'קבוקס
    show_hidden_var = tk.BooleanVar()
    show_hidden_checkbox = ttk.Checkbutton(
        delete_item_frame, text="הצג גם פריטים מוסתרים",
        variable=show_hidden_var, command=refresh_items_table
    )
    show_hidden_checkbox.grid(row=0, column=4, padx=10, pady=8)

    # ----- עץ -----

    columns = (
    "SKU", "Item_name", "Quantity", "Status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background="#ffffff",
                    foreground="#2c3e50",
                    fieldbackground="#ffffff",
                    rowheight=35,
                    font=("Segoe UI", 25))
    style.configure("Custom.Treeview.Heading",
                    background="#34495e",
                    foreground="white",
                    font=("Segoe UI", 25, "bold"))
    style.map("Custom.Treeview", background=[("selected", "#d0ebff")])

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

    # עיצוב צבעים לשורות
    tree.tag_configure("active", background="#e6ffe6")  # ירוק בהיר
    tree.tag_configure("inactive", background="#ffe6e6")  # אדום בהיר

    # קריאה ראשונית לטעינת טבלה
    refresh_items_table()


def open_search_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()


    def search_items(event=None):
        branch = combo_branch.get()  # הסניף הנבחר
        sku = entry_sku.get().strip()
        name = entry_name.get().strip()
        category = entry_category.get().strip()

        query = """
            SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, 
                   inventory.price, inventory.color, inventory.size, inventory.shelf_row, inventory.shelf_column, 
                   branches.branch_id, branches.branch_name, branches.branch_address, inventory.image_path
            FROM inventory
            INNER JOIN branches ON inventory.branch_id = branches.branch_id
            WHERE 1=1
        """
        params = []

        if sku:
            query += " AND inventory.sku LIKE %s"
            params.append(f"%{sku}%")
        if name:
            query += " AND inventory.item_name LIKE %s"
            params.append(f"%{name}%")
        if category:
            query += " AND inventory.category LIKE %s"
            params.append(f"%{category}%")
        if branch and branch != "בחר סניף":
            query += " AND branches.branch_address LIKE %s"
            params.append(f"%{branch}%")

        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

            tree.delete(*tree.get_children())
            if results:
                for index, item in enumerate(results):
                    tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                    tree.insert("", tk.END, values=item[:-1], tags=(tag,))
                status_label.config(text=f"נמצאו {len(results)} תוצאות")
                first_image = results[0][-1]
                display_image(first_image)
            else:
                status_label.config(text="לא נמצאו תוצאות")
                image_label.config(image="")
                image_label.image = None

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בחיפוש: {e}")
        finally:
            if connection:
                connection.close()

    def display_image(image_file):
        try:
            if image_file and os.path.exists(image_file):
                img = Image.open(image_file)
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + img.size, fill=255)
                img.putalpha(mask)
                photo = ImageTk.PhotoImage(img)

                image_label.config(image=photo)
                image_label.image = photo
            else:
                image_label.config(image="")
                image_label.image = None
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה: {e}")

    def show_item_details(event):
        selected_item = tree.focus()
        if selected_item:
            values = tree.item(selected_item, 'values')
            if not values:
                return

            top = tk.Toplevel(tree_frame)
            top.title("פרטי פריט")
            top.geometry("400x500")
            top.configure(bg="white")

            # שליפת תמונה
            sku = values[0]
            try:
                connection = connect_to_database()
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT image_path FROM inventory WHERE sku = %s
                """, (sku,))
                result = cursor.fetchone()
                image_file = result[0] if result else None
            except:
                image_file = None
            finally:
                if connection:
                    connection.close()

            if image_file and os.path.exists(image_file):
                img = Image.open(image_file)
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(top, image=photo, bg="white")
                img_label.image = photo
                img_label.pack(pady=10)
            else:
                tk.Label(top, text="אין תמונה", bg="white").pack(pady=10)

            # פרטי הפריט
            details = [
                f"SKU: {values[0]}",
                f"שם: {values[1]}",
                f"קטגוריה: {values[2]}",
                f"כמות: {values[3]}",
                f"מחיר: {values[4]} ₪",
                f"צבע: {values[5]}",
                f"מידה: {values[6]}",
                f"מיקום: שורה {values[7]}, עמודה {values[8]}",
                f"סניף: {values[10]}",
                f"כתובת: {values[11]}"
            ]

            for d in details:
                tk.Label(top, text=d, bg="white", font=("Arial", 11)).pack(pady=2)
    def on_tree_select(event):
        selected_item = tree.focus()
        if selected_item:
            values = tree.item(selected_item, 'values')
            if values:
                sku = values[0]
                try:
                    connection = connect_to_database()
                    cursor = connection.cursor()
                    cursor.execute("SELECT image_path FROM inventory WHERE sku = %s", (sku,))
                    result = cursor.fetchone()
                    if result:
                        display_image(result[0])
                except:
                    pass
                finally:
                    if connection:
                        connection.close()

    # ----- עיצוב המסכים -----

    form_frame = tk.Frame(tree_frame, bg="#f8f9fa", bd=2, relief="groove")
    form_frame.pack(pady=15, padx=20, fill="x")

    def create_entry(parent, label_text, row, col):
        label = tk.Label(parent, text=label_text, font=("Arial", 16, "bold"), bg="#f8f9fa")
        label.grid(row=row, column=col, padx=5, pady=5)
        entry = tk.Entry(parent, bd=2, relief="groove", font=("Arial", 16))
        entry.grid(row=row, column=col+1, padx=5, pady=5)
        return entry

    entry_sku = create_entry(form_frame, "SKU:", 0, 2)
    entry_name = create_entry(form_frame, "שם פריט:", 0, 4)
    entry_category = create_entry(form_frame, "קטגוריה:", 0, 6)
    # ComboBox for Branch selection
    label_branch = tk.Label(form_frame, text="בחר סניף:", font=("Arial", 16, "bold"), bg="#f8f9fa")
    label_branch.grid(row=0, column=0, padx=5, pady=5)
    combo_branch = ttk.Combobox(form_frame, values=["בחר סניף"], state="readonly", font=("Arial", 16))
    combo_branch.grid(row=0, column=1, padx=5, pady=5)

    # שליפת כל הסניפים מהמאגר
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT branch_address FROM branches")
        branches = cursor.fetchall()
        for branch in branches:
            combo_branch['values'] += (branch[0],)
    except mysql.connector.Error as e:
        messagebox.showerror("שגיאה", f"שגיאה בהבאת סניפים: {e}")
    finally:
        if connection:
            connection.close()
    # חיפוש בזמן אמת
    combo_branch.bind("<<ComboboxSelected>>", search_items)  # חיפוש עדכון לאחר בחירת סניף
    entry_sku.bind("<KeyRelease>", search_items)
    entry_name.bind("<KeyRelease>", search_items)
    entry_category.bind("<KeyRelease>", search_items)

    search_button = tk.Button(form_frame, text="🔍 חפש", font=("Arial", 16), bg="#007bff", fg="white",
                              relief="raised", bd=2, command=search_items)
    search_button.grid(row=0, column=8, padx=10, pady=5)

    # ----- עץ -----

    columns = ("SKU", "שם פריט", "קטגוריה", "כמות", "מחיר", "צבע", "מידה", "שורת מדף", "עמודת מדף", "ID סניף", "שם סניף", "כתובת סניף")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 16), rowheight=30)
    style.map('Treeview', background=[('selected', '#007bff')])
    style.configure("Treeview.Heading", font=("Arial", 16, "bold"))

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.tag_configure('oddrow', background="white")
    tree.tag_configure('evenrow', background="#e9f2fb")

    tree.pack(pady=10, padx=10, fill="both", expand=True)

    # בחירת שורה - להציג תמונה
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # דאבל קליק - הצגת פרטים מלאים
    tree.bind("<Double-1>", show_item_details)

    # ----- תמונה -----

    image_label = tk.Label(tree_frame, bg="white", bd=2, relief="groove")
    image_label.pack(pady=10)

    # ----- סטטוס -----

    status_label = tk.Label(tree_frame, text="", font=("Arial", 16, "italic"), fg="gray")
    status_label.pack(pady=5)
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

    def remove_selected_item_from_cart():
        selected_index = cart_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("שים לב", "לא נבחר פריט להסרה")
            return

        index = selected_index[0]
        item = cart[index]

        # עדכון סכום כולל
        item_total = item["price"] * item["quantity"]
        total_amount.set(total_amount.get() - float(item_total))

        # הסרה מהעגלה
        cart_listbox.delete(index)
        cart.pop(index)
        update_cart_display()


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

    ttk.Button(right_frame, text="הסר פריט נבחר", command=remove_selected_item_from_cart).pack(pady=5)


    total_label = ttk.Label(right_frame, text="סה\"כ לתשלום: ₪0.00")
    total_label.pack(pady=5)


def open_finance_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    left_frame = tk.LabelFrame(tree_frame, text="סניף מס' 1", padx=10, pady=10)
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_frame = tk.LabelFrame(tree_frame, text="סניף מס' 2", padx=10, pady=10)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT branch_id, branch_name FROM branches ORDER BY branch_id LIMIT 2")
    branches = cursor.fetchall()

    def create_branch_finance_display(frame, branch_id, branch_name):
        cursor.execute("SELECT SUM(total_price) FROM purchases WHERE branch_name = %s", (branch_id,))
        income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(total_cost) FROM expenses WHERE branch_id = %s", (branch_id,))
        expenses = cursor.fetchone()[0] or 0

        net_profit = income - expenses

        tk.Label(frame, text=f"שם הסניף: {branch_name}", font=("Arial", 14)).pack(pady=5)
        tk.Label(frame, text=f"רווחים: {income:.2f} ₪", font=("Arial", 12), fg="green").pack(pady=5)
        tk.Label(frame, text=f"הוצאות: {expenses:.2f} ₪", font=("Arial", 12), fg="red").pack(pady=5)
        tk.Label(frame, text=f"קופה: {net_profit:.2f} ₪", font=("Arial", 14, "bold")).pack(pady=10)

    # יצירת תצוגה לשני הסניפים
    if len(branches) >= 1:
        create_branch_finance_display(left_frame, branches[0][0], branches[0][1])
    if len(branches) >= 2:
        create_branch_finance_display(right_frame, branches[1][0], branches[1][1])

    connection.close()
