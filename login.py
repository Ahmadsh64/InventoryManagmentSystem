from PIL import Image
from tkinter import messagebox
from database import connect_to_database
from main_window import open_main_window
import os
import tkinter as tk
from tkinter import ttk
def create_login_window():
    def open_role_login(role):
        global entry_username, entry_password, entry_ID
        for widget in login_window.winfo_children():
            widget.destroy()

        role_name = {"manager": "מנהל", "worker": "עובד", "customer": "לקוח"}.get(role, role)
        ttk.Label(login_window, text=f"התחברות - {role_name}", font=("Arial", 18, "bold"), background="#4169E1",
                  foreground="#2c3e50").pack(pady=100)

        frame = ttk.Frame(login_window)
        frame.pack(pady=20, padx=40)

        if role in ["manager", "worker"]:
            ttk.Label(frame, text="שם משתמש:").grid(row=0, column=0, padx=50, pady=10)
            entry_username = ttk.Entry(frame)
            entry_username.grid(row=0, column=1, padx=50, pady=10)

            ttk.Label(frame, text="סיסמה:").grid(row=1, column=0, padx=50, pady=10)
            entry_password = ttk.Entry(frame, show="*")
            entry_password.grid(row=1, column=1, padx=50, pady=10)

            ttk.Button(frame, text="התחבר", command=lambda: login(role)).grid(row=2, columnspan=2, pady=10)
            ttk.Button(frame, text="שכחתי סיסמה", command=forgot_password).grid(row=3, columnspan=2, pady=10)

            if role == "manager":
                ttk.Button(frame, text="צור משתמש חדש", command=create_new_user).grid(row=4, columnspan=2, pady=10)

        elif role == "customer":
            ttk.Label(frame, text="הזן שם או מזהה:").pack(pady=10)
            entry_ID = ttk.Entry(frame)
            entry_ID.pack(pady=10)

            ttk.Button(frame, text="התחבר", command=customer_login).pack(pady=10)
            ttk.Button(frame, text="צור חשבון חדש", command=register_customer).pack(pady=10)

    def login(role):
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                messagebox.showinfo("הצלחה", f"ברוך הבא {user[1]}!")  # user[1] = first_name
                login_window.destroy()
                open_main_window(user_type=role, user_info=user)
            else:
                messagebox.showerror("שגיאה", "פרטי התחברות שגויים")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה במסד הנתונים: {e}")

    def forgot_password():
        win = tk.Toplevel(login_window)
        win.title("שחזור סיסמה")
        win.geometry("400x250")

        ttk.Label(win, text="הזן את המייל או הטלפון שלך לשחזור סיסמה").pack(pady=10)
        entry_contact = ttk.Entry(win)
        entry_contact.pack(pady=10)

        def reset_password():
            contact = entry_contact.get().strip()
            if not contact:
                messagebox.showerror("שגיאה", "אנא הזן מייל או טלפון")
                return

            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute("SELECT employee_id FROM employees WHERE phone_number=%s OR email=%s", (contact, contact))
                user = cursor.fetchone()

                if not user:
                    messagebox.showerror("שגיאה", "משתמש לא נמצא עם פרטים אלה")
                    conn.close()
                    return

                # פותחים חלון חדש להזנת סיסמה חדשה
                def submit_new_password():
                    new_password = entry_new_password.get().strip()
                    if not new_password:
                        messagebox.showerror("שגיאה", "אנא הזן סיסמה חדשה")
                        return
                    try:
                        cursor.execute("UPDATE employees SET password=%s WHERE employee_id=%s", (new_password, user[0]))
                        conn.commit()
                        messagebox.showinfo("הצלחה", "הסיסמה עודכנה בהצלחה!")
                        win.destroy()
                        conn.close()
                    except Exception as e:
                        messagebox.showerror("שגיאה", f"שגיאה בעדכון הסיסמה: {e}")

                # חלון הזנת סיסמה חדשה
                password_window = tk.Toplevel(win)
                password_window.title("הזן סיסמה חדשה")
                password_window.geometry("400x200")

                ttk.Label(password_window, text="הזן סיסמה חדשה:").pack(pady=10)
                entry_new_password = ttk.Entry(password_window, show="*")
                entry_new_password.pack(pady=10)

                ttk.Button(password_window, text="עדכן סיסמה", command=submit_new_password).pack(pady=20)

            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה במסד הנתונים: {e}")

        ttk.Button(win, text="אפס סיסמה", command=reset_password).pack(pady=20)

    def create_new_user():
        create_win = tk.Toplevel(login_window)
        create_win.title("צור משתמש חדש")
        create_win.geometry("500x600")

        fields = {}

        def add_label_and_entry(text, show=None):
            ttk.Label(create_win, text=text).pack(pady=5)
            entry = ttk.Entry(create_win, show=show)
            entry.pack(pady=5)
            return entry

        # תפקיד
        ttk.Label(create_win, text="בחר תפקיד:").pack(pady=5)
        role_var = tk.StringVar(value="worker")
        ttk.Radiobutton(create_win, text="manager", variable=role_var, value="manager").pack()
        ttk.Radiobutton(create_win, text="worker", variable=role_var, value="worker").pack()

        fields['first_name'] = add_label_and_entry("שם פרטי:")
        fields['last_name'] = add_label_and_entry("שם משפחה:")
        fields['address'] = add_label_and_entry("כתובת:")
        fields['phone'] = add_label_and_entry("מספר טלפון:")
        fields['email'] = add_label_and_entry("מייל:")
        fields['username'] = add_label_and_entry("שם משתמש:")
        fields['password'] = add_label_and_entry("סיסמה:", show="*")
        fields['hourly_rate'] = add_label_and_entry("תעריף לשעה:")
        fields['branch'] = add_label_and_entry("סניף:")

        def submit():
            # בדיקות בסיסיות
            for key, entry in fields.items():
                if not entry.get().strip():
                    messagebox.showerror("שגיאה", f"השדה '{key}' לא יכול להיות ריק")
                    return
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO employees 
                (first_name, last_name, address, phone_number, email, username, password, hourly_rate, branch_id, role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        fields['first_name'].get().strip(),
                        fields['last_name'].get().strip(),
                        fields['address'].get().strip(),
                        fields['phone'].get().strip(),
                        fields['email'].get().strip(),
                        fields['username'].get().strip(),
                        fields['password'].get().strip(),
                        fields['hourly_rate'].get().strip(),
                        fields['branch'].get().strip(),
                        role_var.get()
                    )
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("הצלחה", "משתמש נוצר בהצלחה!")
                create_win.destroy()
            except Exception as e:
                messagebox.showerror("שגיאה", f"לא ניתן ליצור משתמש: {e}")

        ttk.Button(create_win, text="צור משתמש", command=submit).pack(pady=20)

    def customer_login():
        identifier = entry_ID.get().strip()

        if not identifier:
            messagebox.showerror("שגיאה", "אנא הזן שם או מספר מזהה")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # בדיקה לפי מזהה מספרי או שם
            if identifier.isdigit():
                cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (identifier,))
            else:
                cursor.execute("SELECT * FROM customers WHERE customer_name = %s", (identifier,))

            customer = cursor.fetchone()
            conn.close()

            if customer:
                messagebox.showinfo("הצלחה", f"ברוך הבא {customer[1]}!")
                login_window.destroy()
                open_main_window(user_type="customer", user_info=customer)
            else:
                messagebox.showerror("שגיאה", "לקוח לא נמצא במערכת")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה במסד הנתונים: {e}")

    def register_customer():
        win = tk.Toplevel(login_window)
        win.title("רישום לקוח חדש")
        win.geometry("400x400")

        entries = {}

        for label_text in ["שם לקוח:", "טלפון:", "מייל:"]:
            ttk.Label(win, text=label_text).pack(pady=5)
            entry = ttk.Entry(win)
            entry.pack(pady=5)
            entries[label_text] = entry

        def submit_customer():
            name = entries["שם לקוח:"].get().strip()
            phone = entries["טלפון:"].get().strip()
            email = entries["מייל:"].get().strip()

            if not name or not phone or not email:
                messagebox.showerror("שגיאה", "אנא מלא את כל השדות")
                return

            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO customers (customer_name, phone_number, email) VALUES (%s, %s, %s)",
                    (name, phone, email)
                )
                conn.commit()
                cursor.execute("SELECT * FROM customers WHERE customer_id = LAST_INSERT_ID()")
                new_customer = cursor.fetchone()
                conn.close()

                messagebox.showinfo("הצלחה", f"הלקוח נרשם בהצלחה! מזהה לקוח: {new_customer[0]}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה ברישום לקוח: {e}")

        ttk.Button(win, text="רשום לקוח", command=submit_customer).pack(pady=20)

    # --- ממשק ראשי של login ---
    global login_window
    login_window = tk.Tk()
    login_window.title("מסך כניסה")
    login_window.geometry("500x600")
    login_window.config(bg="#4169E1")

    logo_img = tk.PhotoImage(file="static/images/LOGO-FOX.png")
    logo_img = logo_img.subsample(5, 5)

    logo_label = ttk.Label(login_window, image=logo_img, background="#4169E1")
    logo_label.image = logo_img  # חשוב: שמירת הפניה לתמונה
    logo_label.place(x=10, y=10)

    title_label = ttk.Label(login_window, text=":כניסה בתור", font=("Arial", 18, "bold"), background="#4169E1",
                            foreground="#2c3e50")
    title_label.pack(pady=110)

    ttk.Button(login_window, text="כניסת מנהל", command=lambda: open_role_login("manager")).pack(pady=10, fill="x", padx=60)
    ttk.Button(login_window, text="כניסת עובד", command=lambda: open_role_login("worker")).pack(pady=10, fill="x", padx=60)
    ttk.Button(login_window, text="כניסת לקוח", command=lambda: open_role_login("customer")).pack(pady=10, fill="x", padx=60)

    login_window.mainloop()