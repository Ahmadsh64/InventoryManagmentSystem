import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import requests
API_URL = "http://localhost:5000/api"

# צבעים וממדים גלובליים
PRIMARY_COLOR = "#2563eb"
SECONDARY_COLOR = "#f4f6f8"
ACCENT_COLOR = "#10b981"  # ירוק לטקסט חיובי
TEXT_COLOR = "#222222"
BUTTON_TEXT_COLOR = "white"
ERROR_COLOR = "#ef4444"
FRAME_WIDTH = 1300
FRAME_HEIGHT = 700
SIDE_WIDTH = 350


def Notification_orders(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    tree_frame.pack_propagate(False)
    tree_frame.config(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    # סגנונות מותאמים ל-ttk
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton",
                    background=PRIMARY_COLOR,
                    foreground=BUTTON_TEXT_COLOR,
                    font=("Segoe UI", 11, "bold"),
                    padding=6)
    style.map("TButton",
              background=[('active', '#1d4ed8')])
    style.configure("Treeview",
                    font=("Segoe UI", 10),
                    rowheight=30,
                    fieldbackground=SECONDARY_COLOR)
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 11, "bold"),
                    background=PRIMARY_COLOR,
                    foreground=BUTTON_TEXT_COLOR)

    def load_branches():
        try:
            res = requests.get(f"{API_URL}/branches")
            data = res.json()
            branch_filter["values"] = ["הכל"] + [b["branch_name"] for b in data.get("branches", [])]
            branch_filter.set("הכל")
        except:
            branch_filter["values"] = ["הכל"]
            branch_filter.set("הכל")

    def load_notifications():
        notif_tree.delete(*notif_tree.get_children())

        # שליפת ערכי הסינון
        branch = branch_filter.get()
        status = status_filter.get()
        date = date_entry.get().strip()
        search = search_entry.get().lower()

        params = {}

        if branch != "הכל":
            params["branch_name"] = branch
        if status != "הכל":
            params["item_status"] = status
        if date:
            params["created_at"] = date
        if search:
            params["search"] = search

        try:
            res = requests.get(f"{API_URL}/notifications", params=params)
            notifications = res.json()

            for notif in notifications:
                order_id = notif.get("order_id", "")
                customer = notif.get("customer_name", "")
                notif_tree.insert("", "end", values=(order_id, customer))

        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת נתונים:\n{str(e)}")


    # ===== סרגל עליון =====
    top_frame = tk.Frame(tree_frame, height=50, bg=SECONDARY_COLOR)
    top_frame.pack(fill=tk.X, padx=15, pady=10)

    # סינון לפי סניף
    tk.Label(top_frame, text="סניף:", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11)).pack(side=tk.RIGHT, padx=(20, 5))
    branch_filter = ttk.Combobox(top_frame, width=18, font=("Segoe UI", 11), state="readonly")
    branch_filter.pack(side=tk.RIGHT)

    # סינון לפי תאריך (פשוט: תאריך בודד)
    tk.Label(top_frame, text="תאריך:", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11)).pack(side=tk.RIGHT, padx=(20, 5))
    date_entry = ttk.Entry(top_frame, width=12, font=("Segoe UI", 11))  # ניתן להזין YYYY-MM-DD
    date_entry.pack(side=tk.RIGHT)

    # חיפוש
    tk.Label(top_frame, text="🔍 חיפוש:", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11)).pack(side=tk.RIGHT)
    search_entry = ttk.Entry(top_frame, width=30, font=("Segoe UI", 11))
    search_entry.pack(side=tk.RIGHT, padx=8)

    # סינון סטטוס
    tk.Label(top_frame, text="סטטוס:", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11)).pack(side=tk.RIGHT,
                                                                                                      padx=(20, 5))
    status_filter = ttk.Combobox(top_frame, values=["הכל", "חדש", "התחלת מכלה", "נלקח", "סיום המכלה"], width=14, font=("Segoe UI", 11))
    status_filter.set("הכל")
    status_filter.pack(side=tk.RIGHT)

    # כפתור רענון
    refresh_btn = ttk.Button(top_frame, text="🔄 רענן", command=load_notifications)
    refresh_btn.pack(side=tk.RIGHT, padx=20)

    ahmad= ttk.Button(top_frame, text="פעולות", command=show_order_tracking_dashboard)
    ahmad.pack(side=tk.RIGHT, padx=20)

    # ===== מסגרת ראשית =====
    main_frame = tk.Frame(tree_frame, width=FRAME_WIDTH, height=FRAME_HEIGHT - 80, bg="#ffffff")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    # ===== צד שמאל: פרטי פריטים =====
    global notif_frame
    notif_frame = tk.Frame(main_frame, width=FRAME_WIDTH - SIDE_WIDTH, bg=SECONDARY_COLOR, relief=tk.FLAT)
    notif_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    notif_frame.pack_propagate(False)

    # ===== צד ימין: רשימת הזמנות =====
    detail_frame = tk.Frame(main_frame, width=SIDE_WIDTH, relief=tk.GROOVE, borderwidth=2, bg="white")
    detail_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
    detail_frame.pack_propagate(False)

    tk.Label(detail_frame, text="📦 הזמנות פעילות", font=("Segoe UI", 15, "bold"), bg="white", fg=PRIMARY_COLOR).pack(
        pady=12)

    notif_tree = ttk.Treeview(detail_frame, columns=("order_id", "customer"), show="headings", height=22)
    notif_tree.heading("order_id", text="מספר הזמנה")
    notif_tree.heading("customer", text="לקוח")
    notif_tree.column("order_id", width=120, anchor="center")
    notif_tree.column("customer", width=200, anchor="center")
    notif_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    notif_scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=notif_tree.yview)
    notif_tree.configure(yscrollcommand=notif_scroll.set)
    notif_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    # -- פונקציות אירועים וטעינת התראות -- (יש לשלב אותן מחוץ לפונקציה)

    def show_order_details(order_id, items):
        for widget in notif_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(notif_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(notif_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        image_refs = []  # לשמור את האובייקטים של התמונות למניעת GC

        for item in items:
            frame = tk.Frame(scrollable_frame, bg=SECONDARY_COLOR, bd=0, relief="flat", padx=15, pady=12)
            frame.pack(fill="x", padx=15, pady=8)

            # מסגרת עם צל קל
            card_bg = tk.Frame(frame, bg="white", relief="raised", bd=1)
            card_bg.pack(fill="both", expand=True)

            # ==== תמונה ====
            image_path = item.get("image_path", "")
            img_label = tk.Label(card_bg, bg="white")
            if image_path and os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img = img.resize((100, 100), Image.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    img_label.config(image=img_tk)
                    img_label.image = img_tk
                    image_refs.append(img_tk)
                except Exception:
                    img_label.config(text="(בעיה בתמונה)", fg=ERROR_COLOR)
            else:
                img_label.config(text="(אין תמונה)", fg=ERROR_COLOR)
            img_label.grid(row=0, column=0, rowspan=5, padx=15, pady=10)

            # ==== פרטי פריט ====
            info_font = ("Segoe UI", 11)
            bold_font = ("Segoe UI", 11, "bold")

            tk.Label(card_bg, text=f"מק״ט: {item['sku']}", bg="white", fg=TEXT_COLOR, font=info_font).grid(row=0,
                                                                                                           column=1,
                                                                                                           sticky="w",
                                                                                                           pady=2,
                                                                                                           padx=8)
            tk.Label(card_bg, text=f"שם פריט: {item['item_name']}", bg="white", fg=TEXT_COLOR, font=info_font).grid(
                row=1, column=1, sticky="w", pady=2, padx=8)
            tk.Label(card_bg, text=f"כמות: {item['quantity']}", bg="white", fg=TEXT_COLOR, font=info_font).grid(row=2,
                                                                                                                column=1,
                                                                                                                sticky="w",
                                                                                                                pady=2,
                                                                                                                padx=8)
            tk.Label(card_bg, text=f"צבע: {item['color']}  |  מידה: {item['size']}", bg="white", fg=TEXT_COLOR,
                     font=info_font).grid(row=3, column=1, sticky="w", pady=2, padx=8)

            status_color = ACCENT_COLOR if item['item_status'] in ["חדש", "התחלת מכלה", "נלקח", "סיום המכלה"] else ERROR_COLOR
            tk.Label(card_bg, text=f"סטטוס: {item['item_status']}", bg="white", fg=status_color, font=bold_font).grid(
                row=4, column=1, sticky="w", pady=(6, 0), padx=8)

            # ==== כפתורים עם ריווח נכון ====
            btn_frame = tk.Frame(card_bg, bg="white")
            btn_frame.grid(row=5, column=0, columnspan=2, pady=12, padx=8, sticky="w")
            view_map_button = ttk.Button(btn_frame, text="הצג מיקום במפה",
                                         command=lambda sku=item["sku"]: show_item_location_on_map(order_id, sku))
            view_map_button.pack(anchor="e", pady=5)

            def confirm_pickup(order_id, sku):
                try:
                    payload = {"order_id": order_id, "sku": sku}
                    res = requests.post(f"{API_URL}/mark_item_taken", json=payload)
                    if res.status_code == 200:
                        messagebox.showinfo("אישור", "הפריט סומן כנאסף!")

                        # עדכון תצוגת הפריטים
                        items = requests.get(f"{API_URL}/order/{order_id}").json()
                        show_order_details(order_id, items)

                        # עדכון ההתראות (צד ימין)
                        load_notifications()
                    else:
                        messagebox.showwarning("שגיאה", res.json().get("error", "אירעה שגיאה"))
                except Exception as e:
                    messagebox.showerror("שגיאה", str(e))

            sku = item['sku']
            ttk.Button(
                btn_frame,
                text="✅ אישור קבלת פריט",
                command=lambda oid=order_id, s=sku: confirm_pickup(oid, s)
            ).pack(side="left", padx=5)

        # כפתור התחלת מכלה להזמנה (לפני סיום מכלה)
        def start_fulfillment_order(order_id):
            try:
                res = requests.post(f"{API_URL}/order/{order_id}/start_fulfillment")
                if res.status_code == 200:
                    messagebox.showinfo("הצלחה", "התחלת המכלה נרשמה!")

                    # רענון תצוגת פרטי ההזמנה
                    items = requests.get(f"{API_URL}/order/{order_id}").json()
                    show_order_details(order_id, items)

                    # רענון התראות
                    load_notifications()
                else:
                    messagebox.showwarning("שגיאה", res.json().get("message", "אירעה שגיאה"))
            except Exception as e:
                messagebox.showerror("שגיאה", str(e))

        ttk.Button(
            notif_frame,
            text="🚀 התחלת מכלה להזמנה",
            command=lambda oid=order_id: start_fulfillment_order(oid)
        ).pack(pady=5)

        # כפתור סיום מכלה
        def complete_fulfillment():
            try:
                res = requests.post(f"{API_URL}/order/{order_id}/complete_fulfillment")
                if res.status_code == 200:
                    messagebox.showinfo("הצלחה", "ההזמנה סומנה כמושלמת!")
                    items = requests.get(f"{API_URL}/order/{order_id}").json()
                    show_order_details(order_id, items)
                    load_notifications()

                else:
                    messagebox.showwarning("שגיאה", res.json().get("message", "שגיאה כללית"))
            except Exception as e:
                messagebox.showerror("שגיאה", str(e))

        ttk.Button(notif_frame, text="✅ סיום מכלה להזמנה", command=complete_fulfillment).pack(pady=10)

    def on_notification_click(event):
        selected = notif_tree.selection()
        if not selected:
            return
        item = selected[0]

        values = notif_tree.item(item).get("values", [])
        if not values:
            messagebox.showerror("שגיאה", "לא ניתן לקרוא את פרטי ההתראה")
            return

        order_id = values[0]
        notification_id = item  # כי זה ה־iid

        try:
            res = requests.get(f"{API_URL}/order/{order_id}")
            items = res.json()
            show_order_details(order_id, items)

            requests.post(f"{API_URL}/notifications/{notification_id}/mark_read")
            load_notifications()
            show_order_details(order_id, items)
        except Exception as e:
            messagebox.showerror("שגיאה", str(e))

    def periodic_refresh():
        try:
            load_notifications()
        except tk.TclError:
            return
        tree_frame.after(30000, periodic_refresh)

    load_notifications()
    periodic_refresh()

    def show_item_location_on_map(order_id, sku):
        # Store the selected SKU for highlighting later
        global selected_sku_for_map
        selected_sku_for_map = sku  # used inside the map function
        show_warehouse_map_for_order(order_id)

    # ========== מפת מחסן עם פריטים צהובים ==========
    def show_warehouse_map_for_order(order_id):
        import tkinter as tk
        from tkinter import ttk, messagebox, simpledialog
        import requests

        CELL_WIDTH = 70
        CELL_HEIGHT = 40
        TOP_MARGIN = 50
        LEFT_MARGIN = 50
        GRID_SIZE = 10
        BLOCK_SPACING = 20

        zones = [chr(i) for i in range(ord("A"), ord("J") + 1)]
        taken_items = set()

        try:
            response = requests.get(f"{API_URL}/warehouse_map_with_order/{order_id}")
            order_items = response.json()["items"]
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאת קבלת מפת מחסן:\n{e}")
            return

        items_map = {(item['shelf_zone'], item['shelf_row'], item['shelf_column']): item for item in order_items}

        order_window = tk.Toplevel()
        order_window.title(f"מפת מחסן - הזמנה #{order_id}")
        order_window.geometry("850x650")

        # Frame for controls and progress bar
        top_frame = tk.Frame(order_window)
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        zone_nav_frame = tk.Frame(order_window)
        zone_nav_frame.pack(side="top", pady=5)

        tk.Label(zone_nav_frame, text="מעבר בין אזורים:", font=("Arial", 10)).pack(side="right", padx=5)
        for zn in zones:
            btn = tk.Button(zone_nav_frame, text=zn, width=2, command=lambda z=zn: draw_grid_view(z))
            btn.pack(side="right", padx=2)

        # Search field
        tk.Label(top_frame, text="חיפוש (שם, SKU, מיקום):").pack(side="right")
        search_var = tk.StringVar()
        search_entry = tk.Entry(top_frame, textvariable=search_var, width=30)
        search_entry.pack(side="right", padx=5)

        # Filter dropdown
        tk.Label(top_frame, text="סינון לפי מצב:").pack(side="right", padx=(20, 0))
        filter_var = tk.StringVar(value="הכל")
        filter_options = ["הכל", "זמין", "נלקח", "להיאסף", "חסר במלאי"]
        filter_menu = ttk.Combobox(top_frame, textvariable=filter_var, values=filter_options, state="readonly",
                                   width=10)
        filter_menu.pack(side="right", padx=5)

        # Progress bar for order fulfillment
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(top_frame, maximum=len(order_items), variable=progress_var, length=200)
        progress_bar.pack(side="left", padx=10)
        progress_label = tk.Label(top_frame, text=f"נאספו 0 מתוך {len(order_items)} פריטים")
        progress_label.pack(side="left")
        # Side panel for order item list
        side_frame = tk.Frame(order_window, width=250, bg="#f1f1f1")
        side_frame.pack(side="right", fill="y")

        item_list_label = tk.Label(side_frame, text="רשימת פריטים להזמנה", font=("Arial", 12, "bold"), bg="#f1f1f1")
        item_list_label.pack(pady=10)

        item_listbox = tk.Listbox(side_frame, width=40, height=30, font=("Arial", 9))
        item_listbox.pack(padx=5, pady=5)

        def update_item_list():
            item_listbox.delete(0, tk.END)
            for item in order_items:
                sku = item["sku"]
                name = item["item_name"]
                zone = item["shelf_zone"]
                row = item["shelf_row"]
                col = item["shelf_column"]
                status = "✔" if sku in taken_items else "○"
                item_listbox.insert(tk.END, f"{status} {name} ({zone}-{row}-{col})")

        # Frame for canvas and scrollbar
        canvas_frame = tk.Frame(order_window)
        canvas_frame.pack(fill="both", expand=True)

        order_canvas = tk.Canvas(canvas_frame, width=800, height=500, bg="white")
        order_canvas.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=order_canvas.yview)
        scrollbar_y.pack(side="right", fill="y")

        order_canvas.configure(yscrollcommand=scrollbar_y.set)
        order_canvas.bind('<Configure>', lambda e: order_canvas.configure(scrollregion=order_canvas.bbox("all")))

        # Create an internal frame inside the canvas to hold the grid
        grid_frame = tk.Frame(order_canvas)
        order_canvas.create_window((0, 0), window=grid_frame, anchor="nw")

        tooltip_text = order_canvas.create_text(0, 0, text="", anchor="nw", font=("Arial", 8), state="hidden")
        current_view = {"mode": "column", "zone": None, "back_btn": None}

        def update_progress():
            progress_var.set(len(taken_items))
            progress_label.config(text=f"נאספו {len(taken_items)} מתוך {len(order_items)} פריטים")

        def show_item_info_popup(item, zone):
            popup = tk.Toplevel()
            popup.title(f"פרטי פריט - {item['item_name']}")
            popup.geometry("350x320")
            popup.resizable(False, False)

            info_frame = tk.Frame(popup, padx=10, pady=10)
            info_frame.pack(fill="both", expand=True)

            # Editable fields
            fields = {
                "שם פריט": item.get('item_name', ''),
                "SKU": item.get('sku', ''),
                "כמות זמינה": item.get('quantity', ''),
                "תיאור": item.get('description', 'אין'),
                "תאריך תפוגה": item.get('expiration_date', 'לא צויין'),
                "מיקום": f"{zone}-{item.get('shelf_row', '')}-{item.get('shelf_column', '')}"
            }
            entries = {}

            for label_text, value in fields.items():
                frame = tk.Frame(info_frame)
                frame.pack(fill="x", pady=3)
                tk.Label(frame, text=label_text + ":", width=15, anchor="w", font=("Segoe UI", 10, "bold")).pack(
                    side="right")
                ent = tk.Entry(frame, font=("Segoe UI", 10))
                ent.pack(side="right", fill="x", expand=True)
                ent.insert(0, value)
                if label_text == "SKU" or label_text == "מיקום":
                    ent.config(state="readonly")  # SKU and location should not be editable
                entries[label_text] = ent

            btn_frame = tk.Frame(popup, pady=10)
            btn_frame.pack(fill="x", padx=10)

            def confirm_pickup(order_id, sku):
                try:
                    payload = {"order_id": order_id, "sku": sku}
                    res = requests.post(f"{API_URL}/mark_item_taken", json=payload)
                    if res.status_code == 200:
                        messagebox.showinfo("אישור", "הפריט סומן כנאסף!")

                        # עדכון תצוגת הפריטים
                        items = requests.get(f"{API_URL}/order/{order_id}").json()
                        show_order_details(order_id, items)
                        update_item_list()

                        # עדכון ההתראות (צד ימין)
                        load_notifications()
                    else:
                        messagebox.showwarning("שגיאה", res.json().get("error", "אירעה שגיאה"))
                except Exception as e:
                    messagebox.showerror("שגיאה", str(e))

            sku = item['sku']
            ttk.Button(
                btn_frame,
                text="✅ אישור קבלת פריט",
                command=lambda oid=order_id, s=sku: confirm_pickup(oid, s)
            ).pack(side="left", padx=5)
            tk.Button(btn_frame, text="❌ סגור", command=popup.destroy,
                      bg="#f44336", fg="white", width=10).pack(side="left", padx=5)

        def complete_fulfillment():
            items_required = [item.get('sku') for item in order_items if item.get('quantity', 1) > 0]
            if len(taken_items) < len(items_required):
                confirm = messagebox.askyesno("סיום מכלה", "לא כל הפריטים נאספו. האם לסיים בכל זאת?")
                if not confirm:
                    return

            try:
                response = requests.post(f"{API_URL}/order/{order_id}/complete_fulfillment")
                if response.status_code == 200:
                    messagebox.showinfo("בוצע", "המכלה הושלמה בהצלחה.")
                    order_window.destroy()
                    items = requests.get(f"{API_URL}/order/{order_id}").json()
                    show_order_details(order_id, items)
                    load_notifications()  # או לקרוא מחדש לשרת
                else:
                    messagebox.showerror("שגיאה", "נכשל לסיים מכלה")
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בסיום מכלה:\n{e}")

        complete_btn = tk.Button(side_frame, text="✅ סיום מכלה", command=complete_fulfillment,
                                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        complete_btn.pack(pady=10)

        def get_inventory_by_zone(zone):
            try:
                response = requests.get(f"{API_URL}/inventory_by_zone/{zone}")
                return response.json().get("inventory", [])
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאת טעינת נתוני מחסן:\n{e}")
                return []

        def filter_and_search_items(inventory_map):
            filtered = {}
            search_text = search_var.get().strip().lower()
            filter_status = filter_var.get()

            for pos, item in inventory_map.items():
                sku = item.get('sku', '').lower()
                name = item.get('item_name', '').lower()
                loc = f"{item.get('shelf_zone', current_view['zone'])}-{item.get('shelf_row', '')}-{item.get('shelf_column', '')}".lower()
                status = "זמין"
                key = (item.get('shelf_zone'), item.get('shelf_row'), item.get('shelf_column'))
                if key in items_map:
                    sku_in_order = items_map[key]['sku']
                    if sku_in_order in taken_items:
                        status = "נלקח"
                    else:
                        status = "התחלת מכלה"
                if item.get('quantity', 0) == 0:
                    status = "חסר במלאי"

                # Apply filter
                if filter_status != "הכל" and status != filter_status:
                    continue
                # Apply search
                if search_text:
                    if search_text not in sku and search_text not in name and search_text not in loc:
                        continue

                filtered[pos] = (item, status)
            return filtered

        def get_fill_color_by_status(status):
            return {
                "נלקח": "green",
                "התחלת מכלה": "yellow",
                "חסר במלאי": "red",
                "זמין": "white"
            }.get(status, "white")

        def draw_column_view():
            order_canvas.delete("all")
            current_view['mode'] = 'column'
            current_view['zone'] = None

            for widget in grid_frame.winfo_children():
                widget.destroy()

            for zone_index, zone in enumerate(zones):
                block_x = LEFT_MARGIN + zone_index * (CELL_WIDTH + BLOCK_SPACING)
                inventory_data = get_inventory_by_zone(zone)

                # קיבוץ לפי שורה
                rows_map = {}
                for item in inventory_data:
                    row = item['shelf_row']
                    rows_map.setdefault(row, []).append(item)

                for row in range(1, GRID_SIZE + 1):
                    x1 = block_x
                    y1 = TOP_MARGIN + (row - 1) * CELL_HEIGHT
                    x2 = x1 + CELL_WIDTH
                    y2 = y1 + CELL_HEIGHT

                    fill_color = "white"
                    text_lines = [f"{zone}-{row:02}"]
                    is_selected = False

                    if row in rows_map:
                        items_in_row = rows_map[row]
                        for item in items_in_row:
                            key = (item['shelf_zone'], item['shelf_row'], item['shelf_column'])
                            status = "זמין"

                            if key in items_map:
                                sku = items_map[key]['sku']
                                if sku in taken_items:
                                    status = "נלקח"
                                else:
                                    status = "התחלת מכלה"
                            if item['quantity'] == 0:
                                status = "חסר במלאי"

                            item_color = get_fill_color_by_status(status)

                            # נבחר את הצבע ה"משמעותי ביותר" (צהוב > ירוק > אפור) עבור הרקע הכללי
                            if item_color == "yellow":
                                fill_color = "yellow"
                            elif item_color == "green" and fill_color != "yellow":
                                fill_color = "green"
                            elif item_color == "gray" and fill_color not in ["yellow", "green"]:
                                fill_color = "gray"

                            name = item.get('item_name', 'פריט')
                            sku = item.get('sku', '')
                            text_lines.append(f"{name} ({sku})")

                            # סימון פריט שנבחר למפה
                            if "selected_sku_for_map" in globals() and sku == selected_sku_for_map:
                                is_selected = True

                    # ציור
                    order_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    order_canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text="\n".join(text_lines),
                        font=("Arial", 7), justify="center"
                    )

                    if is_selected:
                        order_canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="red", width=3)
                        order_canvas.create_text(x1 + 5, y1 + 5, text="★", anchor="nw", fill="red",
                                                 font=("Arial", 14, "bold"))

                label_id = order_canvas.create_text(
                    block_x + CELL_WIDTH // 2,
                    TOP_MARGIN - 20,
                    text=f"אזור {zone}",
                    font=("Arial", 12, "bold")
                )
                order_canvas.tag_bind(label_id, "<Button-1>", lambda e, z=zone: draw_grid_view(z))

            update_progress()

        def draw_grid_view(zone):
            order_canvas.delete("all")
            current_view['mode'] = 'grid'
            current_view['zone'] = zone

            # קבלת פריטים לאזור
            inventory_data = get_inventory_by_zone(zone)
            inventory_map = {(zone, item['shelf_row'], item['shelf_column']): item for item in inventory_data}

            filtered_items = filter_and_search_items(inventory_map)

            # כפתור חזרה
            if current_view['back_btn'] is None:
                back_btn = tk.Button(order_window, text="⬅ חזרה לרשימת האזורים", command=draw_column_view, bg="#2196F3",
                                     fg="white")
                back_btn.pack(side="top", pady=3)
                current_view['back_btn'] = back_btn
            else:
                current_view['back_btn'].pack(side="top", pady=3)

            for row in range(1, GRID_SIZE + 1):
                for col in range(1, GRID_SIZE + 1):
                    x1 = LEFT_MARGIN + (col - 1) * CELL_WIDTH
                    y1 = TOP_MARGIN + (row - 1) * CELL_HEIGHT
                    x2 = x1 + CELL_WIDTH
                    y2 = y1 + CELL_HEIGHT

                    key = (zone, row, col)
                    item_data_status = filtered_items.get(key)

                    fill_color = "white"
                    text = f"{zone}-{row:02}-{col:02}"
                    is_selected = False

                    if item_data_status:
                        item, status = item_data_status
                        fill_color = get_fill_color_by_status(status)
                        text = f"{item['item_name']}\nSKU:{item['sku']}"

                        # האם זה הפריט שנבחר לצפייה
                        if "selected_sku_for_map" in globals() and item['sku'] == selected_sku_for_map:
                            is_selected = True

                    rect_id = order_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    text_id = order_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Arial", 8),
                                                       justify="center")

                    if is_selected:
                        order_canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="red", width=3)
                        order_canvas.create_text(x1 + 5, y1 + 5, text="★", anchor="nw", fill="red",
                                                 font=("Arial", 14, "bold"))

                    # קישור לפרטים
                    if item_data_status:
                        def make_callback(it=item, zn=zone):
                            return lambda e: show_item_info_popup(it, zn)

                        order_canvas.tag_bind(rect_id, "<Button-1>", make_callback())
                        order_canvas.tag_bind(text_id, "<Button-1>", make_callback())

            # כותרת
            order_canvas.create_text(
                LEFT_MARGIN + (CELL_WIDTH * GRID_SIZE) / 2,
                TOP_MARGIN - 30,
                text=f"מפת מחסן לאזור {zone} (לחצו על פריט לקבלת פרטים)",
                font=("Arial", 14, "bold")
            )

            update_progress()

        def on_search_filter_change(*args):
            if current_view['mode'] == 'grid' and current_view['zone']:
                draw_grid_view(current_view['zone'])
            else:
                draw_column_view()

        search_var.trace_add("write", on_search_filter_change)
        filter_var.trace_add("write", on_search_filter_change)

        draw_column_view()

    tree_frame.bind("<Double-1>", on_notification_click)
    periodic_refresh()
    notif_tree.bind("<Double-1>", on_notification_click)

    load_branches()
    load_notifications()

def show_order_tracking_dashboard():
    window = tk.Toplevel()
    window.title("מעקב אחרי הזמנות")
    window.geometry("1000x600")

    top_frame = tk.Frame(window)
    top_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(top_frame, text="סינון לפי סניף:").pack(side="right")
    branch_var = tk.StringVar()
    branch_filter = ttk.Combobox(top_frame, textvariable=branch_var, state="readonly")
    branch_filter.pack(side="right", padx=5)

    tk.Label(top_frame, text="חיפוש:").pack(side="right", padx=(20, 0))
    search_var = tk.StringVar()
    search_entry = tk.Entry(top_frame, textvariable=search_var, width=30)
    search_entry.pack(side="right")

    tk.Button(top_frame, text="רענן", command=lambda: load_data()).pack(side="left", padx=10)

    columns = ("purchase_id", "purchase_date", "customer_name", "item_name", "sku", "quantity", "total_price", "branch_name", "order_status")
    tree = ttk.Treeview(window, columns=columns, show="headings", height=20)
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    def load_branches():
        try:
            res = requests.get(f"{API_URL}/branches")
            branches = res.json().get("branches", [])
            branch_filter['values'] = ["הכל"] + [b['branch_name'] for b in branches]
            branch_filter.set("הכל")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאת טעינת סניפים: {e}")

    def load_data():
        try:
            res = requests.get(f"{API_URL}/purchases")
            data = res.json().get("purchases", [])
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאת טעינת נתונים: {e}")
            return

        tree.delete(*tree.get_children())

        search_text = search_var.get().lower()
        selected_branch = branch_var.get()

        for row in data:
            if selected_branch != "הכל" and row["branch_name"] != selected_branch:
                continue
            if search_text:
                if not (search_text in row["customer_name"].lower() or
                        search_text in row["item_name"].lower() or
                        search_text in row["sku"].lower()):
                    continue

            tree.insert("", "end", values=(
                row["purchase_id"],
                row["purchase_date"],
                row["customer_name"],
                row["item_name"],
                row["sku"],
                row["quantity"],
                row["total_price"],
                row["branch_name"],
                row["order_status"]
            ))

    load_branches()
    load_data()
