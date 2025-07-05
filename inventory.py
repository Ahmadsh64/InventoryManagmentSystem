import os
import shutil
from datetime import datetime
import mysql.connector
from PIL import Image, ImageTk, ImageDraw
from scanQR import scan_qr_code
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd
from database import connect_to_database
import mysql.connector
import tkinter as tk
import mysql.connector
from ui_utils import create_window_button
from warhouse import Warehouse_Map

# === הגדרות תצוגה ===
CELL_WIDTH = 60
CELL_HEIGHT = 40
BLOCK_SPACING = 30
TOP_MARGIN = 50
LEFT_MARGIN = 50
GRID_SIZE = 10
zones = [chr(i) for i in range(ord("A"), ord("J") + 1)]  # אזורים A-J

# === משתנים גלובליים ===
canvas = None
current_zone_index = 0
cells = {}
view_state = {
    "mode": "column",
    "zone": zones[0],
    "zone_index": 0
}


# === שליפת פריטים לפי אזור וסניף ===
def get_inventory_by_zone(zone, branch_id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT shelf_zone, shelf_row, shelf_column, sku, item_name, quantity, color, size, is_active
        FROM inventory
        WHERE shelf_zone = %s AND branch_id = %s
    """
    cursor.execute(query, (zone, branch_id))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# === ציור מצב עמודות (מעודכן עם branch_id ו-select_shelf) ===
def draw_column_view(cnv, tree_frame, branch_id, select_shelf):
    cnv.delete("all")
    for zone_index, zone in enumerate(zones):
        block_x = LEFT_MARGIN + zone_index * (CELL_WIDTH + BLOCK_SPACING)
        inventory_data = get_inventory_by_zone(zone, branch_id)
        inventory_map = {(item['shelf_row'], item['shelf_column']): item for item in inventory_data}

        for row in range(1, GRID_SIZE + 1):
            x1 = block_x
            y1 = TOP_MARGIN + (row - 1) * CELL_HEIGHT
            x2 = x1 + CELL_WIDTH
            y2 = y1 + CELL_HEIGHT

            item = inventory_map.get((row, 1))
            fill_color = "white"
            text = f"{zone}-{row:02}"

            if item:
                if item["quantity"] == 0 or item["is_active"] == 0:
                    fill_color = "red"
                elif item["quantity"] <= 10:
                    fill_color = "orange"
                elif item["quantity"] < 50:
                    fill_color = "yellow"
                else:
                    fill_color = "lightgreen"
                text = f"{item['item_name']}\nQty:{item['quantity']}"
            else:
                # אם פנוי – הפוך ללחיץ
                rect_id = cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                text_id = cnv.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Arial", 14))
                cnv.tag_bind(rect_id, "<Button-1>", lambda e, r=row, z=zone: select_shelf(r, 1, z))
                cnv.tag_bind(text_id, "<Button-1>", lambda e, r=row, z=zone: select_shelf(r, 1, z))
                continue  # דילוג כדי לא לצייר פעמיים

            cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
            cnv.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Arial", 10))

        label_id = cnv.create_text(block_x + CELL_WIDTH // 2, TOP_MARGIN + 10 * CELL_HEIGHT + 20,
                                   text=zone, font=("Arial", 14, "bold"), fill="blue")
        cnv.tag_bind(label_id, "<Button-1>", lambda e, z=zone: switch_to_grid_view(z, tree_frame, branch_id, select_shelf))

    create_navigation_buttons(tree_frame, branch_id, select_shelf)

# === ציור מצב רשת (מעודכן) ===
def draw_grid_view(cnv, zone, page_index, tree_frame, branch_id, select_shelf):
    cnv.delete("all")
    inventory_data = get_inventory_by_zone(zone, branch_id)
    inventory_map = {(item['shelf_row'], item['shelf_column']): item for item in inventory_data}
    cells.clear()

    for row in range(1, GRID_SIZE + 1):
        for col in range(1, GRID_SIZE + 1):
            x1 = LEFT_MARGIN + (col - 1) * CELL_WIDTH
            y1 = TOP_MARGIN + (row - 1) * CELL_HEIGHT
            x2 = x1 + CELL_WIDTH
            y2 = y1 + CELL_HEIGHT

            item = inventory_map.get((row, col))
            fill_color = "white"
            text = f"{zone}-{row:02}-{col:02}"

            if item:
                if item["quantity"] == 0 or item["is_active"] == 0:
                    fill_color = "red"
                elif item["quantity"] <= 10:
                    fill_color = "orange"
                elif item["quantity"] < 50:
                    fill_color = "yellow"
                else:
                    fill_color = "lightgreen"
                text = f"{item['item_name']}\nQty:{item['quantity']}"
                rect_id = cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                text_id = cnv.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=text, font=("Arial", 8))
                cells[rect_id] = item
                cells[text_id] = item
                cnv.tag_bind(rect_id, "<Button-1>", on_cell_click)
                cnv.tag_bind(text_id, "<Button-1>", on_cell_click)
            else:
                # לחיצה על מיקום פנוי
                rect_id = cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                text_id = cnv.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=text, font=("Arial", 8))
                cnv.tag_bind(rect_id, "<Button-1>", lambda e, r=row, c=col, z=zone: select_shelf(r, c, z))
                cnv.tag_bind(text_id, "<Button-1>", lambda e, r=row, c=col, z=zone: select_shelf(r, c, z))

    cnv.create_text(cnv.winfo_reqwidth() // 2, TOP_MARGIN // 2, text=f"Zone: {zone}", font=("Arial", 16, "bold"))
    create_window_button(tree_frame, branch_id, select_shelf)

# === שאר הפונקציות (מתוקנות גם כן): ===
def switch_to_grid_view(zone, tree_frame, branch_id, select_shelf):
    global current_zone_index
    view_state["mode"] = "grid"
    view_state["zone"] = zone
    view_state["zone_index"] = zones.index(zone)
    current_zone_index = view_state["zone_index"]
    draw_grid_view(canvas, zone, current_zone_index, tree_frame, branch_id, select_shelf)

def grid_prev_zone(tree_frame, branch_id, select_shelf):
    global current_zone_index
    if current_zone_index > 0:
        current_zone_index -= 1
        draw_grid_view(canvas, zones[current_zone_index], current_zone_index, tree_frame, branch_id, select_shelf)

def grid_next_zone(tree_frame, branch_id, select_shelf):
    global current_zone_index
    if current_zone_index < len(zones) - 1:
        current_zone_index += 1
        draw_grid_view(canvas, zones[current_zone_index], current_zone_index, tree_frame, branch_id, select_shelf)

def create_navigation_buttons(tree_frame, branch_id, select_shelf):
    remove_navigation_buttons(tree_frame)
    button_frame = tk.Frame(tree_frame)
    button_frame.pack(pady=10)
    button_frame._custom_buttons = True
    create_window_button(button_frame, text="← Prev", command=lambda: grid_prev_zone(tree_frame, branch_id, select_shelf)).pack(side=tk.LEFT, padx=10)
    create_window_button(button_frame, text="Back to Columns", command=lambda: draw_column_view(canvas, tree_frame, branch_id, select_shelf)).pack(side=tk.LEFT, padx=10)
    create_window_button(button_frame, text="Next →", command=lambda: grid_next_zone(tree_frame, branch_id, select_shelf)).pack(side=tk.LEFT, padx=10)


def remove_navigation_buttons(tree_frame):
    for widget in tree_frame.winfo_children():
        if isinstance(widget, tk.Frame) and hasattr(widget, "_custom_buttons"):
            widget.destroy()


def on_cell_click(event):
    clicked_id = canvas.find_withtag("current")[0]
    item = cells.get(clicked_id)
    if item:
        info = (
            f"Item Name: {item['item_name']}\n"
            f"SKU: {item['sku']}\n"
            f"Quantity: {item['quantity']}\n"
            f"Color: {item['color']}\n"
            f"Size: {item['size']}\n"
            f"Shelf Zone: {item['shelf_zone']}\n"
            f"Shelf Row: {item['shelf_row']}\n"
            f"Shelf Column: {item['shelf_column']}"
        )
        messagebox.showinfo("Item Information", info)

# === יצירת המפה הראשית ===
def create_warehouse_map(tree_frame, select_shelf, branch_id):
    global canvas

    for widget in tree_frame.winfo_children():
        widget.destroy()

    canvas_width = LEFT_MARGIN  + (CELL_WIDTH + BLOCK_SPACING) * len(zones)
    canvas_height = TOP_MARGIN  + CELL_HEIGHT * GRID_SIZE + 120

    canvas = tk.Canvas(tree_frame, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(anchor="center")

    draw_column_view(canvas, tree_frame, branch_id, select_shelf)

def view_inventory(tree_frame):
    from PIL import Image, ImageTk
    import os

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

        # === מסגרת ראשית ===
        main_frame = tk.Frame(tree_frame, bg="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # === מסגרת חיפוש ===
        search_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        search_frame.pack(fill="x", pady=(0, 10))

        title_label = tk.Label(
            search_frame, text="view_inventory🔍",
            font=("Segoe UI", 22, "bold"), bg="#ffffff", fg="#2f3640"
        )
        title_label.grid(row=0, column=0, columnspan=10, pady=20)

        fields = [("Item Name:", 1, 0), ("Branch:", 1, 2), ("Category:", 1, 4)]
        entries = {}

        for text, r, c in fields:
            tk.Label(search_frame, text=text, font=("Segoe UI", 14), bg="#ffffff").grid(row=r, column=c, padx=10, pady=10, sticky="w")

            if text == "Branch:":
                branch_names = list(set([row[11] for row in rows]))
                branch_names.sort()
                branch_names.insert(0, "")
                entry = ttk.Combobox(search_frame, values=branch_names, font=("Segoe UI", 12), state="readonly")
                entry.current(0)
            else:
                entry = tk.Entry(search_frame, font=("Segoe UI", 12))

            entry.grid(row=r, column=c + 1, padx=10, pady=10, sticky="ew")
            entries[text] = entry

        search_frame.grid_columnconfigure((1, 3, 5, 7), weight=1)

        def show_warehouse_map():
            selected_branch = branch_names
            if not selected_branch or selected_branch == "בחר סניף":
                messagebox.showwarning("שים לב", "יש לבחור סניף לפני הצגת מפת המחסן")
                return

            skus_to_highlight = []
            for child in tree.get_children():
                values = tree.item(child, 'values')
                if values:
                    skus_to_highlight.append(values[0])

            Warehouse_Map(branch_address=selected_branch, highlight_skus=skus_to_highlight)

        # === פונקציות סינון ורענון ===
        def filter_inventory_advanced():
            name = entries["Item Name:"].get().strip().lower()
            branch = entries["Branch:"].get().strip().lower()
            category = entries["Category:"].get().strip().lower()
            tree.delete(*tree.get_children())
            for row in rows:
                if (not name or name in row[1].lower()) and \
                   (not category or category in row[2].lower()) and \
                   (not branch or branch in row[11].lower()):
                    tree.insert("", tk.END, values=row)

        def reset_inventory():
            for entry in entries.values():
                entry.set("") if isinstance(entry, ttk.Combobox) else entry.delete(0, tk.END)
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", tk.END, values=row)

        # === כפתורים ===
        button_frame = tk.Frame(search_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=10, pady=10)

        create_window_button(button_frame, "🔍Search", filter_inventory_advanced).pack(side="left", padx=10)
        create_window_button(button_frame, "Reset", reset_inventory).pack(side="left", padx=10)
        create_window_button(button_frame, text="warehouse Map", command=show_warehouse_map).pack(side="left", padx=10)

        # === טבלה ===
        table_frame = tk.Frame(main_frame, bg="#f5f6fa")
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
                        font=("Segoe UI", 13, "bold"))
        style.map("Custom.Treeview", background=[("selected", "#d0ebff")])

        columns = ["SKU", "item_name", "category", "quantity", "price", "color", "size", "shelf_row", "shelf_column",
                   "branch_id", "branch_name", "branch_address"]

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        # === הצגת תמונה ===
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
    def select_shelf(row, col, zone):
        entries["shelf_row"].delete(0, tk.END)
        entries["shelf_row"].insert(0, row)
        entries["shelf_column"].delete(0, tk.END)
        entries["shelf_column"].insert(0, col)
        entries["shelf_zone"].delete(0, tk.END)
        entries["shelf_zone"].insert(0, zone)

    def scan_and_fill_sku():
        scanned = scan_qr_code()
        if scanned:
            entries["SKU"].delete(0, tk.END)
            entries["SKU"].insert(0, scanned)

    def refresh_map():
        branch_name = entries["branch"].get()
        branch_id = branch_dict.get(branch_name, -1)
        if branch_id != -1:
            create_warehouse_map(warehouse_frame, select_shelf, branch_id)

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

    def clear_inputs(entries, image_path):
        for w in entries.values():
            if isinstance(w, ttk.Entry):
                w.delete(0, tk.END)
            elif isinstance(w, ttk.Combobox):
                w.set("")

        image_label.config(image="")
        image_label.image = None
        image_path.set("")  # ✅ מנקה גם את שדה הנתיב של התמונה

    def add_item(entries, image_path):
        # קריאת ערכים
        name     = entries["name"].get().strip()
        sku      = entries["SKU"].get().strip()
        category = entries["category"].get().strip()
        qty      = entries["quantity"].get().strip()
        price    = entries["price"].get().strip()
        branch_n = entries["branch"].get().strip()
        color    = entries["color"].get().strip()
        size     = entries["size"].get().strip()
        zone     = entries["shelf_zone"].get().strip()
        row      = entries["shelf_row"].get().strip()
        col      = entries["shelf_column"].get().strip()
        img_p    = image_path.get()

        # ולידציה
        if not (name and sku and category and qty.isdigit()
                and price.replace('.', '', 1).isdigit()
                and branch_n in branch_dict
                and color and size and zone and row.isdigit() and col.isdigit()
                and img_p):
            messagebox.showerror("שגיאה", "אנא מלא/י את השדות כראוי כולל תמונה")
            return

        # שמירת תמונה בתיקיה המקומית
        os.makedirs("static/images", exist_ok=True)
        img_p = os.path.join("static/images", os.path.basename(img_p))
        dest_path = os.path.join("static/images", os.path.basename(img_p))
        shutil.copy(image_path.get(), dest_path)

        # הוספה למסד
        try:
            conn = connect_to_database()
            cur  = conn.cursor()
            cur.execute(
                """INSERT INTO inventory
                   (item_name, SKU, category, quantity, price, branch_id, color, size, shelf_zone, shelf_row, shelf_column, image_path)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    name, sku, category, int(qty), float(price),
                    branch_dict[branch_n], color, size, zone,
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
        receipt.configure(bg="white")
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
            bg="white", fg="#333"
        ).pack(padx=40, pady=30)

        messagebox.showinfo("הצלחה", "הפריט נוסף בהצלחה!")

    tree_frame.configure(bg="white")

    tk.Label(
        tree_frame, text="🆕 Add New Item", font=("Segoe UI", 24, "bold"),
        bg="white", fg="#2f3640"
    ).grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="w")

    entries = {}
    labels = {
        "SKU": "SKU 🔎",
        "name": "Item Name ✏️",
        "category": "Category 🏷️",
        "quantity": "Quantity 📦",
        "price": "Price 💲",
        "branch": "Branch 🏬",
        "color": "Color 🎨",
        "size": "Size 📏",
        "shelf_zone": "Zone 🗃️",
        "shelf_row": "Shelf Row 📐",
        "shelf_column": "Shelf Column 📐"
    }

    style = ttk.Style()
    style.configure("TEntry", font=("Segoe UI", 13))
    style.configure("TCombobox", font=("Segoe UI", 13))

    # === יצירת שדות ===
    for idx, (key, label_text) in enumerate(labels.items()):
        tk.Label(tree_frame, text=label_text, bg="white",
                 font=("Segoe UI", 14)).grid(row=idx + 1, column=0, padx=15, pady=8, sticky="w")

        if key == "branch":
            entry = ttk.Combobox(tree_frame, values=branch_names, width=28, state="readonly")
            entry.bind("<<ComboboxSelected>>", lambda e: refresh_map())
        else:
            entry = ttk.Entry(tree_frame, width=30)

        entry.grid(row=idx + 1, column=1, padx=15, pady=8, sticky="w")
        entries[key] = entry

        if key == "SKU":
            btn_scan = tk.Button(tree_frame, text="📷 QR Scanner", command=scan_and_fill_sku,
                                 bg="#9b59b6", fg="white", font=("Segoe UI", 11), relief="flat", cursor="hand2")
            btn_scan.grid(row=idx + 1, column=2, padx=5, pady=8, sticky="w")

    # === שדה תמונה ===
    image_path_var = tk.StringVar()
    tk.Label(tree_frame, text="Image Path", bg="white", font=("Segoe UI", 14)) \
        .grid(row=len(labels) + 1, column=0, padx=15, pady=8, sticky="w")
    image_entry = ttk.Entry(tree_frame, textvariable=image_path_var, width=30)
    image_entry.grid(row=len(labels) + 1, column=1, padx=15, pady=8, sticky="w")

    # === תצוגת תמונה ===
    image_label = tk.Label(tree_frame, bg="#ffffff", relief="solid", bd=1)
    image_label.grid(row=2, column=3, rowspan=5, padx=10, pady=10, sticky="n")

    # === כפתורים עיקריים ===
    btn_font = ("Segoe UI", 14)
    btn_pad = {"padx": 10, "pady": 15}

    def create_button(text, command, bg_color):
        return tk.Button(tree_frame, text=text, command=command,
                         bg=bg_color, fg="white", font=btn_font,
                         relief="flat", cursor="hand2")

    create_button("📷 Select Image", select_image, "#3498db") \
        .grid(row=13, column=0, sticky="w", **btn_pad)

    create_button("✔️ Add Item", lambda: add_item(entries, image_path_var), "#27ae60") \
        .grid(row=13, column=1, sticky="w", **btn_pad)

    create_button("🧹 Clear", lambda: clear_inputs(entries, image_path_var), "#e67e22") \
        .grid(row=14, column=0, sticky="w", **btn_pad)

    create_button("🔄 Load Shelves", refresh_map, "#2980b9") \
        .grid(row=14, column=1, sticky="w", **btn_pad)

    # === מפת מחסן ===
    tk.Label(tree_frame, text="📦 Warehouse Map", font=("Segoe UI", 20, "bold"),
             bg="white", fg="#2f3640") \
        .grid(row=0, column=4, padx=(30, 10), pady=(10, 20), sticky="w")

    warehouse_frame = tk.Frame(tree_frame, bg="white", relief="groove", borderwidth=1)
    warehouse_frame.grid(row=1, column=4, rowspan=12, padx=(30, 10), pady=10, sticky="n")
    # שמירת משתנים גלובליים אם צריך
    global add_item_entries, add_item_image_label
    add_item_entries = entries
    add_item_image_label = image_label

def open_update_item_window(tree_frame, sku=""):
    # ניקוי המסגרת הקודמת
    for widget in tree_frame.winfo_children():
        widget.destroy()

    # שליפת סניפים מתוך DB
    try:
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT b.branch_id, b.branch_name FROM inventory_system.branches b "
                    "JOIN inventory_system.inventory i ON i.branch_id = b.branch_id")
        branch_data = cur.fetchall()
        conn.close()
    except Exception as e:
        messagebox.showerror("שגיאה", f"לא ניתן לטעון סניפים: {e}")
        branch_data = []

    branch_dict = {name: bid for bid, name in branch_data}
    branch_names = [""] + sorted(branch_dict.keys())

    # פונקציה לבחירת מיקום מדף
    def select_shelf(row, col, zone):
        entries["shelf_row"].delete(0, tk.END)
        entries["shelf_row"].insert(0, row)
        entries["shelf_column"].delete(0, tk.END)
        entries["shelf_column"].insert(0, col)
        entries["shelf_zone"].delete(0, tk.END)
        entries["shelf_zone"].insert(0, zone)
    def scan_and_fill_sku():
        scanned = scan_qr_code()
        if scanned:
            entries["SKU"].delete(0, tk.END)
            entries["SKU"].insert(0, scanned)

    def refresh_map():
        branch_name = entries["branch"].get()
        branch_id = branch_dict.get(branch_name, -1)
        if branch_id != -1:
            create_warehouse_map(warehouse_frame, select_shelf, branch_id)

    # פונקציות עזר
    image_path = {"val": None}  # משתמש במילון כדי לעדכן מתוך nested

    def display_image(image_path):
        try:
            # תיקון שם הנתיב
            image_path = image_path.replace("\\", "/")

            # קריאה לקובץ
            img = Image.open(image_path)
            img = img.resize((100, 100))  # גודל מותאם
            photo = ImageTk.PhotoImage(img)
            image_label.configure(image=photo)
            image_label.image = photo  # שמירה למניעת מחיקה ע"י garbage collector

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
            messagebox.showerror("שגיאה", f"לא ניתן לטעון את התמונה:\n{e}")

    def select_image():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            image_path_var.set(file_path)
            image_path["val"] = image_path_var.get() # תעדכן גם את המילון
            display_image(file_path)

    def clear_inputs(entries, image_path):
        for w in entries.values():
            if isinstance(w, ttk.Entry):
                w.delete(0, tk.END)
            elif isinstance(w, ttk.Combobox):
                w.set("")

        image_label.config(image="")
        image_label.image = None
        image_path.set("")  # ✅ מנקה גם את שדה הנתיב של התמונה

    def update_item(entries, image_path_var):
        # קריאת ערכים
        name = entries["name"].get().strip()
        sku = entries["SKU"].get().strip()
        category = entries["category"].get().strip()
        quantity = entries["quantity"].get().strip()
        add_quantity = entries["add_quantity"].get()
        price = entries["price"].get().strip()
        branch_name = entries["branch"].get().strip()
        color = entries["color"].get().strip()
        size = entries["size"].get().strip()
        shelf_zone = entries["shelf_zone"].get().strip()
        shelf_row = entries["shelf_row"].get().strip()
        shelf_column = entries["shelf_column"].get().strip()
        image_path = image_path_var.get()

        branch_id = branch_dict.get(branch_name)

        if not (name and sku and category and quantity.isdigit()
                and price.replace('.', '', 1).isdigit()
                and branch_id is not None
                and color and size and shelf_zone and shelf_row.isdigit() and shelf_column.isdigit()
                and image_path):
            messagebox.showerror("שגיאה", "אנא מלא/י את השדות כראוי כולל תמונה")
            return

        # שמירת תמונה בתיקיה המקומית
        os.makedirs("static/images", exist_ok=True)
        img_p = os.path.join("static/images", os.path.basename(image_path))
        dest_path = os.path.join("static/images", os.path.basename(img_p))

        # מניעת העתקה אם זה אותו קובץ
        if os.path.abspath(image_path) != os.path.abspath(dest_path):
            shutil.copy(image_path, dest_path)

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # אם הוזנה כמות להוספה
            add_qty = int(add_quantity) if add_quantity and add_quantity.isdigit() else 0
            new_quantity = int(quantity) + add_qty

            # עדכון הפריט עם כמות חדשה
            cursor.execute(
                """UPDATE inventory SET item_name=%s, category=%s, quantity=%s, price=%s, branch_id=%s, 
                   color=%s, size=%s, shelf_zone=%s , shelf_row=%s, shelf_column=%s, image_path=%s WHERE SKU=%s""",
                (
                name, category, new_quantity, float(price), branch_id, color, size, shelf_zone ,shelf_row, shelf_column, image_path,
                sku)
            )

            # רישום הוצאה רק אם נוספה כמות
            if add_qty > 0:
                total_cost = add_qty * float(price)
                cursor.execute(""" 
                        INSERT INTO expenses (branch_id, sku, item_name, quantity_added, unit_price, total_cost)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (branch_id, sku, name, add_qty, float(price), total_cost))

            connection.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("שגיאה", "לא נמצא פריט עם ה-SKU שסיפקת")
            else:
                messagebox.showinfo("הצלחה", "הפריט עודכן בהצלחה")

                popup = tk.Toplevel()
                popup.title("תעודת קבלת סחורה")
                popup.configure(bg="white")
                total_cost = float(price) * add_qty

                fields = [
                    ("שם פריט:", name),
                    ("SKU:", sku),
                    ("כמות נוספת:", add_qty),
                    ("מחיר ליחידה:", f"₪{price}"),
                    ("סכום כולל:", f"₪{total_cost}"),
                    ("סניף:", branch_name),
                    ("תאריך:", datetime.now().strftime('%Y-%m-%d %H:%M'))
                ]

                for i, (label, value) in enumerate(fields):
                    ttk.Label(popup, text=label, font=("Arial", 11, "bold")).grid(row=i, column=0, sticky="e", padx=10,
                                                                                  pady=5)
                    ttk.Label(popup, text=value, font=("Arial", 11)).grid(row=i, column=1, sticky="w", padx=10, pady=5)

                ttk.Button(popup, text="סגור", command=popup.destroy).grid(row=len(fields), columnspan=2, pady=20)

            clear_inputs(entries, image_path_var)
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת עדכון הפריט: {e}")
        finally:
            if connection:
                connection.close()

    def load_item_details():
        sku = entries["SKU"].get().strip()
        if not sku:
            messagebox.showerror("שגיאה", "הזן SKU כדי לטעון פריט")
            return
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute(
                """SELECT item_name, category, quantity, price, branch_id, color, size, shelf_zone ,shelf_row, shelf_column, image_path 
                   FROM inventory WHERE SKU=%s""",
                (sku,)
            )
            item = cursor.fetchone()
            if item:
                entries["name"].delete(0, tk.END)
                entries["category"].delete(0, tk.END)
                entries["quantity"].delete(0, tk.END)
                entries["price"].delete(0, tk.END)
                entries["branch"].delete(0, tk.END)
                entries["color"].delete(0, tk.END)
                entries["size"].delete(0, tk.END)
                entries["shelf_zone"].delete(0, tk.END)
                entries["shelf_row"].delete(0, tk.END)
                entries["shelf_column"].delete(0, tk.END)

                entries["name"].insert(0, item[0])
                entries["category"].insert(0, item[1])
                entries["quantity"].insert(0, str(item[2]))
                entries["price"].insert(0, str(item[3]))
                entries["branch"].set(item[4])
                entries["color"].insert(0, item[5])
                entries["size"].insert(0, item[6])
                entries["shelf_zone"].insert(0, str(item[7]))
                entries["shelf_row"].insert(0, str(item[8]))
                entries["shelf_column"].insert(0, str(item[9]))
                image_path_var.set(item[10])

                def select_shelf(row, col, zone):
                    entries["shelf_row"].delete(0, tk.END)
                    entries["shelf_row"].insert(0, row)
                    entries["shelf_column"].delete(0, tk.END)
                    entries["shelf_column"].insert(0, col)
                    entries["shelf_zone"].delete(0, tk.END)
                    entries["shelf_zone"].insert(0, zone)

                create_warehouse_map(warehouse_frame, select_shelf, item[4])

                if item[10] and os.path.exists(item[10]):
                    display_image(item[10])
                else:
                    image_label.config(image="")
                    image_label.image = None

                branch_name = next((name for name, bid in branch_dict.items() if bid == item[4]), "")
                entries["branch"].set(branch_name)


            else:
                messagebox.showerror("שגיאה", "פריט לא נמצא")
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת פריט: {e}")
        finally:
            if connection:
                connection.close()

    # === כותרת ראשית ===
    tree_frame.configure(bg="white")

    tk.Label(
        tree_frame, text="🛠️Update Item", font=("Segoe UI", 24, "bold"),
        bg="white", fg="#2f3640"
    ).grid(row=0, column=0, columnspan=4, pady=(5, 20), sticky="w")

    entries = {}
    labels = {
        "SKU": "SKU 🔎",
        "name": "Item Name ✏️",
        "category": "Category 🏷️",
        "quantity": "Quantity 📦",
        "add_quantity": "Add Quantity ➕",
        "price": "Price 💲",
        "branch": "Branch 🏬",
        "color": "Color 🎨",
        "size": "Size 📏",
        "shelf_zone": "Zone 🗃️",
        "shelf_row": "Shelf Row 📐",
        "shelf_column": "Shelf Column 📐"
    }

    style = ttk.Style()
    style.configure("TEntry", font=("Segoe UI", 13))
    style.configure("TCombobox", font=("Segoe UI", 13))

    for idx, (key, label_text) in enumerate(labels.items()):
        tk.Label(tree_frame, text=label_text, bg="white", font=("Segoe UI", 14)) \
            .grid(row=idx + 1, column=0, padx=15, pady=8, sticky="w")

        if key == "branch":
            entry = ttk.Combobox(tree_frame, values=branch_names, width=28, state="readonly")
            entry.bind("<<ComboboxSelected>>", lambda e: refresh_map())
        else:
            entry = ttk.Entry(tree_frame, width=30)

        entry.grid(row=idx + 1, column=1, padx=15, pady=8, sticky="w")
        entries[key] = entry

        if key == "SKU":
            btn_scan = tk.Button(tree_frame, text="📷 QR Scanner", command=scan_and_fill_sku,
                                 bg="#9b59b6", fg="white", font=("Segoe UI", 11), relief="flat", cursor="hand2")
            btn_scan.grid(row=idx + 1, column=2, padx=5, pady=8, sticky="w")

    # === Image Path ===
    image_path_var = tk.StringVar()
    tk.Label(tree_frame, text="Image Path", bg="white", font=("Segoe UI", 14)) \
        .grid(row=len(labels) + 1, column=0, padx=15, pady=8, sticky="w")
    image_entry = ttk.Entry(tree_frame, textvariable=image_path_var, width=30)
    image_entry.grid(row=len(labels) + 1, column=1, padx=15, pady=8, sticky="w")

    # === תצוגת תמונה ===
    image_label = tk.Label(tree_frame, bg="white", relief="solid", bd=1)
    image_label.grid(row=2, column=3, rowspan=5, padx=10, pady=10, sticky="n")

    # === כפתור טעינת פריט ===
    tk.Button(tree_frame, text="🔍 Load Item", command=load_item_details,
              bg="#2ecc71", fg="white", font=("Segoe UI", 14), relief="flat", cursor="hand2") \
        .grid(row=1, column=3, padx=10, pady=10, sticky="w")

    # === כפתורים עיקריים ===
    btn_font = ("Segoe UI", 14)
    btn_pad = {"padx": 10, "pady": 15}

    def create_button(text, command, bg_color, row, col):
        tk.Button(tree_frame, text=text, command=command,
                  bg=bg_color, fg="white", font=btn_font, relief="flat", cursor="hand2") \
            .grid(row=row, column=col, sticky="w", **btn_pad)

    create_button("📷 Select Image", select_image, "#3498db", 11, 2)
    create_button("✔️ Update", lambda: update_item(entries, image_path_var), "#27ae60", 11, 3)
    create_button("🧹 Clear", lambda: clear_inputs(entries, image_path_var), "#e67e22", 12, 3)
    create_button("🔄 Load Shelves", refresh_map, "#2980b9", 12, 2)

    # === מפת מחסן ===
    tk.Label(tree_frame, text="📦 Warehouse Map", font=("Segoe UI", 20, "bold"),
             bg="white", fg="#2f3640") \
        .grid(row=0, column=4, padx=(30, 10), pady=(10, 20), sticky="w")

    warehouse_frame = tk.Frame(tree_frame, bg="white", relief="groove", borderwidth=1)
    warehouse_frame.grid(row=1, column=4, rowspan=12, padx=(30, 10), pady=10, sticky="n")

    global add_item_entries, add_item_image_label
    add_item_entries = entries
    add_item_image_label = image_label

    entries["SKU"].delete(0, tk.END)
    entries["SKU"].insert(0, sku)
    load_item_details()

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

    def scan_and_fill_sku():
        scanned = scan_qr_code()
        if scanned:
            entry_sku.delete(0, tk.END)
            entry_sku.insert(0, scanned)

            # חפש את השורה המתאימה בטבלה
            found = False
            for row in tree.get_children():
                values = tree.item(row)['values']
                sku_in_row = values[0]

                # ניקוי תגים קודמים קודם
                tree.item(row, tags=("active",)) if values[3] == "זמין" else tree.item(row, tags=("inactive",))

                if str(sku_in_row) == str(scanned):
                    tree.item(row, tags=("scanned",))
                    tree.selection_set(row)
                    tree.focus(row)
                    tree.see(row)  # גלילה אוטומטית
                    found = True

            if not found:
                messagebox.showwarning("לא נמצא", "הפריט שנסרק לא נמצא ברשימה")

    def refresh_items_table():
        for row in tree.get_children():
            tree.delete(row)

        # עדכון אוטומטי של זמינות לפי כמות 0
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("UPDATE inventory SET is_active = FALSE WHERE quantity = 0 AND is_active = TRUE")
            connection.commit()
        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעדכון סטטוס פריטים: {e}")
        finally:
            if connection:
                connection.close()

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            query = "SELECT sku, item_name, quantity, is_active FROM inventory WHERE 1=1"
            params = []

            if not show_hidden_var.get():
                query += " AND is_active = TRUE"

            selected_branch = branch_var.get()
            if selected_branch:
                branch_id = selected_branch.split(" - ")[0]
                query += " AND branch_id = %s"
                params.append(branch_id)

            cursor.execute(query, tuple(params))
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

    tree_frame.configure(bg="white")

    # === מסגרת ראשית עם כותרת ===
    delete_item_frame = tk.LabelFrame(
        tree_frame, text="🗑️ ניהול זמינות פריטים",
        font=("Segoe UI", 20, "bold"), bg="white", fg="#2c3e50", bd=2, relief="groove"
    )
    delete_item_frame.pack(fill="x", padx=20, pady=(20, 10), ipadx=10, ipady=10)

    # === שורת שליטה ===
    tk.Label(delete_item_frame, text="🔎 Enter The SKU:", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#34495e").grid(row=0, column=0, padx=10, pady=8, sticky="w")

    entry_sku = ttk.Entry(delete_item_frame, font=("Segoe UI", 13), width=28)
    entry_sku.grid(row=0, column=1, padx=10, pady=8, sticky="w")

    btn_scan = tk.Button(delete_item_frame, text="📷 QR Scanner", command=scan_and_fill_sku,
                         bg="#9b59b6", fg="white", font=("Segoe UI", 13), relief="flat", cursor="hand2")
    btn_scan.grid(row=0, column=2, padx=10, pady=8, sticky="w")

    btn_hide = tk.Button(delete_item_frame, text="🚫 הסתר פריט", command=update_item_visibility,
                         bg="#e74c3c", fg="white", font=("Segoe UI", 13), relief="flat", cursor="hand2")
    btn_hide.grid(row=0, column=3, padx=10, pady=8, sticky="w")

    btn_restore = tk.Button(delete_item_frame, text="♻️ החזר פריט פעיל", command=restore_selected_item,
                            bg="#2ecc71", fg="white", font=("Segoe UI", 13), relief="flat", cursor="hand2")
    btn_restore.grid(row=0, column=4, padx=10, pady=8, sticky="w")

    show_hidden_var = tk.BooleanVar()
    show_hidden_checkbox = ttk.Checkbutton(
        delete_item_frame, text="הצג גם פריטים מוסתרים",
        variable=show_hidden_var, command=refresh_items_table
    )
    show_hidden_checkbox.grid(row=0, column=5, padx=10, pady=8, sticky="w")

    # === בחירת סניף ===
    tk.Label(delete_item_frame, text="📍 בחר סניף:", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#34495e").grid(row=1, column=0, padx=10, pady=8, sticky="w")

    branch_var = tk.StringVar()
    branch_combobox = ttk.Combobox(delete_item_frame, textvariable=branch_var,
                                   font=("Segoe UI", 13), width=28, state="readonly")
    branch_combobox.grid(row=1, column=1, padx=10, pady=8, sticky="w")

    def load_branches():
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("SELECT branch_id, branch_name FROM branches")
            branches = cursor.fetchall()
            branch_list = [f"{branch_id} - {branch_name}" for branch_id, branch_name in branches]
            branch_combobox['values'] = branch_list
            if branch_list:
                branch_combobox.current(0)
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת סניפים: {e}")
        finally:
            if connection:
                connection.close()

    load_branches()
    branch_combobox.bind("<<ComboboxSelected>>", lambda e: refresh_items_table())

    # === טבלת פריטים ===
    columns = ("SKU", "Item_name", "Quantity", "Status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background="#ffffff",
                    foreground="#2c3e50",
                    fieldbackground="#ffffff",
                    rowheight=30,
                    font=("Segoe UI", 13))
    style.configure("Custom.Treeview.Heading",
                    background="#34495e",
                    foreground="white",
                    font=("Segoe UI", 14, "bold"))
    style.map("Custom.Treeview", background=[("selected", "#d0ebff")])

    tree.configure(style="Custom.Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=130)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

    # === תגיות צבעוניות לפי סטטוס ===
    tree.tag_configure("active", background="#e6ffe6")
    tree.tag_configure("inactive", background="#ffe6e6")
    tree.tag_configure("scanned", background="#fffac8")

    refresh_items_table()
def open_search_item_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()


    def search_items(event=None):
        branch = combo_branch.get()  # הסניף הנבחר
        status = combo_status.get()
        sku = entry_sku.get().strip()
        name = entry_name.get().strip()
        category = entry_category.get().strip()

        query = """
            SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, 
                   inventory.price, inventory.color, inventory.size, inventory.shelf_row, inventory.shelf_column, 
                   branches.branch_name, branches.branch_address, inventory.image_path
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
        if status == "Available":
            query += " AND inventory.is_active = 1"
        elif status == "Unavailable":
            query += " AND inventory.is_active = 0"

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
                f"סניף: {values[9]}",
                f"כתובת: {values[10]}"
            ]

            for d in details:
                tk.Label(top, text=d, bg="white", font=("Arial", 11)).pack(pady=2)

    def show_warehouse_map():
        selected_branch = combo_branch.get()
        if not selected_branch or selected_branch == "בחר סניף":
            messagebox.showwarning("שים לב", "יש לבחור סניף לפני הצגת מפת המחסן")
            return

        skus_to_highlight = []
        for child in tree.get_children():
            values = tree.item(child, 'values')
            if values:
                skus_to_highlight.append(values[0])

        Warehouse_Map(branch_address=selected_branch, highlight_skus=skus_to_highlight)

    def scan_and_fill_sku():
        scanned = scan_qr_code()
        if scanned:
            entry_sku.delete(0, tk.END)
            entry_sku.insert(0, scanned)
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

    # === מסגרת טופס ראשית ===
    form_frame = tk.Frame(tree_frame, bg="white", bd=2, relief="groove")
    form_frame.pack(pady=15, padx=20, fill="x")

    def create_entry(parent, label_text, row, col):
        label = tk.Label(parent, text=label_text, font=("Segoe UI", 14, "bold"), bg="white", anchor="w")
        label.grid(row=row, column=col, padx=5, pady=5, sticky="w")
        entry = tk.Entry(parent, bd=2, relief="groove", font=("Segoe UI", 14), width=22)
        entry.grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")
        return entry

    # === שדות חיפוש ===
    entry_sku = create_entry(form_frame, "🔎 SKU:", 1, 0)
    entry_name = create_entry(form_frame, "📦 Item Name:", 0, 2)
    entry_category = create_entry(form_frame, "🏷️ Category:", 1, 2)

    # === סניף ===
    tk.Label(form_frame, text="🏬 Select Branch:", font=("Segoe UI", 14, "bold"),
             bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

    combo_branch = ttk.Combobox(form_frame, state="readonly", font=("Segoe UI", 14), width=20)
    combo_branch.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # === זמינות ===
    tk.Label(form_frame, text="✅ Availability:", font=("Segoe UI", 14, "bold"),
             bg="white").grid(row=0, column=4, padx=5, pady=5, sticky="w")

    combo_status = ttk.Combobox(form_frame, values=["All", "Available", "Unavailable"],
                                state="readonly", font=("Segoe UI", 14), width=20)
    combo_status.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    combo_status.current(0)

    # === סריקת QR + חיפוש ===
    btn_qr_scan = tk.Button(form_frame, text="📷 QR Scanner", command=scan_and_fill_sku,
                            bg="#9b59b6", fg="white", font=("Segoe UI", 13), relief="flat", cursor="hand2")
    btn_qr_scan.grid(row=1, column=4, padx=5, pady=5, sticky="w")

    search_button = tk.Button(form_frame, text="🔍 Search", command=search_items,
                              bg="#2ecc71", fg="white", font=("Segoe UI", 13), relief="flat", cursor="hand2")
    search_button.grid(row=1, column=5, padx=5, pady=5, sticky="w")

    # === מפת מחסן ===
    btn_map = tk.Button(form_frame, text="🔍 warehouse Map", command=show_warehouse_map,
                              bg="#2ecc71", fg="white", font=("Segoe UI", 13), relief="flat", cursor="hand2")
    btn_map.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    # === טעינת סניפים מהמסד ===
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT branch_address FROM branches")
        branches = cursor.fetchall()
        combo_branch['values'] = [b[0] for b in branches]
    except mysql.connector.Error as e:
        messagebox.showerror("שגיאה", f"שגיאה בהבאת סניפים: {e}")
    finally:
        if connection:
            connection.close()

    # === חיבורים לחיפוש ===
    combo_branch.bind("<<ComboboxSelected>>", search_items)
    combo_status.bind("<<ComboboxSelected>>", search_items)
    entry_sku.bind("<KeyRelease>", search_items)
    entry_name.bind("<KeyRelease>", search_items)
    entry_category.bind("<KeyRelease>", search_items)

    # === טבלת נתונים ===
    columns = ("SKU", "item_name", "category", "quantity", "price",
               "color", "size", "shelf_row", "shelf_column", "branch_name", "branch_address")

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview", font=("Segoe UI", 13), rowheight=30, background="#ffffff")
    style.configure("Custom.Treeview.Heading", font=("Segoe UI", 14, "bold"), background="#34495e", foreground="white")
    style.map("Custom.Treeview", background=[("selected", "#d0ebff")])

    tree.configure(style="Custom.Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    tree.tag_configure('oddrow', background="white")
    tree.tag_configure('evenrow', background="#f0f8ff")

    tree.pack(pady=10, padx=20, fill="both", expand=True)

    # === תצוגת תמונה ===
    image_label = tk.Label(tree_frame, bg="white", bd=2, relief="groove")
    image_label.pack(pady=10)

    # === סטטוס ===
    status_label = tk.Label(tree_frame, text="", font=("Segoe UI", 14, "italic"), fg="gray", bg="#f5f6fa")
    status_label.pack(pady=5)

    # === אירועים לעץ ===
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    tree.bind("<Double-1>", show_item_details)

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
    # ניקוי חלון קיים
    for widget in tree_frame.winfo_children():
        widget.destroy()

    # === מסגרות עיקריות ===
    filter_frame = tk.Frame(tree_frame, bg="white")
    filter_frame.pack(fill="x", padx=10, pady=(10, 20))

    table_frame = tk.Frame(tree_frame, bg="white", bd=1, relief="solid")
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    summary_frame = tk.Frame(tree_frame, bg="white")
    summary_frame.pack(fill="x", pady=10)

    # === שליפת סניפים ===
    # === שליפת סניפים ===
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT branch_id, branch_name FROM branches")
    branches = cur.fetchall()
    branch_dict = {name: bid for bid, name in branches}
    cur.close()
    conn.close()

    # === רכיבי סינון ===
    tk.Label(filter_frame, text=":בחר סניף📍", font=("Segoe UI", 14, "bold"), bg="white").pack(side="right", padx=10, pady=5)
    branch_combo = ttk.Combobox(filter_frame, values=list(branch_dict.keys()), width=25, font=("Segoe UI", 12),
                                state="readonly")
    branch_combo.pack(side="right", padx=10, pady=5)

    tk.Label(filter_frame, text=":קטגוריה🏷️", font=("Segoe UI", 14, "bold"), bg="white").pack(side="right", padx=10, pady=5)
    category_combo = ttk.Combobox(filter_frame, values=["כל הקטגוריות"], width=18,
                                  font=("Segoe UI", 11), state="readonly")
    category_combo.set("כל הקטגוריות")
    category_combo.pack(side="right", padx=10, pady=5)

    tk.Label(filter_frame, text=":מתאריך📅", font=("Segoe UI", 14, "bold"), bg="white").pack(side="right", padx=10, pady=5)
    start_date = DateEntry(filter_frame, date_pattern="yyyy-mm-dd", font=("Segoe UI", 12))
    start_date.set_date(date.today())
    start_date.pack(side="right", padx=10, pady=5)

    tk.Label(filter_frame, text=":עד תאריך📅", font=("Segoe UI", 14, "bold"), bg="white").pack(side="right", padx=10, pady=5)
    end_date = DateEntry(filter_frame, date_pattern="yyyy-mm-dd", font=("Segoe UI", 12))
    end_date.set_date(date.today())
    end_date.pack(side="right", padx=10, pady=5)

    # === פונקציה לעדכון קטגוריות לפי סניף ===
    def update_categories_by_branch(event=None):
        selected_branch = branch_combo.get()
        if not selected_branch:
            return
        branch_id = branch_dict.get(selected_branch)

        try:
            conn = connect_to_database()
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT category 
                FROM inventory 
                WHERE branch_id = %s AND category IS NOT NULL AND category <> ''
            """, (branch_id,))
            categories = [row[0] for row in cur.fetchall()]
            categories.insert(0, "כל הקטגוריות")
            category_combo['values'] = categories
            category_combo.set("כל הקטגוריות")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליפת קטגוריות: {e}")
        finally:
            if conn:
                conn.close()

    # === קישור שינוי סניף לאירוע עדכון קטגוריות ===
    branch_combo.bind("<<ComboboxSelected>>", update_categories_by_branch)

    # === פונקציית הצגת גרף רווח/הוצאה ===
    def show_chart(income, expense):
        labels = ["רווחים", "הוצאות"]
        values = [income, expense]
        colors = ['#4CAF50', '#F44336']
        plt.figure(figsize=(5, 4))
        plt.bar(labels, values, color=colors)
        plt.title("רווח מול הוצאה")
        plt.ylabel('₪')
        plt.show()

    # === סינון והצגת הכנסות בלבד ===
    def filter_income():
        tree.delete(*tree.get_children())
        summary_var.set("")

        branch_name = branch_combo.get()
        category_filter = category_combo.get()
        if not branch_name:
            messagebox.showerror("שגיאה", "בחר סניף חוקי.")
            return

        s_date = start_date.get_date()
        e_date = end_date.get_date()

        conn = connect_to_database()
        cur = conn.cursor(buffered=True)
        income = 0

        try:
            branch_id = branch_dict[branch_name]

            cur.execute("""
                SELECT purchase_date, item_name, total_price
                FROM purchases 
                WHERE branch_name = %s AND purchase_date BETWEEN %s AND %s
            """, (branch_name, s_date, e_date))
            rows = cur.fetchall()

            for date_p, item, price in rows:
                cur.execute("SELECT category FROM inventory WHERE item_name = %s AND branch_id = %s", (item, branch_id))
                res = cur.fetchone()
                item_category = res[0] if res else "לא ידוע"

                if category_filter != "כל הקטגוריות" and item_category != category_filter:
                    continue

                income += price
                tree.insert("", "end", values=("הכנסה", date_p.strftime("%Y-%m-%d"), item, item_category,
                                               f"{price:.2f} ₪", branch_name), tags=("income",))

            summary_var.set(f"סה\"כ רווחים: {income:.2f} ₪ | הוצאות: 0 ₪ | קופה נטו: {income:.2f} ₪")
            show_chart(income, 0)

        except Exception as e:
            messagebox.showerror("שגיאה", str(e))
        finally:
            cur.close()
            conn.close()

    # === סינון והצגת הוצאות בלבד ===
    def filter_expense():
        tree.delete(*tree.get_children())
        summary_var.set("")

        branch_name = branch_combo.get()
        category_filter = category_combo.get()
        if not branch_name:
            messagebox.showerror("שגיאה", "בחר סניף חוקי.")
            return

        s_date = start_date.get_date()
        e_date = end_date.get_date()

        conn = connect_to_database()
        cur = conn.cursor(buffered=True)
        expense = 0

        try:
            branch_id = branch_dict[branch_name]

            cur.execute("""
                SELECT e.expense_date, e.item_name, e.total_cost
                FROM expenses e
                JOIN branches b ON e.branch_id = b.branch_id
                WHERE b.branch_name = %s AND e.expense_date BETWEEN %s AND %s
            """, (branch_name, s_date, e_date))
            rows = cur.fetchall()

            for date_e, item, cost in rows:
                cur.execute("SELECT category FROM inventory WHERE item_name = %s AND branch_id = %s", (item, branch_id))
                res = cur.fetchone()
                item_category = res[0] if res else "לא ידוע"

                if category_filter != "כל הקטגוריות" and item_category != category_filter:
                    continue

                expense += cost
                tree.insert("", "end", values=("הוצאה", date_e.strftime("%Y-%m-%d"), item, item_category,
                                               f"{cost:.2f} ₪", branch_name), tags=("expense",))

            summary_var.set(f"סה\"כ רווחים: 0 ₪ | הוצאות: {expense:.2f} ₪ | קופה נטו: -{expense:.2f} ₪")
            show_chart(0, expense)

        except Exception as e:
            messagebox.showerror("שגיאה", str(e))
        finally:
            cur.close()
            conn.close()

    # === איפוס סינונים ===
    def reset_filters():
        branch_combo.set("")
        category_combo.set("כל הקטגוריות")
        start_date.set_date(date.today())
        end_date.set_date(date.today())
        tree.delete(*tree.get_children())
        summary_var.set("")
        show_total_summary()  # או show_financial_data() אם ברירת המחדל לפי סניף

    # === הצגת הכנסות והוצאות ביחד עם סינון לפי סניף ===
    def show_financial_data():
        tree.delete(*tree.get_children())
        summary_var.set("")

        branch_name = branch_combo.get()
        category_filter = category_combo.get()
        if not branch_name:
            messagebox.showerror("שגיאה", "בחר סניף חוקי.")
            return

        s_date = start_date.get_date()
        e_date = end_date.get_date()

        conn = connect_to_database()
        cur = conn.cursor(buffered=True)  # ✅ חשוב מאוד!

        income = 0
        expense = 0

        try:
            branch_id = branch_dict[branch_name]

            # === הכנסות ===
            cur.execute("""
                SELECT purchase_date, item_name, total_price, branch_name
                FROM purchases 
                WHERE branch_name = %s AND purchase_date BETWEEN %s AND %s
            """, (branch_name, s_date, e_date))

            income_rows = cur.fetchall()

            for date_p, item, price, branch in income_rows:
                cur.execute("SELECT category FROM inventory WHERE item_name = %s AND branch_id = %s", (item, branch_id))
                res = cur.fetchone()
                item_category = res[0] if res else "לא ידוע"

                if category_filter != "כל הקטגוריות" and item_category != category_filter:
                    continue

                income += price
                tree.insert("", "end", values=("הכנסה", date_p.strftime("%Y-%m-%d"), item, item_category,
                                               f"{price:.2f} ₪", branch), tags=("income",))

            # === הוצאות ===
            cur.execute("""
                SELECT e.expense_date, e.item_name, e.total_cost, b.branch_name
                FROM expenses e 
                JOIN branches b ON e.branch_id = b.branch_id
                WHERE b.branch_name = %s AND e.expense_date BETWEEN %s AND %s
            """, (branch_name, s_date, e_date))

            expense_rows = cur.fetchall()

            for date_e, item, cost, branch in expense_rows:
                cur.execute("SELECT category FROM inventory WHERE item_name = %s AND branch_id = %s", (item, branch_id))
                res = cur.fetchone()
                item_category = res[0] if res else "לא ידוע"

                if category_filter != "כל הקטגוריות" and item_category != category_filter:
                    continue

                expense += cost
                tree.insert("", "end", values=("הוצאה", date_e.strftime("%Y-%m-%d"), item, item_category,
                                               f"{cost:.2f} ₪", branch), tags=("expense",))

            net = income - expense
            summary_var.set(f"סה\"כ רווחים: {income:.2f} ₪ | הוצאות: {expense:.2f} ₪ | קופה נטו: {net:.2f} ₪")
            show_chart(income, expense)

        except Exception as e:
            messagebox.showerror("שגיאה", str(e))
        finally:
            cur.close()
            conn.close()

    # === הצגת סיכום כללי ללא סינון סניף ===
    def show_total_summary():
        tree.delete(*tree.get_children())
        summary_var.set("")

        s_date = start_date.get_date()
        e_date = end_date.get_date()
        selected_category = category_combo.get()

        conn = connect_to_database()
        cur = conn.cursor(buffered=True)
        income = 0
        expense = 0

        try:
            # === הכנסות ===
            cur.execute("""
                SELECT p.purchase_date, p.item_name, p.total_price, b.branch_name, i.category
                FROM purchases p
                JOIN inventory i ON p.item_name = i.item_name AND p.branch_id = i.branch_id
                JOIN branches b ON p.branch_id = b.branch_id
                WHERE p.purchase_date BETWEEN %s AND %s
            """, (s_date, e_date))
            income_rows = cur.fetchall()

            for date_p, item, price, branch_name, category in income_rows:
                if selected_category != "כל הקטגוריות" and category != selected_category:
                    continue
                income += price
                tree.insert("", "end",
                            values=(
                            "הכנסה", date_p.strftime("%Y-%m-%d"), item, category, f"{price:.2f} ₪", branch_name),
                            tags=("income",))

            # === הוצאות ===
            cur.execute("""
                SELECT e.expense_date, e.item_name, e.total_cost, b.branch_name, i.category
                FROM expenses e
                JOIN branches b ON e.branch_id = b.branch_id
                JOIN inventory i ON e.item_name = i.item_name AND e.branch_id = i.branch_id
                WHERE e.expense_date BETWEEN %s AND %s
            """, (s_date, e_date))
            expense_rows = cur.fetchall()

            for date_e, item, cost, branch_name, category in expense_rows:
                if selected_category != "כל הקטגוריות" and category != selected_category:
                    continue
                expense += cost
                tree.insert("", "end",
                            values=("הוצאה", date_e.strftime("%Y-%m-%d"), item, category, f"{cost:.2f} ₪", branch_name),
                            tags=("expense",))

            net = income - expense
            summary_var.set(f"רווח כולל: {income:.2f} ₪ | הוצאה כוללת: {expense:.2f} ₪ | קופה כוללת: {net:.2f} ₪")
            show_chart(income, expense)

        except Exception as e:
            messagebox.showerror("שגיאה", str(e))
        finally:
            cur.close()
            conn.close()

    # === ייצוא לאקסל ===
    def export_to_excel():
        rows = [tree.item(child)["values"] for child in tree.get_children()]
        if not rows:
            messagebox.showwarning("שגיאה", "אין נתונים לייצוא.")
            return

        df = pd.DataFrame(rows, columns=["סוג", "תאריך", "שם פריט", "קטגוריה", "סכום", "סניף"])
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("הצלחה", f"הקובץ נשמר:\n{file_path}")


    tk.Button(summary_frame, text="✅רק הכנסות", command=filter_income,
              bg="#2ecc71", fg="white", font=("Segoe UI", 12), relief="flat").pack(side="right", padx=10, pady=5)

    tk.Button(summary_frame, text="📉רק הוצאות", command=filter_expense,
              bg="#e74c3c", fg="white", font=("Segoe UI", 12), relief="flat").pack(side="right", padx=10, pady=5)

    tk.Button(summary_frame, text="🔄איפוס", command=reset_filters,
              bg="#95a5a6", fg="white", font=("Segoe UI", 12), relief="flat").pack(side="right", padx=10, pady=5)

    tk.Button(summary_frame, text="📊הצג", command=show_financial_data,
              bg="#3498db", fg="white", font=("Segoe UI", 12), relief="flat").pack(side="right", padx=10, pady=5)

    tk.Button(summary_frame, text="📃סיכום כללי", command=show_total_summary,
              bg="#9b59b6", fg="white", font=("Segoe UI", 12), relief="flat").pack(side="right", padx=10, pady=5)

    # === משתנה סיכום ===
    summary_var = tk.StringVar()
    tk.Label(summary_frame, textvariable=summary_var, font=("Segoe UI", 14, "bold"),
             fg="blue", bg="#f5f6fa").pack()

    tk.Button(summary_frame, text="📤 ייצוא ל-Excel", command=export_to_excel,
              bg="#27ae60", fg="white", font=("Segoe UI", 12), relief="flat").pack(pady=5)

    # === טבלת נתונים ===
    columns = ("type", "date", "item", "category", "amount", "branch")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    # עיצוב הטבלה
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    font=("Segoe UI", 12),
                    rowheight=30,
                    background="white",
                    fieldbackground="white")
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 13, "bold"),
                    background="#34495e",
                    foreground="white")
    style.map("Treeview", background=[("selected", "#d6eaf8")])

    tree.tag_configure("income", background="#eafaf1")
    tree.tag_configure("expense", background="#fdecea")

    for col, name in zip(columns, ["סוג", "תאריך", "פריט", "קטגוריה", "סכום", "סניף"]):
        tree.heading(col, text=name)
        tree.column(col, anchor="center", width=140)

    tree.pack(fill="both", expand=True)