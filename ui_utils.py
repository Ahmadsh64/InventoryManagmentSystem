import tkinter as tk

def create_window_button(parent, text, command, icon=None):
    btn = tk.Button(
        parent,
        text=f"{icon}  {text}" if icon else text,
        font=("Segoe UI", 10, "bold"),
        bg="#353b48",
        fg="white",
        activebackground="#40739e",
        activeforeground="white",
        bd=0,
        padx=16,
        pady=8,
        anchor="center",
        command=command,
        relief="flat",
        cursor="hand2"
    )
    btn.pack(side="right", padx=6, pady=6)
    return btn
