import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion 

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.last_scan_results = {}
        # بيانات الدخول - عدلها حسب إعدادات شبكتك في GNS3
        self.SSH_USER = "admin"
        self.SSH_PASS = "cisco123"
        self.SSH_SECRET = "cisco" 
        self.setup_gui()

    def setup_gui(self):
        self.root.minsize(700, 650)
        self.root.geometry("850x750")
        self.root.title("Network Management - GNS3 Edition")
        self.root.configure(bg="#e6f2ff") 

        # العنوان
        label = tk.Label(self.root, text="Network Management System", font=('Arial', 18, 'bold'), bg="#e6f2ff", fg="#003366")
        label.pack(pady=15)

        # --- قسم المسح ---
        frame_scan = tk.Frame(self.root, bg="#e6f2ff")
        frame_scan.place(x=20, y=70)

        tk.Label(frame_scan, text="Target Networks (CIDR List):", font=('Arial', 10, 'bold'), bg="#e6f2ff").grid(row=0, column=0, padx=5)
        
        self.network_entry = tk.Entry(frame_scan, width=40, font=('Arial', 11)) 
        self.network_entry.grid(row=0, column=1, padx=5)
        
        # القيمة الافتراضية (يمكن للمستخدم تعديلها الآن)
        self.network_entry.insert(0, "192.168.20.0/24, 192.168.31.0/24, 192.168.32.0/24") 
        
        # **تعديل 1: جعل الحقل قابلاً للكتابة (تم حذف state='readonly')**
        
        btn_scan = tk.Button(frame_scan, text="🔍 Start Scan", font=('Arial', 11, 'bold'), bg="#4CAF50", fg="white", command=self.start_scan_thread)
        btn_scan.grid(row=0, column=2, padx=10)

        # --- قسم النتائج ---
        tk.Label(self.root, text="Scan Results / Logs (Read-Only):", font=('Arial', 11, 'bold'), bg="#e6f2ff").place(x=20, y=120)
        
        self.output_text = scrolledtext.ScrolledText(self.root, width=95, height=22, font=('Consolas', 9))
        self.output_text.place(x=20, y=145)
        
        # جعل مربع النتائج للقراءة فقط (لا يؤثر على الإدخال أعلاه)
        self.output_text.config(state=tk.DISABLED)

        # --- قسم التحكم (IP Helper) ---
        lbl_ip = tk.Label(self.root, text="IP Helper Address (Router IP):", font=('Arial', 10, 'bold'), bg="#e6f2ff")
        lbl_ip.place(x=20, y=500)
        
        self.ip_helper_entry = tk.Entry(self.root, width=25, font=('Arial', 11))
        self.ip_helper_entry.place(x=20, y=525)

        btn_helper = tk.Button(self.root, text="Apply IP Helper", font=('Arial', 11), bg="#2196F3", fg="white", command=self.start_ip_helper_thread)
        btn_helper.place(x=250, y=520)

        # --- قسم DHCP ---
        btn_dhcp = tk.Button(self.root, text="⚙️ Configure DHCP Pool", font=('Arial', 12, 'bold'), bg="#FF9800", fg="white", command=self.open_dhcp_window)
        btn_dhcp.place(x=20, y=600)

    def log(self, message):
        """دالة للكتابة داخل مربع النص المقفل"""
        self.output_text.config(state=tk.NORMAL) # فتح القفل
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED) # إعادة القفل

    def start_scan_thread(self):
        # قراءة النطاقات من الحقل (أصبح قابلاً للتعديل الآن)
        target_networks = [n.strip() for n in self.network_entry.get().split(',') if n.strip()]

        if not target_networks:
            messagebox.showwarning("Input Error", "Please enter at least one target network.")
            return

        # تنظيف الشاشة
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

        self.log(f"Starting Scan on {', '.join(target_networks)}...")
        self.log("Identifying devices (SSH/ARP)... Please wait.")
        
        t = threading.Thread(target=self.run_scan, args=(target_networks,))
        t.start()

    def run_scan(self, target_networks): 
        try:
            scanner = backendFinalVersion.Scan(
                ssh_user=self.SSH_USER, 
                ssh_pass=self.SSH_PASS, 
                ssh_secret=self.SSH_SECRET
            )
            
            results = scanner.scan_multiple(target_networks)
            self.last_scan_results = results 
            
            self.log("-" * 60)
            
            total_devices = sum(len(devices) for devices in results.values())
            if total_devices == 0:
                self.log("No devices found! Check Loopback adapter and connections.")
            else:
                for category, devices in results.items():
                    if devices:
                        self.log(f"[{category}]:")
                        for dev in devices:
                            self.log(f" - IP: {dev['ip']} | Type: {dev['descr']}")
                            
            self.log("-" * 60)
            
        except Exception as e:
            self.log(f"Error during scan: {e}")

    # **تعديل 2: دالة التحقق من صحة IP Helper**
    def start_ip_helper_thread(self):
        target_ip = self.ip_helper_entry.get().strip()
        
        # 1. التحقق من أن الحقل ليس فارغاً
        if not target_ip:
            messagebox.showwarning("Input Error", "Please enter IP Helper Address.")
            return
        
        # 2. التحقق من إجراء المسح أولاً
        if not self.last_scan_results:
             messagebox.showwarning("Sequence Error", "Please run a Network Scan first.")
             return

        # 3. منطق التحقق (Validation Logic)
        # جلب قائمة الرواتر المكتشفة فقط
        discovered_routers = self.last_scan_results.get("Routers", [])
        # إنشاء قائمة بعناوين IP الخاصة بالرواتر
        valid_router_ips = [dev['ip'] for dev in discovered_routers]

        # فحص: هل الـ IP المدخل هو راوتر مكتشف؟
        if target_ip not in valid_router_ips:
            # فحص إضافي: هل هو موجود كجهاز آخر (مثل سويتش)؟ لإعطاء رسالة خطأ دقيقة
            found_anywhere = False
            found_type = "Unknown"
            for category, devices in self.last_scan_results.items():
                for dev in devices:
                    if dev['ip'] == target_ip:
                        found_anywhere = True
                        found_type = category[:-1] # حذف حرف s من الجمع
                        break
            
            if found_anywhere:
                messagebox.showerror("Invalid Device Type", f"The IP {target_ip} was found but it is a '{found_type}', NOT a Router.\nIP Helper must be a Router address.")
            else:
                messagebox.showerror("IP Not Found", f"The IP {target_ip} was not found in the scan results.\nPlease scan the network or check the IP.")
            
            return # إيقاف العملية هنا

        # إذا تجاوز الشروط، نبدأ العملية
        self.log(f"\nApplying IP Helper {target_ip} (Validated as Router)...")
        t = threading.Thread(target=self.run_ip_helper, args=(target_ip,))
        t.start()

    def run_ip_helper(self, target_ip):
        try:
            logs = backendFinalVersion.run_ip_helper_logic(
                target_ip, 
                self.last_scan_results, 
                self.SSH_USER, 
                self.SSH_PASS, 
                self.SSH_SECRET 
            )
            for msg in logs:
                self.log(msg)
            self.log("IP Helper Task Finished.")
        except Exception as e:
            self.log(f"Configuration Error: {e}")

    def open_dhcp_window(self):
        if not self.last_scan_results.get("Routers"):
            messagebox.showwarning("No Routers", "No Routers found in scan results to configure DHCP.")
            return

        dhcp_win = tk.Toplevel(self.root)
        dhcp_win.title("DHCP Pool Config")
        dhcp_win.geometry("400x350")
        
        tk.Label(dhcp_win, text="Pool Name:").pack(pady=5)
        e_name = tk.Entry(dhcp_win); e_name.pack()
        e_name.insert(0, "LAN_POOL")

        tk.Label(dhcp_win, text="Network (e.g., 192.168.20.0):").pack(pady=5)
        e_net = tk.Entry(dhcp_win); e_net.pack()
        e_net.insert(0, "192.168.20.0")

        tk.Label(dhcp_win, text="Subnet Mask:").pack(pady=5)
        e_mask = tk.Entry(dhcp_win); e_mask.pack()
        e_mask.insert(0, "255.255.255.0") 

        tk.Label(dhcp_win, text="Default Gateway (Router IP):").pack(pady=5)
        e_gw = tk.Entry(dhcp_win); e_gw.pack()
        e_gw.insert(0, "192.168.20.1")

        tk.Label(dhcp_win, text="DNS Server:").pack(pady=5)
        e_dns = tk.Entry(dhcp_win); e_dns.pack()
        e_dns.insert(0, "8.8.8.8")

        def apply_dhcp():
            params = {
                'pool_name': e_name.get(),
                'network': e_net.get(),
                'netmask': e_mask.get(), 
                'default_router': e_gw.get(),
                'dns_server': e_dns.get()
            }
            if not params['pool_name'] or not params['network'] or not params['netmask'] or not params['default_router']:
                messagebox.showerror("Error", "All fields are required!")
                return
            
            dhcp_win.destroy()
            self.log(f"\nConfiguring DHCP Pool '{params['pool_name']}'...")
            threading.Thread(target=self.run_dhcp, args=(params,)).start()

        tk.Button(dhcp_win, text="Apply Configuration", bg="orange", command=apply_dhcp).pack(pady=20)

    def run_dhcp(self, params):
        try:
            logs = backendFinalVersion.run_dhcp_pool_logic(
                params,
                self.last_scan_results,
                self.SSH_USER,
                self.SSH_PASS,
                self.SSH_SECRET 
            )
            for msg in logs:
                self.log(msg)
        except Exception as e:
            self.log(f"DHCP Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()