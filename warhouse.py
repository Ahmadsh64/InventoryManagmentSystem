import tkinter as tk
from tkinter import messagebox
import mysql.connector

CELL_WIDTH = 10  # רוחב הכפתור בטקסט (מספר תווים)
CELL_HEIGHT = 3  # גובה הכפתור (מספר שורות טקסט)
BLOCK_SPACING = 10
TOP_MARGIN = 50
LEFT_MARGIN = 50
GRID_SIZE = 10
zones = [chr(i) for i in range(ord("A"), ord("J")+1)]  # אזורים A-J

root = None
current_zone_index = 0
buttons = {}  # מאגר כפתורים לפי מיקום

view_state = {
    "mode": "column",
    "zone": zones[0],
    "zone_index": 0,
    "selected_sku": None  # פריט מסומן אם יש
}

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="inventory_system"
    )

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

def on_button_click(row, col):
    # קבלת מידע על הכפתור שנלחץ
    zone = view_state["zone"]
    inventory_data = get_inventory_by_zone(zone)
    inventory_map = {(item['shelf_row'], item['shelf_column']): item for item in inventory_data}

    item = inventory_map.get((row, col))
    if item:
        # אם יש פריט במיקום הזה - הצגת מידע
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
        # מדף פנוי - למשל אפשר להציג חלון להוספת פריט חדש
        messagebox.showinfo("Empty Shelf", f"Shelf {zone}-{row}-{col} is empty. You can add an item here.")

def draw_grid_view_with_buttons(parent_frame, zone, item_sku=None):
    # נקה את תכולת המסגרת קודם
    for widget in parent_frame.winfo_children():
        widget.destroy()

    inventory_data = get_inventory_by_zone(zone)
    inventory_map = {(item['shelf_row'], item['shelf_column']): item for item in inventory_data}

    buttons.clear()

    for row in range(1, GRID_SIZE+1):
        for col in range(1, GRID_SIZE+1):
            item = inventory_map.get((row, col))
            btn_text = f"{zone}-{row:02}-{col:02}"
            state = tk.NORMAL
            bg_color = "white"

            if item:
                # צבע לפי מלאי
                if item['sku'] == item_sku:
                    bg_color = "yellow"
                    state = tk.NORMAL  # הפריט המסומן פעיל
                else:
                    # כפתור לא פעיל למלאים אחרים
                    state = tk.DISABLED
                    if item['quantity'] > 100:
                        bg_color = "lightgreen"
                    elif item['quantity'] >= 1:
                        bg_color = "orange"
                    else:
                        bg_color = "red"

                btn_text = f"{item['item_name']}\nQty: {item['quantity']}"
            else:
                # מדף פנוי
                bg_color = "white"
                state = tk.NORMAL

            btn = tk.Button(
                parent_frame,
                text=btn_text,
                width=CELL_WIDTH,
                height=CELL_HEIGHT,
                bg=bg_color,
                state=state,
                command=lambda r=row, c=col: on_button_click(r, c)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            buttons[(row, col)] = btn

def create_window():
    global root
    root = tk.Tk()
    root.title("Warehouse Map - Grid Buttons View")

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    # נניח שאנחנו במצב רשת אזור A, וללא פריט מסומן
    draw_grid_view_with_buttons(frame, zone=zones[0], item_sku=None)

    root.mainloop()

if __name__ == "__main__":
    create_window()
