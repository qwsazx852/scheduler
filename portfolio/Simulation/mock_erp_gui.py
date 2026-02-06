import tkinter as tk
from tkinter import messagebox
import time

class MockERP:
    def __init__(self, root):
        self.root = root
        self.root.title("T100 ERP - Sales Order Entry (Simulation)")
        self.root.geometry("600x450")
        
        # simulated lag
        self.root.configure(bg="#f0f0f0")

        # Title
        tk.Label(root, text="T100 銷售訂單維護作業 (axmt500)", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        # Form Frame
        form_frame = tk.Frame(root, bg="#f0f0f0")
        form_frame.pack(pady=20)

        self.entries = {}
        
        fields = [
            ("客戶編號 (Customer ID):", "CUST_001"),
            ("訂單單號 (Order No):", "AUTO_GEN"),
            ("產品料號 (Part No):", ""),
            ("訂購數量 (Quantity):", ""),
            ("預交日期 (Delivery Date):", "")
        ]

        for i, (label_text, default) in enumerate(fields):
            tk.Label(form_frame, text=label_text, font=("Arial", 12), bg="#f0f0f0").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            if default:
                entry.insert(0, default)
            
            # Store reference by label simple name
            key = label_text.split("(")[0].strip() # e.g. "客戶編號"
            self.entries[key] = entry

        # Buttons
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="查詢 (Query)", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="新增 (Add)", width=10).pack(side="left", padx=5)
        self.save_btn = tk.Button(btn_frame, text="存檔 (Save)", width=10, command=self.save_order, bg="#4CAF50", fg="white")
        self.save_btn.pack(side="left", padx=5)
        tk.Button(btn_frame, text="離開 (Exit)", width=10, command=root.quit).pack(side="left", padx=5)

        # Status Bar
        self.status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def save_order(self):
        # Simulate processing time
        self.status.config(text="Processing...")
        self.root.update()
        time.sleep(0.5)
        
        part_no = self.entries["產品料號"].get()
        qty = self.entries["訂購數量"].get()
        
        if not part_no or not qty:
            messagebox.showerror("Error", "欄位不可為空 (Fields Required)!")
            self.status.config(text="Error")
            return

        messagebox.showinfo("Success", f"訂單建立成功 (Order Created)\n料號: {part_no}\n數量: {qty}")
        self.status.config(text="Saved Successfully")
        
        # Clear fields for next demo
        self.entries["產品料號"].delete(0, tk.END)
        self.entries["訂購數量"].delete(0, tk.END)
        self.entries["預交日期"].delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MockERP(root)
    root.mainloop()
