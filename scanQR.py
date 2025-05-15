from tkinter import ttk, messagebox, filedialog
import cv2
from pyzbar.pyzbar import decode

def scan_qr_code():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            sku_code = obj.data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            return sku_code  # מחזיר את הקוד שנסרק

        cv2.imshow("Scan QR Code - Press Q to cancel", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("סריקה בוטלה", "לא נסרק קוד.")
    return None
