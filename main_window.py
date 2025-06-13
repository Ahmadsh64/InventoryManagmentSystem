import tkinter as tk
from inventory import (
    view_inventory, open_add_item_window, open_search_item_window,
    open_update_item_window, open_delete_item_window,
    open_purchase_window, open_finance_window)
from reports import open_report_window
from Notifications import refresh_alerts_only, open_alerts_window,Notification_orders
from dashboard import open_dashboard_window

def open_main_window(user_type, user_info):
    main_window = tk.Tk()
    main_window.title("Inventory Management System")
    main_window.geometry("1200x800")  # או כל מידה אחרת שאתה מעדיף
    main_window.configure(bg="#f5f6fa")

    # Sidebar
    sidebar = tk.Frame(main_window, width=220, bg="#1e272e")
    sidebar.pack(side="left", fill="y")


    # Top logo + name
    logo_label = tk.Label(sidebar, text="🌀 StockKeeper", bg="#1e272e", fg="#f5f6fa", font=("Helvetica", 18, "bold"))
    logo_label.pack(pady=30)

    # Main content area
    content_frame = tk.Frame(main_window, bg="#f5f6fa")
    content_frame.pack(side="right", fill="both", expand=True)

    header = tk.Label(content_frame, text=f"Welcome, {user_info[1]} ({user_type.title()})", font=("Helvetica", 20, "bold"), bg="#f5f6fa", fg="#2f3640")
    header.pack(pady=10)

    # Alerts label
    alerts_label = tk.Label(content_frame, text="", font=("Arial", 12, "bold"), bg="#f5f6fa", fg="red")
    alerts_label.pack(anchor="ne", padx=20)

    # Tree Frame
    global tree_frame
    tree_frame = tk.Frame(content_frame, bg="#ffffff", relief="groove")
    tree_frame.pack(fill="both", expand=True)

    # Sidebar buttons
    def create_sidebar_button(text, command, icon=None):
        btn = tk.Button(
            sidebar,
            text=f"{icon}  {text}" if icon else text,
            font=("Helvetica", 14),
            bg="#2f3640",
            fg="white",
            activebackground="#57606f",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            anchor="w",
            command=command
        )
        btn.pack(fill="x", padx=10, pady=5)

    # User-specific buttons
    if user_type == "manager":
        refresh_alerts_only(alerts_label)
        create_sidebar_button("Add Item", lambda: open_add_item_window(tree_frame), "➕")
        create_sidebar_button("Update Item", lambda: open_update_item_window(tree_frame), "✏️")
        create_sidebar_button("Delete Item", lambda: open_delete_item_window(tree_frame), "🗑️")
        create_sidebar_button("Search Item", lambda: open_search_item_window(tree_frame), "🔍")
        create_sidebar_button("View Inventory", lambda: view_inventory(tree_frame), "📦")
        create_sidebar_button("Sales", lambda: Notification_orders(tree_frame), "📦")
        create_sidebar_button("Reports", lambda: open_report_window(tree_frame), "📈")
        create_sidebar_button("Alerts", lambda: open_alerts_window(tree_frame, alerts_label, main_window), "🚨")
        create_sidebar_button("Finance", lambda: open_finance_window(tree_frame), "💰")
        create_sidebar_button(" דשבורד", lambda :open_dashboard_window(tree_frame),"📊")

    elif user_type == "worker":
        create_sidebar_button("View Inventory", lambda: view_inventory(tree_frame), "📦")
        create_sidebar_button("Sales", lambda: Notification_orders(tree_frame), "📦")
        create_sidebar_button("Update Item", lambda: open_update_item_window(tree_frame), "✏️")
        create_sidebar_button("Search Item", lambda: open_search_item_window(tree_frame), "🔍")
        create_sidebar_button("Reports", lambda: open_report_window(tree_frame), "📈")

    elif user_type == "customer":
        create_sidebar_button("View Inventory", lambda: view_inventory(tree_frame), "📦")
        create_sidebar_button("Purchase", lambda: open_purchase_window(tree_frame, user_info), "🛒")

    create_sidebar_button("Logout", lambda: return_to_login(main_window), "⏏️")

    main_window.mainloop()

def return_to_login(current_window):
    from login import create_login_window
    current_window.destroy()
    create_login_window()
