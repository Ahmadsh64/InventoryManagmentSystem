
from database import connect_to_database
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

ICONS = {
    "total": "📦",
    "overstock": "📈",
    "outofstock": "⚠️",
    "bestseller": "🏆",
    "sales": "🛒",
}

def open_dashboard_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    title_label = tk.Label(tree_frame, text="📊 דשבורד ניהולי - מצב מערכת", font=("Arial", 22, "bold"), bg="#f9f9f9")
    title_label.pack(pady=15)

    # בחירת סניף
    filter_frame = tk.Frame(tree_frame, bg="#f9f9f9")
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="סנן לפי סניף:", font=("Arial", 12), bg="#f9f9f9").pack(side=tk.LEFT, padx=5)

    branch_var = tk.StringVar()
    branch_dropdown = ttk.Combobox(filter_frame, textvariable=branch_var, width=25, state="readonly")
    branch_dropdown.pack(side=tk.LEFT, padx=5)

    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT branch_id, branch_name FROM branches")
    branches = cursor.fetchall()
    conn.close()

    branch_dropdown['values'] = ["כל הסניפים"] + [f"{branch[0]} - {branch[1]}" for branch in branches]
    branch_dropdown.current(0)

    # כפתור רענון
    refresh_btn = ttk.Button(filter_frame, text="🔄 רענן נתונים", command=lambda: update_dashboard(branch_var.get(), stats_labels, graph_frames))
    refresh_btn.pack(side=tk.LEFT, padx=5)

    # אזור סטטיסטיקות
    stats_frame = tk.Frame(tree_frame, bg="#f9f9f9")
    stats_frame.pack(pady=15)

    stats_labels = {}

    def create_stat_card(master, key, bg_color):
        frame = tk.Frame(master, bg=bg_color, padx=20, pady=15, relief=tk.RAISED, bd=2)
        label = tk.Label(frame, text=f"{ICONS[key]}\n...", font=("Arial", 14, "bold"), bg=bg_color, fg="white", justify="center")
        label.pack()
        return frame, label

    colors = {
        "total": "#007ACC",
        "overstock": "#28A745",
        "outofstock": "#DC3545",
        "bestseller": "#17A2B8",
        "sales": "#6F42C1"
    }

    keys = ["total", "overstock", "outofstock", "bestseller", "sales"]
    for i, key in enumerate(keys):
        frame, label = create_stat_card(stats_frame, key, colors[key])
        frame.grid(row=i // 5, column=i % 5, padx=10, pady=10, sticky="e")
        stats_labels[key] = label

    # אזור גרפים
    graph_frame = tk.Frame(tree_frame, bg="#f9f9f9")
    graph_frame.pack(pady=15)

    graph_frames = {
        "category_pie": tk.LabelFrame(graph_frame, text="התפלגות מלאי לפי קטגוריה", font=("Arial", 12, "bold")),
        "branch_bar": tk.LabelFrame(graph_frame, text="מצב מלאי לפי סניפים", font=("Arial", 12, "bold")),
        "sales_line": tk.LabelFrame(graph_frame, text="מכירות חודשיות", font=("Arial", 12, "bold"))
    }

    graph_frames["category_pie"].grid(row=0, column=0, padx=10, pady=10)
    graph_frames["branch_bar"].grid(row=0, column=1, padx=10, pady=10)
    graph_frames["sales_line"].grid(row=0, column=2, columnspan=2, padx=10, pady=10)

    # טען נתונים ראשונים
    update_dashboard(branch_var.get(), stats_labels, graph_frames)

def update_dashboard(branch_filter, stats_labels, graph_frames):
    conn = connect_to_database()
    cursor = conn.cursor()

    where_clause = ""
    where_clauses =""
    params = ()
    if branch_filter != "כל הסניפים" and branch_filter:
        branch_id = int(branch_filter.split(" - ")[0])
        where_clause = " AND branch_id = %s "
        where_clauses="WHERE i.branch_id=%s"
        params = (branch_id,)

    # סה"כ מלאי
    cursor.execute(f"SELECT SUM(quantity) FROM inventory WHERE is_active = TRUE {where_clause}", params)
    total_inventory = cursor.fetchone()[0] or 0
    stats_labels["total"].config(text=f"{ICONS['total']}\nסה\"כ מלאי: {total_inventory}")

    # עודף מלאי (יותר מחודש ו-100 יחידות לא נמכרו)
    cursor.execute(f"""
    SELECT i.sku, i.item_name, b.branch_name, i.quantity, i.received_date, i.is_active,
                   IFNULL(SUM(p.quantity), 0), TIMESTAMPDIFF(MONTH, i.received_date, CURDATE())
            FROM inventory i
            JOIN branches b ON i.branch_id = b.branch_id
            LEFT JOIN purchases p ON i.sku = p.sku AND p.purchase_date >= i.received_date
			{where_clauses}
            GROUP BY i.sku 
            HAVING SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
    """, params)
    overstock = cursor.fetchall()
    stats_labels["overstock"].config(text=f"{ICONS['overstock']}\nעודף מלאי: {len(overstock)}")

    # חוסרי מלאי
    cursor.execute(f"SELECT COUNT(*) FROM inventory WHERE quantity < 100 {where_clause}", params)
    outofstock = cursor.fetchone()[0]
    stats_labels["outofstock"].config(text=f"{ICONS['outofstock']}\nחוסרי מלאי: {outofstock}")

    # המוצר הנמכר ביותר
    cursor.execute(f"""
        SELECT p.sku, SUM(p.quantity) as total_sold
        FROM purchases p
        JOIN inventory i ON p.sku = i.sku
        WHERE i.is_active = TRUE {where_clause.replace('AND', 'AND i.')}
        GROUP BY p.sku
        ORDER BY total_sold DESC
        LIMIT 1
    """, params)
    best_seller = cursor.fetchone()
    if best_seller:
        stats_labels["bestseller"].config(text=f"{ICONS['bestseller']}\nהנמכר ביותר:\n{best_seller[0]} ({best_seller[1]} יח')")
    else:
        stats_labels["bestseller"].config(text=f"{ICONS['bestseller']}\nהנמכר ביותר: אין נתונים")

    # מכירות אחרונות (30 ימים)
    cursor.execute(f"""
        SELECT SUM(p.quantity) FROM purchases p
        JOIN inventory i ON p.sku = i.sku
        WHERE p.purchase_date >= CURDATE() - INTERVAL 30 DAY
        {where_clause.replace('AND', 'AND i.')}
    """, params)
    recent_sales = cursor.fetchone()[0] or 0
    stats_labels["sales"].config(text=f"{ICONS['sales']}\nמכירות 30 ימים: {recent_sales}")

    # גרף פאי — קטגוריות
    cursor.execute(f"""
        SELECT category, SUM(quantity) FROM inventory
        WHERE is_active = TRUE {where_clause}
        GROUP BY category
    """, params)
    data = cursor.fetchall()
    categories = [row[0] for row in data]
    quantities = [row[1] for row in data]

    draw_pie_chart(categories, quantities, graph_frames["category_pie"])

    # גרף עמודות — מלאי לפי סניפים
    cursor.execute("""
        SELECT b.branch_name, SUM(i.quantity)
        FROM inventory i
        JOIN branches b ON i.branch_id = b.branch_id
        WHERE i.is_active = TRUE
        GROUP BY b.branch_name
    """)
    data = cursor.fetchall()
    branch_names = [row[0] for row in data]
    branch_quantities = [row[1] for row in data]

    draw_bar_chart(branch_names, branch_quantities, graph_frames["branch_bar"])

    # גרף קו — מכירות לפי חודש
    cursor.execute("""
        SELECT DATE_FORMAT(purchase_date, '%Y-%m') as month, SUM(quantity)
        FROM purchases
        GROUP BY month
        ORDER BY month ASC
    """)
    data = cursor.fetchall()
    months = [row[0] for row in data]
    sales = [row[1] for row in data]

    draw_line_chart(months, sales, graph_frames["sales_line"])

    conn.close()

def draw_pie_chart(labels, sizes, frame):
    for widget in frame.winfo_children():
        widget.destroy()
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def draw_bar_chart(labels, values, frame):
    for widget in frame.winfo_children():
        widget.destroy()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(labels, values, color="#007ACC")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def draw_line_chart(labels, values, frame):
    for widget in frame.winfo_children():
        widget.destroy()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(labels, values, marker='o', color="#28A745")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
