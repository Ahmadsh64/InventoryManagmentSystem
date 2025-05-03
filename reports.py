import os
import shutil
from datetime import datetime

import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import connect_to_database
from PIL import Image, ImageTk, ImageDraw

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

            if report_type == "דוח מלאי":
                cursor.execute("""
                    SELECT inventory.sku, inventory.item_name, inventory.category, inventory.quantity, inventory.price, inventory.color, 
                           inventory.size, inventory.shelf_row, inventory.shelf_column, branches.branch_name, branches.branch_address, 
                           inventory.last_updated 
                    FROM inventory_system.inventory 
                    INNER JOIN inventory_system.branches ON inventory.branch_id = branches.branch_id
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "SKU", "item_name", "category", "quantity", "price", "color", "size",
                    "shelf_row", "shelf_column", "branch_name", "branch_address", "last_updated"
                ])

                global report_file_name
                report_file_name = "דוח_מלאי.xlsx"

                # יצירת קובץ Excel עם גרף
                # יצירת קובץ Excel עם גרף
                with pd.ExcelWriter(report_file_name, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
                    df.to_excel(writer, index=False, sheet_name='מלאי')
                    workbook = writer.book
                    worksheet = writer.sheets['מלאי']

                    # הפיכת עמודת תאריך לעמודת טקסט/תאריך
                    df['last_updated'] = pd.to_datetime(df['last_updated'])

                    # הוספת גרף מסוג עמודות – תאריך מול כמות
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name': 'כמות לפי תאריך',
                        'categories': f'=מלאי!L$2:$L${len(df) + 1}',  # last_updated
                        'values': f'=מלאי!$D$2:$D${len(df) + 1}',  # quantity
                    })
                    chart.set_title({'name': 'גרף כמות לפי תאריך עדכון'})
                    chart.set_x_axis({'name': 'תאריך עדכון'})
                    chart.set_y_axis({'name': 'כמות'})

                    worksheet.insert_chart('N2', chart)


            elif report_type == "דוח רכישות":
                cursor.execute("""
                    SELECT p.customer_id, p.customer_name, c.phone_number, c.email, p.item_name, p.quantity, 
                           p.total_price, p.purchase_date, p.color, p.size, p.branch_name 
                    FROM inventory_system.Purchases p 
                    INNER JOIN inventory_system.Customers c ON p.customer_name = c.customer_name
                """)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[
                    "Customer ID", "Customer Name", "Phone Number", "Email", "Item Name",
                    "Quantity", "Total Price", "Purchase Date", "Color", "Size", "Branch Name"
                ])

                report_file_name = "דוח_רכישות.xlsx"
                # המרת תאריך
                df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])

                # שמירת דוח + גרף
                with pd.ExcelWriter(report_file_name, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
                    df.to_excel(writer, index=False, sheet_name='רכישות')
                    workbook = writer.book
                    worksheet = writer.sheets['רכישות']

                    # גרף עמודות לפי תאריך רכישה מול כמות
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name': 'כמות רכישות לפי תאריך',
                        'categories': f'=רכישות!H$2:H${len(df) + 1}',  # Purchase Date
                        'values': f'=רכישות!F$2:F${len(df) + 1}',  # Quantity
                    })

                    chart.set_title({'name': 'כמות רכישות לפי תאריך'})
                    chart.set_x_axis({'name': 'תאריך רכישה'})
                    chart.set_y_axis({'name': 'כמות'})

                    worksheet.insert_chart('L2', chart)

            messagebox.showinfo("הצלחה", f"הדוח נוצר ונשמר כ-{report_file_name}")
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
            messagebox.showerror("שגיאה", "הדוח הזה לא נמצא")

    report_window_frame = tk.LabelFrame(tree_frame, text="בחר סוג דוח")
    report_window_frame.pack(padx=10, pady=10)

    ttk.Label(report_window_frame, text="סוג דוח:").grid(row=0, column=0, padx=5, pady=5)
    report_combobox = ttk.Combobox(report_window_frame, values=["דוח מלאי", "דוח רכישות"], state="readonly")
    report_combobox.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(report_window_frame, text="צור דוח", command=generate_report).grid(row=1, column=0, columnspan=2, pady=10)

    show_report_Button = ttk.Button(tree_frame, text="הצג דוח", command=show_report, state=tk.DISABLED)
    show_report_Button.pack(pady=5)

