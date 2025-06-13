import os
import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_to_database

from PIL import Image, ImageTk

def open_report_window(tree_frame):
    for widget in tree_frame.winfo_children():
        widget.destroy()

    def generate_report():
        report_type = report_combobox.get()
        if not report_type:
            messagebox.showerror("שגיאה", "אנא בחר סוג דוח")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            global report_file_name

            if report_type == "דוח מלאי":
                cursor.execute("""
                    SELECT i.sku, i.item_name, i.category, i.quantity, i.price, i.color, i.size,
                           i.shelf_row, i.shelf_column, b.branch_name, b.branch_address, i.last_updated
                    FROM inventory i
                    INNER JOIN branches b ON i.branch_id = b.branch_id
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "SKU", "Item Name", "Category", "Quantity", "Price", "Color", "Size",
                    "Shelf Row", "Shelf Column", "Branch Name", "Branch Address", "Last Updated"
                ])
                report_file_name = "דוח_מלאי.xlsx"

            elif report_type == "דוח מכירות (רכישות)":
                cursor.execute("""
                    SELECT p.customer_id, p.customer_name, c.phone_number, c.email, p.item_name, p.quantity, 
                           p.total_price, p.purchase_date, p.color, p.size, p.branch_name 
                    FROM Purchases p 
                    INNER JOIN Customers c ON p.customer_name = c.customer_name
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "Customer ID", "Customer Name", "Phone Number", "Email", "Item Name",
                    "Quantity", "Total Price", "Purchase Date", "Color", "Size", "Branch Name"
                ])
                df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])
                report_file_name = "דוח_רכישות.xlsx"

            elif report_type == "דוח חוסרים במלאי":
                cursor.execute("""
                    SELECT i.sku, i.item_name, i.quantity, b.branch_name, i.category, i.last_updated
                    FROM inventory i
                    INNER JOIN branches b ON i.branch_id = b.branch_id
                    WHERE i.quantity <= 100 
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "SKU", "Item Name", "Quantity", "Branch Name", "Category", "Last Updated"
                ])
                report_file_name = "דוח_חוסרים.xlsx"

            elif report_type == "דוח הזמנות":
                cursor.execute("""
                    SELECT e.expense_id, b.branch_name, e.sku, e.item_name,
                           e.quantity_added, e.unit_price, e.total_cost, e.expense_date
                    FROM expenses e
                    INNER JOIN branches b ON e.branch_id = b.branch_id
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "Expense ID", "Branch Name", "SKU", "Item Name",
                    "Quantity Added", "Unit Price", "Total Cost", "Expense Date"
                ])
                df['Expense Date'] = pd.to_datetime(df['Expense Date'])
                report_file_name = "דוח_הזמנות.xlsx"

            elif report_type == "דוח שולי רווח":
                cursor.execute("""
                    SELECT p.item_name, SUM(p.total_price) AS total_sales
                    FROM purchases p
                    GROUP BY p.item_name
                """)
                sales = cursor.fetchall()
                sales_df = pd.DataFrame(sales, columns=["Item Name", "Total Sales"])

                cursor.execute("""
                    SELECT e.item_name, SUM(e.total_cost) AS total_expense
                    FROM expenses e
                    GROUP BY e.item_name
                """)
                expenses = cursor.fetchall()
                expenses_df = pd.DataFrame(expenses, columns=["Item Name", "Total Expense"])

                df = pd.merge(sales_df, expenses_df, on="Item Name", how="left").fillna(0)
                df['Profit'] = df['Total Sales'] - df['Total Expense']
                report_file_name = "דוח_שולי_רווח.xlsx"

            elif report_type == "דוח מלאי חודשי":
                cursor.execute("""
                    SELECT MONTH(p.purchase_date) AS month, p.item_name, SUM(p.quantity) AS total_purchases
                    FROM purchases p
                    GROUP BY month, p.item_name
                """)
                purchases = cursor.fetchall()
                purchases_df = pd.DataFrame(purchases, columns=["Month", "Item Name", "Total Purchases"])

                cursor.execute("""
                    SELECT MONTH(e.expense_date) AS month, e.item_name, SUM(e.quantity_added) AS total_restocks
                    FROM expenses e
                    GROUP BY month, e.item_name
                """)
                restocks = cursor.fetchall()
                restocks_df = pd.DataFrame(restocks, columns=["Month", "Item Name", "Total Restocks"])

                df = pd.merge(purchases_df, restocks_df, on=["Month", "Item Name"], how="outer").fillna(0)
                df['Balance'] = df['Total Restocks'] - df['Total Purchases']
                df['Month'] = df['Month'].astype(int)
                report_file_name = "דוח_מלאי_חודשי.xlsx"

            elif report_type == "דוח עודפים במלאי":
                cursor.execute("""
                    SELECT i.sku, i.item_name, b.branch_name, i.quantity, i.price, i.received_date, i.is_active,
                           IFNULL(SUM(p.quantity), 0), TIMESTAMPDIFF(MONTH, i.received_date, CURDATE())
                    FROM inventory i
                    JOIN branches b ON i.branch_id = b.branch_id
                    LEFT JOIN purchases p ON i.sku = p.sku AND p.purchase_date >= i.received_date
                    GROUP BY i.sku
                    HAVING i.quantity > 100 AND SUM(p.quantity) < 100 AND TIMESTAMPDIFF(MONTH, i.received_date, CURDATE()) >= 1
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "SKU", "Item Name", "Branch Name", "Quantity", "Price", "Received Date", "Is Active", "Sum Purchased", "Months"
                ])
                df['Received Date'] = pd.to_datetime(df['Received Date'])
                report_file_name = "דוח_עודפים.xlsx"

            else:
                messagebox.showerror("שגיאה", "סוג דוח לא נתמך")
                return

            with pd.ExcelWriter(report_file_name, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
                df.to_excel(writer, index=False, sheet_name='דוח')
                workbook = writer.book
                worksheet = writer.sheets['דוח']

                if report_type in ["דוח מלאי", "דוח מכירות (רכישות)", "דוח הזמנות", "דוח מלאי חודשי"]:
                    chart = workbook.add_chart({'type': 'column'})
                    if report_type == "דוח מלאי":
                        chart.add_series({
                            'name': 'כמות במלאי',
                            'categories': f'=דוח!B2:B{len(df)+1}',
                            'values': f'=דוח!D2:D{len(df)+1}',
                        })
                    elif report_type == "דוח מכירות (רכישות)":
                        chart.add_series({
                            'name': 'כמות רכישות',
                            'categories': f'=דוח!E2:E{len(df)+1}',
                            'values': f'=דוח!F2:F{len(df)+1}',
                        })
                    elif report_type == "דוח הזמנות":
                        chart.add_series({
                            'name': 'הזמנות לפי מוצר',
                            'categories': f'=דוח!D2:D{len(df)+1}',
                            'values': f'=דוח!E2:E{len(df)+1}',
                        })
                    elif report_type == "דוח מלאי חודשי":
                        chart.add_series({
                            'name': 'יתרת מלאי חודשית',
                            'categories': f'=דוח!A2:A{len(df)+1}',
                            'values': f'=דוח!E2:E{len(df)+1}',
                        })
                    worksheet.insert_chart('M2', chart)

            messagebox.showinfo("הצלחה", f"הדוח נוצר ונשמר כ־{report_file_name}")
            show_report_Button.config(state=tk.NORMAL)

        except mysql.connector.Error as e:
            messagebox.showerror("שגיאה", f"שגיאה בעת יצירת הדוח: {e}")
        finally:
            if connection:
                connection.close()

    def show_report():
        if report_file_name and os.path.exists(report_file_name):
            os.system(f'open "{report_file_name}"' if os.name == "posix" else f'start {report_file_name}')
        else:
            messagebox.showerror("שגיאה", "הדוח לא נמצא")

    # סטיילינג
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 11), padding=6)
    style.configure("TCombobox", font=("Segoe UI", 11))

    title_label = ttk.Label(tree_frame, text="מערכת דוחות", font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
    title_label.pack(pady=(10, 20))

    report_window_frame = ttk.LabelFrame(tree_frame, text="בחירת דוח", padding=15)
    report_window_frame.pack(padx=15, pady=10, fill="x")

    ttk.Label(report_window_frame, text="בחר סוג דוח:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    report_combobox = ttk.Combobox(report_window_frame, values=[
        "דוח מלאי", "דוח מכירות (רכישות)", "דוח חוסרים במלאי",
        "דוח הזמנות", "דוח שולי רווח", "דוח מלאי חודשי", "דוח עודפים במלאי"
    ], state="readonly", width=30)
    report_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    create_button = ttk.Button(report_window_frame, text="צור דוח", command=generate_report)
    create_button.grid(row=1, column=0, columnspan=2, pady=15)

    show_report_Button = ttk.Button(tree_frame, text="הצג דוח", command=show_report, state=tk.DISABLED)
    show_report_Button.pack(pady=(0, 15))
