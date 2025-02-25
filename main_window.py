import tkinter as tk
from tkinter import ttk
from inventory import view_inventory, open_add_item_window , open_search_item_window, open_update_item_window, open_report_window, open_delete_item_window, open_purchase_window


# פתיחת חלון ראשי
def open_main_window(user_type):
    global tree_frame
    main_window = tk.Tk()
    main_window.title("מערכת לניהול מלאי")
    main_window.geometry("800x600")
    main_window.config(bg="#34495e")

    title_label = ttk.Label(main_window, text=f"התחברות - {user_type}", font=("Arial", 18, "bold"), background="#34495e", foreground="#2c3e50")
    title_label.pack(pady=10)

    tree_frame = tk.Frame(main_window, bg="#f4f4f4")
    tree_frame.pack(side="right", fill="both", expand=True)

    sidebar = tk.Frame(main_window, width=200, bg="#2d3436", height=600, relief="sunken")
    sidebar.pack(side="left", fill="y")

    def create_sidebar_button(text, command):
        button = tk.Button(sidebar, text=text, bg="#34495e", fg="White", font=("Arial", 14), command=command)
        button.pack(fill="x", padx=10, pady=10)
        return button

    if user_type == "admin":
        create_sidebar_button("Add Item",lambda: open_add_item_window(tree_frame))
        create_sidebar_button("Update Item",lambda: open_update_item_window(tree_frame))
        create_sidebar_button("Delete Item",lambda: open_delete_item_window(tree_frame))
        create_sidebar_button("Search Item",lambda: open_search_item_window(tree_frame))
        create_sidebar_button("View Inventory",lambda: view_inventory(tree_frame))
        create_sidebar_button("Generating Reports",lambda: open_report_window(tree_frame))
    elif user_type == "worker":
        create_sidebar_button("View Inventory",lambda: view_inventory(tree_frame))
        create_sidebar_button("Update Item",lambda: open_update_item_window(tree_frame))
        create_sidebar_button("Search Item",lambda: open_search_item_window(tree_frame))
        create_sidebar_button("Generating Reports",lambda: open_report_window(tree_frame))
    elif user_type == "customer":
        create_sidebar_button("View Inventory",lambda: view_inventory(tree_frame))
        create_sidebar_button("Purchase Item",lambda: open_purchase_window(tree_frame))

    create_sidebar_button("Exit", lambda: return_to_login(main_window))

    main_window.mainloop()


def return_to_login(current_window):
    from login import create_login_window
    current_window.destroy()
    create_login_window()


#ahmed1