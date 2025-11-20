import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion  # التأكد من وجود ملف backendFinalVersion.py في نفس المجلد

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.setup_gui()
        self.last_scan_results = {} 

    def setup_gui(self):
        self.root.minsize(700, 600)
        self.root.geometry("800x700")
        self.root.title("First GUI - Network Management")
        self.root.configure(bg="lightblue")

        label = tk.Label(self.root, text="Welcome To The Computer Networks Management!", font=('Arial', 18), bg="lightblue")
        label.pack(pady=10)

        btn_scan = tk.Button(self.root, text="قائمة الاجهزة المكتشفة (Scan)", font=('Arial', 12), command=self.start_scan_thread)
        btn_scan.place(x=20, y=60)

        output_label = tk.Label(self.root, text="النتائج:", font=('Arial', 12), bg="lightblue")
        output_label.place(x=300, y=70)

        self.output_text = scrolledtext.ScrolledText(self.root, width=80, height=20, font=('Courier', 9))
        self.output_text.place(x=20, y=100)

        lbl_ip = tk.Label(self.root, text="IP Relay Agent:", font=('Arial', 10), bg="lightblue")
        lbl_ip.place(x=20, y=410)
        
        self.ipentry = tk.Entry(self.root, width=20, font=('Arial', 12))
        self.ipentry.place(x=20, y=430)

        lbl_extra = tk.Label(self.root, text="حقل إضافي (اختياري):", font=('Arial', 10), bg="lightblue")
        lbl_extra.place(x=20, y=455)
        
        self.ipentry1 = tk.Entry(self.root, width=20, font=('Arial', 12))
        self.ipentry1.place(x=20, y=475)

        btn_helper = tk.Button(self.root, text="تطبيق IP Helper", font=('Arial', 12), command=self.start_ip_helper_thread)
        btn_helper.place(x=20, y=510)

        btn_dhcp = tk.Button(self.root, text="زر تعيين خدمات DHCP", font=('Arial', 12), command=self.dhcp_function_placeholder)
        btn_dhcp.place(x=20, y=550)

    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def start_scan_thread(self):
        self.output_text.delete(1.0, tk.END)
        self.log("Starting Network Scan... Please wait.")
        t = threading.Thread(target=self.run_scan)
        t.start()

    def run_scan(self):
        try:
            # إعدادات الاتصال الافتراضية (يجب تغييرها لتناسب شبكتك الحقيقية)
            scanner = backendFinalVersion.Scan(ssh_user="admin", ssh_pass="cisco123", ssh_secret="cisco")
            
            # تأكد من النطاق الصحيح لشبكتك (مثلاً 192.168.1.0/24)
            results = scanner.scan("192.168.1.0/24", auto_fix_ssh=True)
            
            self.last_scan_results = results 
            
            self.log("-" * 50)
            self.log(f"Scan Complete. Found Devices:")
            
            found_any = False
            for category, devices in results.items():
                if devices:
                    found_any = True
                    self.log(f"\n[{category}]:")
                    for dev in devices:
                        self.log(f" - IP: {dev['ip']}, MAC: {dev['mac']}, Name: {dev['name']}")
            
            if not found_any:
                self.log("No devices found. (Check IP range or Permissions)")
            
            self.log("-" * 50)
            
        except Exception as e:
            self.log(f"Error during scan: {e}")

    def start_ip_helper_thread(self):
        target_ip = self.ipentry.get()
        if not target_ip:
            messagebox.showwarning("Input Error", "Please enter IP Relay Agent first.")
            return
        
        if not self.last_scan_results:
            messagebox.showwarning("Order Error", "Please Run Scan First to find devices.")
            return

        self.log(f"\nStarting IP Helper Configuration on found devices for Agent: {target_ip}...")
        t = threading.Thread(target=self.run_ip_helper, args=(target_ip,))
        t.start()

    def run_ip_helper(self, target_ip):
        try:
            logs = backendFinalVersion.run_ip_helper_logic(target_ip, self.last_scan_results)
            for msg in logs:
                self.log(msg)
            self.log("IP Helper Configuration Finished.")
        except Exception as e:
            self.log(f"Error: {e}")

    def dhcp_function_placeholder(self):
        messagebox.showinfo("Info", "DHCP function not connected yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()