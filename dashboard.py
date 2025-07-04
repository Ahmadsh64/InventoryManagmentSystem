import tkinter as tk
from tkinter import ttk
from database import connect_to_database
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# === פונקציות עזר ===

def fetch_branches():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT branch_id, branch_name FROM branches")
    result = cursor.fetchall()
    conn.close()
    return result


def generate_demo_data(branch_id=None):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    inventory_filter = "WHERE i.is_active = TRUE"
    purchase_filter = ""
    expense_filter = ""
    inv_exp_params = ()
    purchase_params = ()

    if branch_id:
        # שליפת שם הסניף לפי מזהה
        branch_name = next((b[1] for b in fetch_branches() if b[0] == branch_id), None)

        inventory_filter += " AND i.branch_id = %s"
        expense_filter = "WHERE e.branch_id = %s"
        purchase_filter = "WHERE branch_name = %s"

        inv_exp_params = (branch_id,)
        purchase_params = (branch_name,)

    # סה"כ מלאי
    cursor.execute(f"""
        SELECT SUM(i.quantity) AS total_inventory 
        FROM inventory i 
        {inventory_filter}
    """, inv_exp_params)
    total_inventory = cursor.fetchone()["total_inventory"] or 0

    # עודף מלאי
    cursor.execute(f"""
        SELECT COUNT(*) AS overstock 
    FROM (
    SELECT i.sku, i.item_name, b.branch_name, i.quantity, i.received_date, i.is_active,
                   IFNULL(SUM(p.quantity), 0), TIMESTAMPDIFF(MONTH, i.received_date, CURDATE())
            FROM inventory i
            JOIN branches b ON i.branch_id = b.branch_id
            LEFT JOIN purchases p ON i.sku = p.sku AND p.purchase_date >= i.received_date
{inventory_filter}
            GROUP BY i.sku
            HAVING i.quantity > 50 AND i.is_active = TRUE AND SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
    ) AS subquery; 
    """, inv_exp_params)
    overstock_items = cursor.fetchone()["overstock"] or 0

    # חוסרים
    cursor.execute(f"""
        SELECT COUNT(*) AS out_of_stock 
        FROM inventory i 
        {inventory_filter} AND i.quantity < 10
    """, inv_exp_params)
    out_of_stock = cursor.fetchone()["out_of_stock"] or 0

    # הפריט הנמכר ביותר
    cursor.execute(f"""
        SELECT sku, SUM(quantity) AS total_sold 
        FROM purchases 
        {purchase_filter}
        GROUP BY sku 
        ORDER BY total_sold DESC 
        LIMIT 1
    """, purchase_params)
    row = cursor.fetchone()
    bestseller = (row["sku"], row["total_sold"]) if row else ("-", 0)

    # מכירות ב־30 ימים אחרונים
    cursor.execute(f"""
        SELECT SUM(total_price) AS total 
        FROM purchases 
        {purchase_filter + ' AND ' if purchase_filter else 'WHERE '}
        purchase_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    """, purchase_params)
    sales_30_days = cursor.fetchone()["total"] or 0

    # הוצאות
    cursor.execute(f"""
        SELECT SUM(total_cost) AS total 
        FROM expenses e 
        {expense_filter}
    """, inv_exp_params)
    expenses = cursor.fetchone()["total"] or 0

    # רווחים כוללים
    cursor.execute(f"""
        SELECT SUM(total_price) AS total 
        FROM purchases 
        {purchase_filter}
    """, purchase_params)
    total_income = cursor.fetchone()["total"] or 0

    profit = total_income
    net_profit = total_income - expenses

    # מלאי לפי סניפים (גרף בר)
    cursor.execute("""
        SELECT b.branch_name, SUM(i.quantity) AS total 
        FROM inventory i
        JOIN branches b ON i.branch_id = b.branch_id 
        WHERE i.is_active = 1
        GROUP BY b.branch_name
    """)
    branch_inventory = {row["branch_name"]: row["total"] for row in cursor.fetchall()}

    # קטגוריות מלאי (גרף עוגה)
    cursor.execute(f"""
        SELECT category, SUM(quantity) AS qty 
        FROM inventory i 
        {inventory_filter}
        GROUP BY category
    """, inv_exp_params)
    category_data = {row["category"]: row["qty"] for row in cursor.fetchall()}

    # הכנסות לפי חודש
    cursor.execute(f"""
        SELECT DATE_FORMAT(purchase_date, '%Y-%m') AS month, 
               SUM(total_price) AS income
        FROM purchases
        {purchase_filter}
        GROUP BY month
        ORDER BY month
    """, purchase_params)
    income_per_month = {row["month"]: row["income"] for row in cursor.fetchall()}

    # הוצאות לפי חודש
    cursor.execute(f"""
        SELECT DATE_FORMAT(expense_date, '%Y-%m') AS month, 
               SUM(total_cost) AS cost
        FROM expenses e
        {expense_filter}
        GROUP BY month
        ORDER BY month
    """, inv_exp_params)
    expense_per_month = {row["month"]: row["cost"] for row in cursor.fetchall()}

    # טופ 5 פריטים
    cursor.execute(f"""
        SELECT sku, SUM(quantity) AS total_sold 
        FROM purchases 
        {purchase_filter}
        GROUP BY sku 
        ORDER BY total_sold DESC 
        LIMIT 5
    """, purchase_params)
    top_items = [(row["sku"], row["total_sold"]) for row in cursor.fetchall()]

    # הכנסות והוצאות חודשיות
    months = sorted(set(income_per_month.keys()) | set(expense_per_month.keys()))
    monthly_finance = {
        m: (
            income_per_month.get(m, 0),
            expense_per_month.get(m, 0)
        )
        for m in months
    }

    # מכירות לפי חודש
    monthly_sales = {m: v[0] for m, v in monthly_finance.items()}

    # גידול במכירות ורווחים בין חודשיים אחרונים
    sorted_months = sorted(monthly_sales.keys())
    if len(sorted_months) >= 2:
        last, current = sorted_months[-2], sorted_months[-1]
        sales_growth = (monthly_sales[current], monthly_sales[last])
        profit_growth = (monthly_finance[current][0], monthly_finance[last][0])
    else:
        sales_growth = (0, 0)
        profit_growth = (0, 0)

    conn.close()

    return {
        "total_inventory": total_inventory,
        "overstock_items": overstock_items,
        "out_of_stock": out_of_stock,
        "bestseller": bestseller,
        "sales_30_days": sales_30_days,
        "profit": profit,
        "expenses": expenses,
        "net_profit": net_profit,
        "category_data": category_data,
        "branch_inventory": branch_inventory,
        "monthly_sales": monthly_sales,
        "monthly_finance": monthly_finance,
        "sales_growth": sales_growth,
        "profit_growth": profit_growth,
        "top_items": top_items,
    }


# ============================ פונקציות עזר ============================

def create_chart_frame(parent, title, row=0, column=0):
    frame = tk.LabelFrame(
        parent, text=title, font=("Segoe UI", 11, "bold"),
        bg="white", width=380, height=330,
        labelanchor="n", bd=1, relief="solid"
    )
    frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
    frame.grid_propagate(False)
    frame.columnconfigure(0, weight=1)
    return frame

def draw_top_items(items, frame):
    for sku, qty in items:
        row = tk.Frame(frame, bg="white")
        row.pack(fill="x", padx=10, pady=2)
        tk.Label(row, text=sku, bg="white", anchor="w",
                 font=("Segoe UI", 10)).pack(side="right", fill="x", expand=True)
        qty_str = f"{qty:,}" if isinstance(qty, (int, float)) else str(qty)
        tk.Label(row, text=qty_str, bg="white", anchor="e",
                 font=("Segoe UI", 10, "bold"), fg="#007ACC").pack(side="left")

def draw_pie_chart(data, frame, title):
    plt.rcParams['font.family'] = 'Arial'
    fig, ax = plt.subplots(figsize=(3.5, 2))
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%',
           startangle=140, textprops={'fontsize': 10})
    ax.axis('equal')
    fig.tight_layout()
    show_chart(fig, frame)

def draw_bar_chart(data, frame, title):
    plt.rcParams['font.family'] = 'Arial'
    fig, ax = plt.subplots(figsize=(4, 2.5))  # מתאים לרוחב 550px
    ax.bar(data.keys(), data.values(), color="#007ACC")
    ax.tick_params(axis='x', labelrotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout()
    show_chart(fig, frame)

def draw_line_chart(data, frame, title):
    plt.rcParams['font.family'] = 'Arial'
    fig, ax = plt.subplots(figsize=(4, 2.5))  # מתאים לרוחב 550px
    ax.plot(list(data.keys()), list(data.values()), marker='o',
            color="#28A745", linewidth=2)
    ax.tick_params(axis='x', labelrotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout()
    show_chart(fig, frame)

def draw_double_line_chart(data, frame, title):
    plt.rcParams['font.family'] = 'Arial'
    fig, ax = plt.subplots(figsize=(4, 2.5))  # מתאים לרוחב 550px
    months = list(data.keys())
    income = [v[0] for v in data.values()]
    expenses = [v[1] for v in data.values()]
    ax.plot(months, income, label="הכנסות", marker='o', color="#28A745", linewidth=2)
    ax.plot(months, expenses, label="הוצאות", marker='o', color="#DC3545", linewidth=2)
    ax.legend(fontsize=9, loc="upper right")
    ax.tick_params(axis='x', labelrotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout()
    show_chart(fig, frame)

def draw_growth_chart(labels, values, frame):
    plt.rcParams['font.family'] = 'Arial'
    fig, ax = plt.subplots(figsize=(4, 2.5))  # מתאים לרוחב 550px
    ax.plot(labels, values, marker='o', color="#FFA500", linewidth=2)
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_ylabel("% שינוי", fontsize=10)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, fontsize=9)
    ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout()
    show_chart(fig, frame)

def show_chart(fig, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.grid(row=0, column=0, padx=10, pady=10)
    plt.close(fig)

def format_stat_with_growth(title, current, previous, icon):
    try:
        growth = ((current - previous) / previous * 100) if previous else 0
    except ZeroDivisionError:
        growth = 0
    arrow = "🔼" if growth >= 0 else "🔽"
    color = "#28A745" if growth >= 0 else "#DC3545"
    text = f"{icon} {title}:\n{current:,} {arrow} {abs(growth):.1f}%"
    return text, color

def calculate_growth_rate(monthly_data):
    labels = list(monthly_data.keys())
    values = list(monthly_data.values())
    growth = []
    for i in range(1, len(values)):
        prev = values[i - 1]
        curr = values[i]
        rate = ((curr - prev) / prev * 100) if prev else 0
        growth.append(rate)
    return labels[1:], growth

# ============================ דשבורד ראשי ============================
def open_modern_dashboard(tree_frame):
    # ניקוי המסך
    for widget in tree_frame.winfo_children():
        widget.destroy()

    tree_frame.configure(bg="white")

    # סינון סניף
    top_frame = tk.Frame(tree_frame, bg="white")
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="בחר סניף:", bg="white", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=5)
    branch_cb = ttk.Combobox(top_frame, state="readonly", width=30, font=("Segoe UI", 11))
    branches = fetch_branches()
    branch_cb["values"] = ["כל הסניפים"] + [f"{b[0]} - {b[1]}" for b in branches]
    branch_cb.current(0)
    branch_cb.pack(side=tk.LEFT, padx=5)

    # כותרת לסניף
    branch_label = tk.Label(tree_frame, text="נתוני כלל הסניפים", bg="white",
                            font=("Segoe UI", 12, "bold"), fg="#1b75bb")
    branch_label.pack(pady=(5, 0))

    # סטטיסטיקות
    stats_frame = tk.Frame(tree_frame, bg="white")
    stats_frame.pack(fill="x", padx=20, pady=10)

    # אזור הגרפים
    charts_frame = tk.Frame(tree_frame, bg="white")
    charts_frame.pack(fill="both", expand=True, padx=20, pady=5)

    # גרידים נכונים
    charts_frame.grid_rowconfigure((0, 1), weight=1)
    charts_frame.grid_columnconfigure((0, 1, 2), weight=1)

    # שורה עליונה
    pie_frame = create_chart_frame(charts_frame, "התפלגות מלאי", row=0, column=0)
    bar_frame = create_chart_frame(charts_frame, "מלאי לפי סניפים", row=0, column=1)
    top_items_frame = create_chart_frame(charts_frame, "הנמכרים ביותר", row=0, column=2)

    # שורה תחתונה
    sales_frame = create_chart_frame(charts_frame, "מכירות לפי חודש", row=1, column=0)
    inventory_to_sales_frame = create_chart_frame(charts_frame, "ניתוח מלאי מול מכירות", row=1, column=1)
    movement_frame = create_chart_frame(charts_frame, "שיעור שינוי במכירות", row=1, column=2)

    # === פונקציית רענון הדשבורד לפי סניף ===
    def refresh_dashboard(event=None):
        selected = branch_cb.get()
        branch_id = None
        if selected != "כל הסניפים":
            branch_id = int(selected.split(" - ")[0])
            branch_label.config(text=f"נתוני סניף: {selected.split(' - ')[1]}")
        else:
            branch_label.config(text="נתוני כלל הסניפים")
        data = generate_demo_data(branch_id)
        update_ui(data)

    # === עדכון ממשק הדשבורד ===
    def update_ui(data):
        # ניקוי כל הקובצי תצוגה הקודמים
        for frame in [stats_frame, pie_frame, bar_frame, top_items_frame,
                      sales_frame, inventory_to_sales_frame, movement_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

        # הצגת כרטיסי סטטיסטיקה
        sales_text, sales_color = format_stat_with_growth("מכירות 30 ימים", *data["sales_growth"], "🛒")
        profit_text, profit_color = format_stat_with_growth("רווחים", *data["profit_growth"], "💰")
        bestseller_sku, bestseller_qty = data.get("bestseller", ("-", 0))

        stats = [
            ("סה\"כ מלאי", f"{data['total_inventory']:,}", "📦", "#007ACC"),
            ("עודף מלאי", str(data['overstock_items']), "📈", "#28A745"),
            ("חוסרים", str(data['out_of_stock']), "⚠️", "#DC3545"),
            ("הנמכר ביותר", f"{bestseller_sku} ({bestseller_qty})", "🏆", "#17A2B8"),
            (sales_text, "", "", sales_color),
            (profit_text, "", "", profit_color),
            ("הוצאות", f"₪{data['expenses']:,}", "💸", "#DC3545"),
            ("רווח נקי", f"₪{data['net_profit']:,}", "🧾", "#FFC107"),
        ]

        for title, value, icon, color in stats:
            card = tk.Frame(stats_frame, bg="white", width=190, height=80, bd=1, relief="solid")
            card.pack(side="left", padx=10)
            card.pack_propagate(False)
            tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg="white", fg="#555").pack(anchor="nw", padx=10)
            tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg="white", fg=color).pack(anchor="nw", padx=10)
            if icon:
                tk.Label(card, text=icon, font=("Segoe UI", 9), bg="white", fg="gray").pack(anchor="nw", padx=10)

        # הצגת גרפים
        draw_pie_chart(data["category_data"], pie_frame, "קטגוריות")
        draw_bar_chart(data["branch_inventory"], bar_frame, "סניפים")
        draw_top_items(data["top_items"], top_items_frame)
        draw_line_chart(data["monthly_sales"], sales_frame, "מכירות")
        draw_double_line_chart(data["monthly_finance"], inventory_to_sales_frame, "מכירות לעומת מלאי")
        labels, values = calculate_growth_rate(data["monthly_sales"])
        draw_growth_chart(labels, values, movement_frame)

    # קישור קומבובוקס
    branch_cb.bind("<<ComboboxSelected>>", refresh_dashboard)

    # הצגת דשבורד ראשוני
    refresh_dashboard()

