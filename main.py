import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from login import create_login_window
if __name__ == "__main__":
    create_login_window()
    try:
        print("Starting main.py...")
        # שאר הקוד שלך
    except Exception as e:
        import traceback

        print("Exception occurred:")
        traceback.print_exc()
#ahmed