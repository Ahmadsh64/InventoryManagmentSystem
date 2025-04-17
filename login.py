import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from database import connect_to_database
from main_window import open_main_window


def create_login_window():
    global login_window
    login_window = tk.Tk()
    login_window.title("מסך כניסה")
    login_window.geometry("500x600")
    login_window.config(bg="#4169E1")

    logo_img = tk.PhotoImage(file="images/LOGO-FOX.png")
    logo_img = logo_img.subsample(5, 5)

    logo_label = ttk.Label(login_window, image=logo_img, background="#4169E1")
    logo_label.place(x=10, y=10)

    title_label = ttk.Label(login_window, text=":כניסה בתור", font=("Arial", 18, "bold"), background="#4169E1",
                            foreground="#2c3e50")
    title_label.pack(pady=110)

    manager_button = ttk.Button(login_window, text="התחבר כמנהל", command=lambda: open_login_window("מנהל"),
                                style="TButton")
    manager_button.pack(fill="x", padx=50, pady=10)

    employee_button = ttk.Button(login_window, text="התחבר כעובד", command=lambda: open_login_window("עובד"),
                                 style="TButton")
    employee_button.pack(fill="x", padx=50, pady=10)

    customer_button = ttk.Button(login_window, text="התחבר כלקוח", command=lambda: open_login_window("לקוח"),
                                 style="TButton")
    customer_button.pack(fill="x", padx=50, pady=10)

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 14), foreground="#2c3e50", background="#3498db", width=20)
    style.map("TButton", background=[('active', '#2980b9')])

    login_window.mainloop()


def open_login_window(user_type):
    global entry_username, entry_password ,entry_ID
    for widget in login_window.winfo_children():
        widget.destroy()

    ttk.Label(login_window, text=f"התחברות - {user_type}", font=("Arial", 18, "bold"), background="#4169E1", foreground="#2c3e50").pack(pady=100)

    if user_type in ["עובד", "מנהל"]:
        frame = ttk.Frame(login_window)
        frame.pack(expand=True)

        ttk.Label(frame, text="שם משתמש:").grid(row=0, column=0, padx=50, pady=10)
        entry_username = ttk.Entry(frame)
        entry_username.grid(row=0, column=1, padx=50, pady=10)

        ttk.Label(frame, text="סיסמה:").grid(row=1, column=0, padx=50, pady=10)
        entry_password = ttk.Entry(frame, show="*")
        entry_password.grid(row=1, column=1, padx=50, pady=10)

        if user_type == "מנהל":
            ttk.Button(frame, text="התחבר", command=admin_login).grid(row=2, column=0, columnspan=2, pady=10)
        elif user_type == "עובד":
            tk.Button(frame, text="התחבר", command=worker_login).grid(row=2, column=0, columnspan=2, pady=10)
    elif user_type == "לקוח":
        frame = ttk.Frame(login_window)
        frame.pack(expand=True)
        ttk.Label(frame, text="שם משתמש או מס' מזהה").grid(row=0, column=0, padx=50, pady=10)
        entry_ID = ttk.Entry(frame)
        entry_ID.grid(row=0, column=1, padx=50, pady=10)

        ttk.Button(frame, text="התחבר", command=customer_login).grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="יצירת חשבון חדש", command=register_customer).grid(row=2, column=0, columnspan=2, pady=10)


def admin_login():
    username = entry_username.get()
    password = entry_password.get()
    if username == "admin" and password == "1234":
        messagebox.showinfo("התחברת בהצלחה!", "ברוך הבא")
        login_window.destroy()
        open_main_window(user_type="admin")
    else:
        messagebox.showerror("שגיאה!", "שם משתמש או סיסמה שגויים")



def worker_login():
    user_name = entry_username.get()
    password = entry_password.get()
    if user_name == "worker" and password == "5678":
        messagebox.showinfo("התחברת בהצלחה כעובד", "ברוך הבא")
        login_window.destroy()
        open_main_window(user_type="worker")
    else:
        messagebox.showerror("שגיאה!", "שם משתמש או סיסמה שגויים")


def customer_login():
    ID = entry_ID.get()
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE customer_id = %s OR customer_name = %s", (ID, ID))
    customer = cursor.fetchone()
    conn.close()

    if customer:
        messagebox.showinfo("ברוך הבא, לקוח", "בהצלחה")
        login_window.destroy()
        open_main_window(user_type="customer")
    else:
        messagebox.showerror("שגיאה", "שם משתמש או מס' מזהה לא נמצאו במערכת")

def register_customer():
    def submit_registration():
        name = entry_name.get()
        phone = entry_phone.get()
        email = entry_email.get()

        if not name or not phone or not email:
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (customer_name, phone_number, email) VALUES (%s, %s, %s)",
                           (name, phone, email))
            conn.commit()
            messagebox.showinfo("הצלחה", "החשבון נוצר בהצלחה")
            register_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("שגיאה", f"שגיאה במסד הנתונים: {err}")
        finally:
            conn.close()

    register_window = tk.Toplevel()
    register_window.title("רישום לקוח חדש")
    register_window.geometry("400x300")

    ttk.Label(register_window, text="שם מלא:").pack(pady=5)
    entry_name = ttk.Entry(register_window)
    entry_name.pack(pady=5)

    ttk.Label(register_window, text="מספר טלפון").pack(pady=5)
    entry_phone = ttk.Entry(register_window)
    entry_phone.pack(pady=5)

    ttk.Label(register_window, text="אימייל").pack(pady=5)
    entry_email = ttk.Entry(register_window)
    entry_email.pack(pady=5)

    ttk.Button(register_window, text="צור חשבון", command=submit_registration).pack(pady=20)


create_login_window()
