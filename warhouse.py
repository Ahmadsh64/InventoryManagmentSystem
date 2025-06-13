import tkinter as tk
from functools import partial
from tkinter import messagebox
import mysql.connector
# יצירת חלון ראשי
def create_window():
    global root, canvas
    root = tk.Tk()
    root.title("Warehouse Map - Columns/Grid View")

    canvas_width = LEFT_MARGIN * 2 + (CELL_WIDTH + BLOCK_SPACING) * len(zones)
    canvas_height = TOP_MARGIN * 2 + CELL_HEIGHT * GRID_SIZE + 100
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    draw_column_view(canvas)

    root.mainloop()



# הגדרות תצוגה
CELL_WIDTH = 50
CELL_HEIGHT = 30
BLOCK_SPACING = 30
TOP_MARGIN = 50
LEFT_MARGIN = 50
GRID_SIZE = 10

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
def get_inventory_by_zone(zone):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT shelf_zone, shelf_row, shelf_column, sku, item_name, quantity, color, size
    FROM inventory
    WHERE shelf_zone = %s 
    """
    cursor.execute(query, (zone,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# משתנים גלובליים
root = None
current_zone_index = 0
cells = {}

view_state = {
    "mode": "column",
    "zone": zones[0],
    "zone_index": 0
}
def get_items_by_order(order_id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        inv.shelf_zone, inv.shelf_row, inv.shelf_column,
        inv.item_name, inv.quantity, inv.color, inv.size, inv.sku
    FROM order_items oi
    JOIN inventory inv ON oi.sku = inv.sku
    WHERE oi.order_id = %s
    """
    cursor.execute(query, (order_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# ציור מצב עמודות
def draw_column_view(cnv):
    cnv.delete("all")
    for zone_index, zone in enumerate(zones):
        block_x = LEFT_MARGIN + zone_index * (CELL_WIDTH + BLOCK_SPACING)
        inventory_data = get_inventory_by_zone(zone)
        inventory_map = {(item['shelf_row'], item['shelf_column']): item for item in inventory_data}

        for row in range(1, GRID_SIZE+1):
            x1 = block_x
            y1 = TOP_MARGIN + (row-1)*CELL_HEIGHT
            x2 = x1 + CELL_WIDTH
            y2 = y1 + CELL_HEIGHT

            item = inventory_map.get((row, 1))  # עמודה 1 בלבד במצב עמודות
            fill_color = "white"
            text = f"{zone}-{row:02}"

            if item:
                fill_color = "lightgreen" if item['quantity'] > 100 else "yellow" if item['quantity'] >= 1 else "red"
                text = f"{item['item_name']}\nQty:{item['quantity']}"

            cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
            cnv.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Arial", 7))

        # תווית אזור עם מעבר למצב רשת בלחיצה
        label_id = cnv.create_text(block_x + CELL_WIDTH // 2, TOP_MARGIN + 10 * CELL_HEIGHT + 20,
                                   text=zone, font=("Arial", 10, "bold"), fill="blue")
        canvas.tag_bind(label_id, "<Button-1>", lambda e, z=zone: switch_to_grid_view(z, canvas))

    remove_navigation_buttons()

# ציור מצב רשת
def draw_grid_view(cnv, zone, page_index):
    global canvas  # ודא שזה נמצא כאן
    cnv.delete("all")
    inventory_data = get_inventory_by_zone(zone)
    inventory_map = {(item['shelf_row'], item['shelf_column']): item for item in inventory_data}

    cells.clear()

    for row in range(1, GRID_SIZE+1):
        for col in range(1, GRID_SIZE+1):
            x1 = LEFT_MARGIN + (col-1)*CELL_WIDTH
            y1 = TOP_MARGIN + (row-1)*CELL_HEIGHT
            x2 = x1 + CELL_WIDTH
            y2 = y1 + CELL_HEIGHT

            item = inventory_map.get((row, col))
            fill_color = "white"
            text = f"{zone}-{row:02}-{col:02}"

            if item:
                fill_color = "lightgreen" if item['quantity'] > 100 else "yellow" if item['quantity'] >= 1 else "red"
                text = f"{item['item_name']}\nQty:{item['quantity']}"

            rect_id = cnv.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
            text_id = cnv.create_text((x1 + x2)//2, (y1 + y2)//2, text=text, font=("Arial", 8), justify="center")

            cells[rect_id] = item
            cells[text_id] = item

            cnv.tag_bind(rect_id, "<Button-1>", on_cell_click)
            cnv.tag_bind(text_id, "<Button-1>", on_cell_click)

    cnv.create_text(cnv.winfo_reqwidth() // 2, TOP_MARGIN // 2, text=f"Zone: {zone}", font=("Arial", 16, "bold"))

    create_navigation_buttons()

# כפתורי ניווט במצב רשת
def create_navigation_buttons():
    remove_navigation_buttons()

    btn_frame = tk.Frame(root)
    btn_frame.pack()
    btn_frame._custom_buttons = True  # לסימון לזהות ולמחוק בעתיד

    tk.Button(btn_frame, text="← Prev", command=grid_prev_zone).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Back to Columns", command=lambda: draw_column_view(canvas)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Next →", command=grid_next_zone).pack(side=tk.LEFT, padx=10)

# ניקוי כפתורי ניווט
def remove_navigation_buttons():
    if root is None:
        return

    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame) and hasattr(widget, "_custom_buttons"):
            widget.destroy()


# מעבר למצב רשת
def switch_to_grid_view(zone, cnv):
    global current_zone_index
    view_state["mode"] = "grid"
    view_state["zone"] = zone
    view_state["zone_index"] = zones.index(zone)
    current_zone_index = view_state["zone_index"]
    draw_grid_view(cnv, zone, current_zone_index)

# ניווט אזורים במצב רשת
def grid_prev_zone():
    global current_zone_index
    if current_zone_index > 0:
        current_zone_index -= 1
        draw_grid_view(canvas, zones[current_zone_index], current_zone_index)

def grid_next_zone():
    global current_zone_index
    if current_zone_index < len(zones) - 1:
        current_zone_index += 1
        draw_grid_view(canvas, zones[current_zone_index], current_zone_index)

def on_zone_click(event, zone):
    switch_to_grid_view(zone)

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

# הרצת התוכנית
if __name__ == "__main__":
    create_window()