import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import connect_to_database
from main_window import open_main_window


# ======================== פונקציה ראשית ========================
def create_login_window():
    global login_window
    login_window = tk.Tk()
    login_window.title("מסך כניסה")
    login_window.state('zoomed')

    create_left_frame()
    create_right_frame()

    login_window.mainloop()


# ======================== צד שמאל - בחירת תפקיד ========================
def create_left_frame():
    left_frame = tk.Frame(login_window, bg="white")
    left_frame.place(relx=0, rely=0, relwidth=0.35, relheight=1)
    canvas = tk.Canvas(left_frame, highlightthickness=0)
    canvas.place(relwidth=1, relheight=1)

    # לוגו
    try:
        logo_img = tk.PhotoImage(file="static/images/LOGO-FOX.png").subsample(5, 5)
        tk.Label(left_frame, image=logo_img).pack(pady=(30, 10))
        left_frame.image = logo_img
    except:
        tk.Label(left_frame, text="[Logo Missing]", fg="red", font=("Arial", 20)).pack(pady=30)

    # כותרת
    tk.Label(left_frame, text=":כניסה בתור", font=("Arial", 20, "bold"), fg="red").pack(pady=(10, 30))

    # כפתורי בחירת תפקיד
    roles = {"manager": "כניסת מנהל", "worker": "כניסת עובד", "customer": "כניסת לקוח"}
    for role, text in roles.items():
        tk.Button(left_frame, text=text, command=lambda r=role: open_role_login(r),
                  font=("Arial", 20), bg="red", fg="white", bd=0, cursor="hand2").pack(pady=10, padx=40, fill="x")

    # תוספת: תת כותרת מתחת לכפתורים
    tk.Label(left_frame, text="🌀 StockKeeper\n FOX מערכת ניהול מתקדמת לחנויות",
             font=("Helvetica", 20), fg="red", justify="center").pack(pady=(50, 20))
    # יצירת מסגרת תחתונה לאייקונים
    bottom_frame = tk.Frame(left_frame)
    bottom_frame.pack(side="bottom", fill="x", pady=10)

    # סמל נגישות בצד שמאל
    tk.Label(bottom_frame, text="♿ ", font=("Helvetica", 15), fg="black").pack(side="left", padx=20)

    # כפתור עזרה בצד ימין
    tk.Button(bottom_frame, text="❓", font=("Helvetica", 15), bg="black", fg="white", cursor="hand2", bd=0,
              command=open_help_window).pack(side="right", padx=20)

    # משפט זכויות יוצרים בתחתית
    tk.Label(left_frame, text="© 2025 StockKeeper - כל הזכויות שמורות ל | FOX מערכת ניהול חכמה ומתקדמת לחנויות  ",
             font=("Helvetica", 9), fg="black", justify="center").pack(side="bottom", pady=10)


def open_help_window():
    help_win = tk.Toplevel(login_window)
    help_win.title("עזרה ותמיכה")
    help_win.geometry("400x300")

    tk.Label(help_win, text="ברוך הבא למרכז התמיכה של StockKeeper!", font=("Helvetica", 14)).pack(pady=20)
    tk.Label(help_win, text="במידה ואתה זקוק לעזרה:\n📞 טלפון: 03-1234567\n📧 דוא\"ל: support@stockkeeper.com",
             font=("Helvetica", 12)).pack(pady=10)
    tk.Button(help_win, text="סגור", command=help_win.destroy).pack(pady=20)


# ======================== צד ימין - תמונת רקע וטקסט ========================
def create_right_frame():
    right_frame = tk.Frame(login_window)
    right_frame.place(relx=0.35, rely=0, relwidth=0.65, relheight=1)
    canvas = tk.Canvas(right_frame, highlightthickness=0)
    canvas.place(relwidth=1, relheight=1)

    def update_bg(event=None):
        w, h = right_frame.winfo_width(), right_frame.winfo_height()
        try:
            image = Image.open("static/images/background1.jpg").resize((w, h))
            bg_image = ImageTk.PhotoImage(image)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=bg_image)
            canvas.bg_img = bg_image

            # כותרת ראשית
            canvas.create_text(w // 2, int(h * 0.7),
                               text="🌀StockKeeper \nניהול חכם שליטה מלאה הצלחה מתחילה כאן",
                               font=("Helvetica", int(h * 0.045), "bold"),
                               fill="white", justify="center")

        except:
            canvas.create_text(w // 2, h // 2, text="[Image Load Error]", fill="white")

    login_window.bind("<Configure>", update_bg)


# ======================== פתיחת מסך התחברות לפי תפקיד ========================
def open_role_login(role):
    for widget in login_window.winfo_children():
        widget.destroy()

    left_frame = tk.Frame(login_window, bg="white")
    left_frame.place(relx=0, rely=0, relwidth=0.35, relheight=1)

    role_titles = {"manager": "מנהל", "worker": "עובד", "customer": "לקוח"}
    tk.Label(left_frame, text=f"התחברות - {role_titles.get(role, role)}", font=("Arial", 22, "bold"), bg="white",
             fg="red").pack(pady=(80, 20))

    form_frame = tk.Frame(left_frame, bg="white")
    form_frame.pack(pady=10, padx=40)

    if role in ["manager", "worker"]:
        create_employee_login_form(form_frame, role)
    elif role == "customer":
        create_customer_login_form(form_frame)

    create_right_frame()  # נשאר קבוע


# ======================== טפסים ========================
def create_employee_login_form(frame, role):
    global entry_username, entry_password
    entry_username = create_labeled_entry(frame, "שם משתמש:")
    entry_password = create_labeled_entry(frame, "סיסמה:", show="*")

    tk.Button(frame, text="התחבר", bg="red", fg="white", font=("Helvetica", 20, "bold"),
              command=lambda: employee_login(role), bd=0, cursor="hand2").pack(pady=(30, 10), fill="x")

    tk.Button(frame, text="שכחתי סיסמה", bg="white", fg="red", font=("Helvetica", 20),
              command=forgot_password, bd=0, cursor="hand2").pack()

    if role == "manager":
        tk.Button(frame.master, text="צור משתמש חדש", bg="red", fg="white", font=("Helvetica", 20),
                  command=create_new_user, bd=0, cursor="hand2").pack(pady=10)


def create_customer_login_form(frame):
    global entry_ID
    entry_ID = create_labeled_entry(frame, "הזן שם או מזהה:")

    tk.Button(frame, text="התחבר", bg="#6A0DAD", fg="white", font=("Helvetica", 20, "bold"),
              command=customer_login, bd=0, cursor="hand2").pack(pady=(30, 10), fill="x")
    tk.Button(frame, text="צור חשבון חדש", bg="white", fg="red", font=("Helvetica", 20),
              command=register_customer, bd=0, cursor="hand2").pack()


def create_labeled_entry(frame, label, show=None):
    tk.Label(frame, text=label, bg="white", anchor="w").pack(fill="x", pady=(10, 2))
    entry = tk.Entry(frame, font=("Helvetica", 25), show=show, bd=0, highlightthickness=1, highlightcolor="#6A0DAD")
    entry.pack(fill="x", ipady=6)
    return entry


# ======================== פונקציות לוגיקה ========================
def employee_login(role):
    username, password = entry_username.get().strip(), entry_password.get().strip()
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
            messagebox.showinfo("הצלחה", f"ברוך הבא {user[1]}!")
            login_window.destroy()
            open_main_window(user_type=role, user_info=user)
        else:
            messagebox.showerror("שגיאה", "פרטי התחברות שגויים")
    except Exception as e:
        messagebox.showerror("שגיאה", f"שגיאה במסד הנתונים: {e}")


def customer_login():
    identifier = entry_ID.get().strip()
    if not identifier:
        messagebox.showerror("שגיאה", "אנא הזן שם או מספר מזהה")
        return

    try:
        conn = connect_to_database()
        cursor = conn.cursor()

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


# ======================== שכחתי סיסמה ========================
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


# ======================== יצירת משתמש חדש ========================
def create_new_user():
    win = tk.Toplevel(login_window)
    win.title("צור משתמש חדש")
    win.geometry("500x600")

    fields = {}

    def add_field(label, show=None):
        ttk.Label(win, text=label).pack(pady=5)
        entry = ttk.Entry(win, show=show)
        entry.pack(pady=5)
        fields[label] = entry

    # תפקיד
    role_var = tk.StringVar(value="worker")
    ttk.Label(win, text="בחר תפקיד:").pack(pady=5)
    for role in ["manager", "worker"]:
        ttk.Radiobutton(win, text=role, variable=role_var, value=role).pack()

    add_field("שם פרטי")
    add_field("שם משפחה")
    add_field("כתובת")
    add_field("מספר טלפון")
    add_field("מייל")
    add_field("שם משתמש")
    add_field("סיסמה", show="*")
    add_field("תעריף לשעה")
    add_field("סניף")

    def submit_user():
        values = {label: entry.get().strip() for label, entry in fields.items()}
        if any(not val for val in values.values()):
            messagebox.showerror("שגיאה", "יש למלא את כל השדות")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO employees 
                (first_name, last_name, address, phone_number, email, username, password, hourly_rate, branch_id, role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                values["שם פרטי"], values["שם משפחה"], values["כתובת"],
                values["מספר טלפון"], values["מייל"], values["שם משתמש"],
                values["סיסמה"], values["תעריף לשעה"], values["סניף"], role_var.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("הצלחה", "משתמש נוצר בהצלחה!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן ליצור משתמש: {e}")

    ttk.Button(win, text="צור משתמש", command=submit_user).pack(pady=20)


# ======================== רישום לקוח חדש ========================
def register_customer():
    win = tk.Toplevel(login_window)
    win.title("רישום לקוח חדש")
    win.geometry("400x400")

    fields = {}
    for label in ["שם לקוח", "טלפון", "מייל"]:
        ttk.Label(win, text=label).pack(pady=5)
        entry = ttk.Entry(win)
        entry.pack(pady=5)
        fields[label] = entry

    def submit_customer():
        name, phone, email = (
        fields["שם לקוח"].get().strip(), fields["טלפון"].get().strip(), fields["מייל"].get().strip())
        if not all([name, phone, email]):
            messagebox.showerror("שגיאה", "אנא מלא את כל השדות")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (customer_name, phone_number, email) VALUES (%s, %s, %s)",
                           (name, phone, email))
            conn.commit()
            cursor.execute("SELECT * FROM customers WHERE customer_id = LAST_INSERT_ID()")
            new_customer = cursor.fetchone()
            conn.close()
            messagebox.showinfo("הצלחה", f"הלקוח נרשם בהצלחה! מזהה לקוח: {new_customer[0]}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה ברישום לקוח: {e}")

    ttk.Button(win, text="רשום לקוח", command=submit_customer).pack(pady=20)
