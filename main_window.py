import ctypes
import tkinter as tk
from inventory import (
    view_inventory, open_add_item_window, open_search_item_window,
    open_update_item_window, open_delete_item_window,
    open_purchase_window, open_finance_window)
from reports import open_report_window
from Notifications import refresh_alerts_only, open_alerts_window, Notification_orders
from dashboard import open_modern_dashboard

# תמיכה ב־DPI גבוה ב-Windows (למניעת טשטוש)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# ... (התחלה זהה)

def open_main_window(user_type, user_info):
    main_window = tk.Tk()
    main_window.title("Inventory Management System")
    main_window.geometry("1200x800")
    main_window.configure(bg="#f5f6fa")

    sidebar_visible = True

    # הגדרות פונט וסגנון
    FONT_FAMILY = "Segoe UI"
    BUTTON_FONT = (FONT_FAMILY, 13)
    HEADER_FONT = (FONT_FAMILY, 14, "bold")

    main_container = tk.Frame(main_window, bg="white")
    main_container.pack(fill="both", expand=True)

    main_container.columnconfigure(0, weight=0)
    main_container.columnconfigure(1, weight=1)
    main_container.rowconfigure(0, weight=1)

    sidebar = tk.Frame(main_container, width=230, bg="#2f3640")
    sidebar.grid(row=0, column=0, sticky="ns")

    content_frame = tk.Frame(main_container, bg="white")
    content_frame.grid(row=0, column=1, sticky="nsew")

    # לוגו/שם אפליקציה
    logo_label = tk.Label(
        sidebar, text="🌀 StockKeeper", bg="#2f3640", fg="white",
        font=("Segoe UI", 18, "bold")
    )
    logo_label.pack(pady=(30, 10))

    # --- Header ---
    header_frame = tk.Frame(content_frame, height=50, bg="white")
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)

    header_frame.columnconfigure(0, weight=1)
    header_frame.columnconfigure(1, weight=4)
    header_frame.columnconfigure(2, weight=1)

    toggle_btn = tk.Button(
        header_frame, text="❌", command=lambda: toggle_sidebar(),
        font=(FONT_FAMILY, 12), bg="white", bd=0, fg="#2f3640", cursor="hand2"
    )
    toggle_btn.grid(row=0, column=0, sticky="w", padx=10)

    header = tk.Label(
        header_frame,
        text=f"Welcome, {user_info[1]} ({user_type.title()})",
        font=HEADER_FONT, bg="#f5f6fa", fg="#2f3640"
    )
    header.grid(row=0, column=1)

    alerts_label = tk.Label(
        header_frame, text="", font=(FONT_FAMILY, 12, "bold"),
        bg="white", fg="red"
    )
    alerts_label.grid(row=0, column=2, sticky="e", padx=10)

    def toggle_sidebar():
        nonlocal sidebar_visible
        if sidebar_visible:
            sidebar.grid_remove()
            toggle_btn.config(text="☰")
        else:
            sidebar.grid()
            toggle_btn.config(text="❌")
        sidebar_visible = not sidebar_visible

    # --- עיצוב אזור התוכן ---
    global tree_frame
    tree_frame = tk.Frame(content_frame, bg="white", relief="sunken", bd=1)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
    tree_frame.pack_propagate(False)

    # === יצירת כפתור סרגל צד עם עיצוב אחיד ===
    def create_sidebar_button(text, command, icon=None):
        btn = tk.Button(
            sidebar,
            text=f"{icon}  {text}" if icon else text,
            font=BUTTON_FONT,
            bg="#353b48",
            fg="white",
            activebackground="#40739e",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            anchor="w",
            command=command,
            cursor="hand2",
            relief="flat"
        )
        btn.pack(fill="x", padx=12, pady=4)

    # --- כפתורי ניווט לפי סוג המשתמש ---
    if user_type == "manager":
        refresh_alerts_only(alerts_label)
        create_sidebar_button("Add Item", lambda: open_add_item_window(tree_frame), "➕")
        create_sidebar_button("Update Item", lambda: open_update_item_window(tree_frame), "✏️")
        create_sidebar_button("Delete Item", lambda: open_delete_item_window(tree_frame), "🗑️")
        create_sidebar_button("Search Item", lambda: open_search_item_window(tree_frame), "🔍")
        create_sidebar_button("View Inventory", lambda: view_inventory(tree_frame), "📦")
        create_sidebar_button("Sales", lambda: Notification_orders(tree_frame), "🛍️")
        create_sidebar_button("Reports", lambda: open_report_window(tree_frame), "📈")
        create_sidebar_button("Alerts", lambda: open_alerts_window(tree_frame, alerts_label, main_window), "🚨")
        create_sidebar_button("Finance", lambda: open_finance_window(tree_frame), "💰")
        create_sidebar_button("Dashboard", lambda: open_modern_dashboard(tree_frame), "📊")

    elif user_type == "worker":
        create_sidebar_button("View Inventory", lambda: view_inventory(tree_frame), "📦")
        create_sidebar_button("Sales", lambda: Notification_orders(tree_frame), "🛍️")
        create_sidebar_button("Update Item", lambda: open_update_item_window(tree_frame), "✏️")
        create_sidebar_button("Search Item", lambda: open_search_item_window(tree_frame), "🔍")
        create_sidebar_button("Reports", lambda: open_report_window(tree_frame), "📈")

    elif user_type == "customer":
        create_sidebar_button("View Inventory", lambda: view_inventory(tree_frame), "📦")
        create_sidebar_button("Purchase", lambda: open_purchase_window(tree_frame, user_info), "🛒")

    create_sidebar_button("Logout", lambda: return_to_login(main_window), "⏏️")

    # --- כיתוב תחתון ---
    footer = tk.Label(
        sidebar, text="© 2025 FOX Stores", bg="#2f3640", fg="#dcdde1",
        font=(FONT_FAMILY, 9), anchor="center"
    )
    footer.pack(side="bottom", pady=15)

    main_window.mainloop()


def return_to_login(current_window):
    from login import create_login_window
    current_window.destroy()
    create_login_window()
