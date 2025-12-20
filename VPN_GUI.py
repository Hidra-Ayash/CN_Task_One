import tkinter as tk
from tkinter import messagebox
import threading
import backendFinalVersion  # الربط مع منطق العمل

class VPNInterface:
    def __init__(self, parent_root):
        self.parent_root = parent_root
        
        # إخفاء النافذة الرئيسية (First_GUI)
        self.parent_root.withdraw()

        # إنشاء نافذة الـ VPN
        self.window = tk.Toplevel()
        self.window.title("VPN Site-to-Site Configuration")
        self.window.geometry("900x650")
        self.window.configure(bg="#f0f2f5") # لون خلفية هادئ
        
        # عند إغلاق النافذة من علامة X نعود للرئيسية
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        self.setup_ui()

    def setup_ui(self):
        # العنوان الرئيسي
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=100)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame, text="IPsec VPN Deployment Tool",
            font=("Segoe UI", 22, "bold"), fg="white", bg="#2c3e50"
        ).pack(pady=25)

        # حاوية النماذج (Form)
        main_container = tk.Frame(self.window, bg="white", padx=40, pady=30, relief="flat")
        main_container.pack(pady=30, padx=50, fill="both")

        fields = [
            ("HQ Router IP (WAN):", "e.g. 192.168.32.10"),
            ("Branch Router IP (WAN):", "e.g. 192.168.32.20"),
            ("HQ LAN Network:", "e.g. 192.168.20.0"),
            ("Branch LAN Network:", "e.g. 192.168.30.0"),
            ("Shared Secret Key:", "Enter Strong Key")
        ]
        
        self.entries = []
        for i, (label_text, placeholder) in enumerate(fields):
            tk.Label(
                main_container, text=label_text, font=("Segoe UI", 11, "bold"),
                bg="white", fg="#34495e"
            ).grid(row=i, column=0, pady=15, sticky="w")
            
            entry = tk.Entry(
                main_container, font=("Segoe UI", 12), width=35, 
                relief="solid", bd=1, highlightthickness=1, highlightcolor="#3498db"
            )
            if "Key" in label_text: entry.config(show="*")
            entry.grid(row=i, column=1, pady=15, padx=20, sticky="w")
            # إضافة نص توضيحي خفيف (اختياري)
            entry.insert(0, "") 
            self.entries.append(entry)

        # أزرار التحكم
        btn_frame = tk.Frame(self.window, bg="#f0f2f5")
        btn_frame.pack(pady=20)

        # زر التنفيذ
        self.deploy_btn = tk.Button(
            btn_frame, text="🚀 Deploy VPN", font=("Segoe UI", 12, "bold"),
            bg="#27ae60", fg="white", width=18, height=2, relief="flat",
            cursor="hand2", command=self.run_deployment
        )
        self.deploy_btn.pack(side="left", padx=15)

        # زر الرجوع
        back_btn = tk.Button(
            btn_frame, text="⬅ Back to Home", font=("Segoe UI", 12),
            bg="#95a5a6", fg="white", width=15, height=2, relief="flat",
            cursor="hand2", command=self.go_back
        )
        back_btn.pack(side="left", padx=15)

    def run_deployment(self):
        vals = [e.get().strip() for e in self.entries]
        if any(v == "" for v in vals):
            messagebox.showwarning("Incomplete Data", "Please fill all fields before deploying.")
            return

        self.deploy_btn.config(state="disabled", text="Connecting...", bg="#7f8c8d")
        
        def task():
            try:
                # استدعاء الجسر في الباك إند (تأكد من وجود الدالة في backendFinalVersion)
                logs = backendFinalVersion.run_vpn_logic_bridge(
                    vals[0], vals[1], vals[2], vals[3], vals[4],
                    "admin", "cisco123", "cisco"
                )
                messagebox.showinfo("Configuration Result", "\n".join(logs))
            except Exception as e:
                messagebox.showerror("Critical Error", f"Failed to connect: {str(e)}")
            finally:
                self.deploy_btn.config(state="normal", text="🚀 Deploy VPN", bg="#27ae60")

        threading.Thread(target=task, daemon=True).start()

    def go_back(self):
        self.window.destroy()
        self.parent_root.deiconify() # إعادة إظهار الصفحة الرئيسية

def open_vpn_window(root):
    return VPNInterface(root)