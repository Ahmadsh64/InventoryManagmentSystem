import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from database import connect_to_database
from main_window import open_main_window

ctk.set_appearance_mode("light")  # אפשר גם "dark"
ctk.set_default_color_theme("blue")  # תומך גם ב"green", "dark-blue", "blue"

class LoginApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("FOX | מערכת ניהול מלאי")
        self.window.state('zoomed')
        self.build_login_screen()
        self.window.mainloop()

    def build_login_screen(self):
        # תמונה - לוגו FOX
        logo_image = Image.open("images/LOGO-FOX.png")
        logo_ctk_image = ctk.CTkImage(dark_image=logo_image, size=(100, 100))
        logo_label = ctk.CTkLabel(self.window, image=logo_ctk_image, text="")
        logo_label.pack(pady=20)

        title = ctk.CTkLabel(self.window, text="כניסה למערכת", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=10)

        # כפתורים
        ctk.CTkButton(self.window, text="כניסת מנהל", command=lambda: self.open_role_login("מנהל")).pack(pady=10, fill="x", padx=60)
        ctk.CTkButton(self.window, text="כניסת עובד", command=lambda: self.open_role_login("עובד")).pack(pady=10, fill="x", padx=60)
        ctk.CTkButton(self.window, text="כניסת לקוח", command=lambda: self.open_role_login("לקוח")).pack(pady=10, fill="x", padx=60)

    def open_role_login(self, role):
        for widget in self.window.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.window, text=f"התחברות כ{role}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)

        frame = ctk.CTkFrame(self.window)
        frame.pack(pady=20, padx=40)

        if role in ["מנהל", "עובד"]:
            self.entry_username = ctk.CTkEntry(frame, placeholder_text="שם משתמש")
            self.entry_username.pack(pady=10)
            self.entry_password = ctk.CTkEntry(frame, placeholder_text="סיסמה", show="*")
            self.entry_password.pack(pady=10)

            ctk.CTkButton(frame, text="התחבר", command=lambda: self.login(role)).pack(pady=20)
        elif role == "לקוח":
            self.entry_ID = ctk.CTkEntry(frame, placeholder_text="שם או מספר מזהה")
            self.entry_ID.pack(pady=10)
            ctk.CTkButton(frame, text="התחבר", command=self.customer_login).pack(pady=10)
            ctk.CTkButton(frame, text="צור חשבון חדש", fg_color="gray", command=self.register_customer).pack(pady=10)

    def login(self, role):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if role == "מנהל" and username == "admin" and password == "1234":
            messagebox.showinfo("הצלחה", "ברוך הבא מנהל!")
            self.window.destroy()
            open_main_window(user_type="admin")
        elif role == "עובד" and username == "worker" and password == "5678":
            messagebox.showinfo("הצלחה", "ברוך הבא עובד!")
            self.window.destroy()
            open_main_window(user_type="worker")
        else:
            messagebox.showerror("שגיאה", "פרטי התחברות שגויים")

    def customer_login(self):
        ID = self.entry_ID.get()
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM customers WHERE customer_id = %s OR customer_name = %s", (ID, ID))
        customer = cursor.fetchone()
        conn.close()

        if customer:
            messagebox.showinfo("ברוך הבא", f"שלום {customer[1]}")
            self.window.destroy()
            open_main_window(user_type="customer")
        else:
            messagebox.showerror("שגיאה", "המשתמש לא נמצא")

    def register_customer(self):
        register_win = ctk.CTkToplevel(self.window)
        register_win.title("רישום לקוח חדש")
        register_win.geometry("400x300")

        ctk.CTkLabel(register_win, text="שם מלא:").pack(pady=5)
        entry_name = ctk.CTkEntry(register_win)
        entry_name.pack(pady=5)

        ctk.CTkLabel(register_win, text="טלפון:").pack(pady=5)
        entry_phone = ctk.CTkEntry(register_win)
        entry_phone.pack(pady=5)

        ctk.CTkLabel(register_win, text="אימייל:").pack(pady=5)
        entry_email = ctk.CTkEntry(register_win)
        entry_email.pack(pady=5)

        def submit():
            if not entry_name.get() or not entry_phone.get() or not entry_email.get():
                messagebox.showerror("שגיאה", "מלא את כל השדות")
                return
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO customers (customer_name, phone_number, email) VALUES (%s, %s, %s)",
                               (entry_name.get(), entry_phone.get(), entry_email.get()))
                conn.commit()
                messagebox.showinfo("הצלחה", "חשבון נוצר")
                register_win.destroy()
            except Exception as e:
                messagebox.showerror("שגיאה", str(e))
            finally:
                conn.close()

        ctk.CTkButton(register_win, text="צור חשבון", command=submit).pack(pady=20)

