import tkinter as tk
from tkinter import messagebox
import mysql.connector

# הגדרות תצוגה
CELL_WIDTH = 50
CELL_HEIGHT = 30
BLOCK_SPACING = 30
TOP_MARGIN = 50
LEFT_MARGIN = 50
GRID_SIZE = 10
ENTRANCE_COORDINATES = (LEFT_MARGIN - 80, TOP_MARGIN + CELL_HEIGHT * 9)

zones = [chr(i) for i in range(ord("A"), ord("J")+1)]  # אזורים A-J

# חיבור למסד הנתונים
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="inventory_system"
    )

# שליפת נתונים לפי אזור
def get_inventory_by_zone(zone, branch_address=None):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT shelf_zone, shelf_row, shelf_column, sku, item_name, quantity, color, size, is_active
    FROM inventory i
    JOIN branches b ON i.branch_id = b.branch_id
    WHERE shelf_zone = %s 
    """
    params = [zone]

    if branch_address:
        query += " AND b.branch_address = %s"
        params.append(branch_address)

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# משתנים גלובליים
root = None
canvas = None
current_zone_index = 0
cells = {}

view_state = {
    "mode": "column",
    "zone": zones[0],
    "zone_index": 0,
    "branch_address": None  # ⬅️ עדיין ריק, יתעדכן אחר כך
}

# ציור מצב עמודות
def draw_column_view(cnv, branch_address=None):
    cnv.delete("all")
    for zone_index, zone in enumerate(zones):
        block_x = LEFT_MARGIN + zone_index * (CELL_WIDTH + BLOCK_SPACING)
        inventory_data = get_inventory_by_zone(zone, branch_address)
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
                # 🟡 סימון אם הפריט ברשימת הפריטים המסומנים
                if item['sku'] in view_state.get("highlight_skus", []):
                    fill_color = "gold"
                elif not item['is_active'] or item['quantity'] == 0:
                    fill_color = "red"
                elif item['quantity'] >= 50:
                    fill_color = "lightgreen"
                elif item['quantity'] > 10:
                    fill_color = "yellow"
                else:
                    fill_color = "orange"

                text = f"{item['item_name']}\nQty:{item['quantity']}"

            cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
            cnv.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Arial", 7))

        # 🔵 תווית אזור עם קישור למצב רשת
        label_id = cnv.create_text(block_x + CELL_WIDTH // 2, TOP_MARGIN + 10 * CELL_HEIGHT + 20,
                                   text=zone, font=("Arial", 10, "bold"), fill="blue")
        cnv.tag_bind(label_id, "<Button-1>", lambda e, z=zone: switch_to_grid_view(z))

    remove_navigation_buttons()
    draw_legend()

    ENTRANCE_COORDINATES = (
        LEFT_MARGIN + ((CELL_WIDTH + BLOCK_SPACING) * len(zones)) // 2 - CELL_WIDTH // 2,
        TOP_MARGIN + CELL_HEIGHT * GRID_SIZE + 40
    )
    # ציור כניסה
    # ציור כניסה (במרכז בתחתית)
    entrance_x, entrance_y = ENTRANCE_COORDINATES
    cnv.create_rectangle(entrance_x, entrance_y, entrance_x + CELL_WIDTH, entrance_y + CELL_HEIGHT, fill="blue")
    cnv.create_text(entrance_x + CELL_WIDTH // 2, entrance_y + CELL_HEIGHT // 2, text="כניסה", fill="white")

    # ניווט לפריט
    # ניווט לפריט (ניווט מדויק בין העמודות כמו Waze)
    highlighted_skus = view_state.get("highlight_skus", [])
    if highlighted_skus:
        for zone_index, zone in enumerate(zones):
            inventory_data = get_inventory_by_zone(zone, branch_address)
            for item in inventory_data:
                if item["sku"] in highlighted_skus:
                    row = item["shelf_row"]
                    col = item["shelf_column"]

                    # חישוב מיקום תא הפריט
                    block_x = LEFT_MARGIN + zone_index * (CELL_WIDTH + BLOCK_SPACING)
                    x_item_center = block_x + (CELL_WIDTH // 2)
                    y_item_center = TOP_MARGIN + (row - 1) * CELL_HEIGHT + (CELL_HEIGHT // 2)

                    # נקודת כניסה
                    x_start = ENTRANCE_COORDINATES[0] + CELL_WIDTH // 2
                    y_start = ENTRANCE_COORDINATES[1]

                    # חישוב קו הניווט דרך הנתיב:
                    path_coords = [(x_start, y_start)]

                    # שלב 1: התקדמות אופקית ימינה עד לעמודה לפני האזור הרצוי
                    x_pass_column = block_x - (BLOCK_SPACING // 2)
                    path_coords.append((x_pass_column, y_start))

                    # שלב 2: תנועה אנכית למרכז השורה של הפריט
                    path_coords.append((x_pass_column, y_item_center))

                    # שלב 3: תנועה ימינה פנימה אל תוך המדף
                    path_coords.append((x_item_center, y_item_center))

                    # ציור כל מקטעי המסלול
                    for i in range(len(path_coords) - 1):
                        x1, y1 = path_coords[i]
                        x2, y2 = path_coords[i + 1]
                        cnv.create_line(x1, y1, x2, y2, fill="purple", width=3, dash=(4, 2))


# ציור מצב רשת
def draw_grid_view(cnv, zone, page_index, branch_address=None):
    cnv.delete("all")
    inventory_data = get_inventory_by_zone(zone, branch_address)
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
                if item['sku'] in view_state.get("highlight_skus", []):
                    fill_color = "mediumpurple"  # צבע בולט עבור פריט שמסומן
                elif not item['is_active'] or item['quantity'] == 0:
                    fill_color = "red"
                elif item['quantity'] >= 50:
                    fill_color = "lightgreen"
                elif item['quantity'] > 10:
                    fill_color = "yellow"
                else:
                    fill_color = "orange"

                text = f"{item['item_name']}\nQty:{item['quantity']}"

            rect_id = cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
            text_id = cnv.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=text, font=("Arial", 8))
            cells[rect_id] = item
            cells[text_id] = item
            cnv.tag_bind(rect_id, "<Button-1>", on_cell_click)
            cnv.tag_bind(text_id, "<Button-1>", on_cell_click)

    cnv.create_text(cnv.winfo_reqwidth() // 2, TOP_MARGIN // 2, text=f"Zone: {zone}", font=("Arial", 16, "bold"))
    create_navigation_buttons()
    draw_legend()

# כפתורי ניווט במצב רשת
def create_navigation_buttons():
    remove_navigation_buttons()

    btn_frame = tk.Frame(root)
    btn_frame.pack()
    btn_frame._custom_buttons = True  # לסימון לזהות ולמחוק בעתיד

    tk.Button(btn_frame, text="← Prev", command=grid_prev_zone).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Back to Columns",
              command=lambda: draw_column_view(canvas, view_state["branch_address"])).pack(side=tk.LEFT, padx=10)

    tk.Button(btn_frame, text="Next →", command=grid_next_zone).pack(side=tk.LEFT, padx=10)
# מקרא צבעים
def draw_legend():
    legend_frame = tk.Frame(root, bg="white")
    legend_frame.pack(pady=5)
    legend_frame._legend = True  # מסמן שנוכל להסיר אותו מאוחר יותר

    items = [
        ("lightgreen", "זמין (כמות ≥ 50)"),
        ("yellow", "זמין (כמות < 50)"),
        ("orange", "זמין (כמות ≤ 10)"),
        ("red", "לא זמין או כמות = 0")
    ]

    for color, desc in items:
        color_box = tk.Canvas(legend_frame, width=20, height=20)
        color_box.create_rectangle(0, 0, 20, 20, fill=color)
        color_box.pack(side=tk.LEFT, padx=(10,2))
        label = tk.Label(legend_frame, text=desc, bg="white", font=("Arial", 10))
        label.pack(side=tk.LEFT, padx=(0, 10))

# ניקוי כפתורי ניווט
# ניקוי כפתורי ניווט
def remove_navigation_buttons():
    for widget in root.pack_slaves():
        if isinstance(widget, tk.Frame) and (hasattr(widget, "_custom_buttons") or hasattr(widget, "_legend")):
            widget.destroy()

# מעבר למצב רשת
def switch_to_grid_view(zone):
    global current_zone_index
    view_state["mode"] = "grid"
    view_state["zone"] = zone
    view_state["zone_index"] = zones.index(zone)
    current_zone_index = view_state["zone_index"]
    draw_grid_view(canvas, zones[current_zone_index], current_zone_index, branch_address=view_state["branch_address"])


# ניווט אזורים במצב רשת
def grid_prev_zone():
    global current_zone_index
    if current_zone_index > 0:
        current_zone_index -= 1
        draw_grid_view(canvas, zones[current_zone_index], current_zone_index,
                       branch_address=view_state["branch_address"])


def grid_next_zone():
    global current_zone_index
    if current_zone_index < len(zones) - 1:
        current_zone_index += 1
        draw_grid_view(canvas, zones[current_zone_index], current_zone_index,
                       branch_address=view_state["branch_address"])


# הצגת פרטי פריט בעת לחיצה
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
    else:
        messagebox.showinfo("Info", "No item in this location.")

# יצירת חלון ראשי
def Warehouse_Map(branch_address=None, highlight_skus=None):
    global root, canvas
    root = tk.Tk()
    root.title("Warehouse Map - Columns/Grid View")

    canvas_width = LEFT_MARGIN * 2 + (CELL_WIDTH + BLOCK_SPACING) * len(zones)
    canvas_height = TOP_MARGIN * 2 + CELL_HEIGHT * GRID_SIZE + 100
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    # שמירת כתובת הסניף
    view_state["branch_address"] = branch_address
    view_state["highlight_skus"] = highlight_skus or []
    draw_column_view(canvas, branch_address)



