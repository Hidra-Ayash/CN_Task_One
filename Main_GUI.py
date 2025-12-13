import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion
import queue  # استيراد مكتبة الطابور للتعامل الآمن مع الخيوط

class NetworkApp:
    def __init__(self, root, back_callback): 
        self.root = root
        self.back_to_welcome = back_callback
        self.last_scan_results = {}
        
        # 1. إنشاء طابور الرسائل GUI Queue
        self.gui_queue = queue.Queue()

        # Login Data
        self.SSH_USER = "admin"
        self.SSH_PASS = "cisco123"
        self.SSH_SECRET = "cisco"
        
        # ************************************************
        # الإصلاح: تعريف self.running أولاً
        self.running = True
        # ************************************************

        self.setup_gui()
        
        # 2. بدء مراقبة الطابور بعد تعريف self.running
        self.process_queue() 
        
        # عند إغلاق النافذة، نضمن عدم استدعاء after مجدداً
        self.root.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """ يتم استدعاؤها عند تدمير نافذة NetworkApp """
        if event.widget == self.root:
             self.running = False


    # ---------------------------------------------------------
    # QUEUE PROCESSING (الحل الجذري للمشكلة)
    # ---------------------------------------------------------
    def process_queue(self):
        """
        تتحقق هذه الدالة من الطابور كل 100 ميلي ثانية وتنفذ المهام
        الموجودة فيه داخل الخيط الرئيسي حصراً.
        """
        if not self.running:
            return

        try:
            while True:
                # جلب المهمة من الطابور دون انتظار
                task = self.gui_queue.get_nowait()
                # تنفيذ المهمة (وهي عبارة عن دالة lambda)
                task()
        except queue.Empty:
            pass
        
        # إعادة جدولة الفحص فقط إذا كانت self.running لا تزال True
        self.root.after(100, self.process_queue)

    def run_on_main_thread(self, func):
        """ دالة مساعدة لوضع المهام في الطابور """
        self.gui_queue.put(func)

    # ---------------------------------------------------------
    # GUI SETUP (تم إضافة زر الرجوع هنا)
    # ---------------------------------------------------------
    def setup_gui(self):
        self.root.title("Network Management - GNS3 Edition")
        self.root.resizable(True, True)
        self.root.configure(bg="#e9f2fa") # يفضل إعادته لضمان الخلفية

        # ===== HEADER & BACK BUTTON =====
        header_frame = tk.Frame(self.root, bg="#004d80")
        header_frame.pack(fill="x")
        
      


        tk.Label(
            header_frame,
            text="Network Management System",
            font=("Arial", 22, "bold"),
            bg="#004d80",
            fg="white"
        ).pack(side="left", padx=(50, 0), pady=15) 

        # ===== MAIN CONTAINER =====
        container = tk.Frame(self.root, bg="#e9f2fa")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # -----------------------------------------------------
        # SECTION 1 — SCAN NETWORK
        # -----------------------------------------------------
        scan_frame = tk.LabelFrame(
            container, text=" Scan Network ",
            font=('Arial', 12, 'bold'),
            bg="#f7fbff",
            fg="#003459",
            padx=10, pady=10
        )
        scan_frame.pack(fill="x", pady=10)

        tk.Label(
            scan_frame, text="Target Networks (CIDR List):",
            font=('Arial', 10, 'bold'), bg="#f7fbff"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.network_entry = tk.Entry(scan_frame, width=45, font=('Arial', 11))
        self.network_entry.grid(row=0, column=1, padx=5)
        self.network_entry.insert(
            0, "192.168.32.0/24,192.168.20.0/24, 192.168.31.0/24 "
        )

        self.scan_button = tk.Button(
            scan_frame, text="🔍 Start Scan",
            font=('Arial', 11, 'bold'), bg="#2e8b57", fg="white",
            width=15, command=self.start_scan_thread
        )
        self.scan_button.grid(row=0, column=2, padx=10)

        # -----------------------------------------------------
        # SECTION 2 — OUTPUT LOGS
        # -----------------------------------------------------
        output_frame = tk.LabelFrame(
            container, text=" Scan Results / Logs ",
            font=('Arial', 12, 'bold'), bg="#f7fbff",
            fg="#003459", padx=10, pady=10
        )
        output_frame.pack(fill="both", pady=10)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, width=80, height=15, font=('Consolas', 10)
        )
        self.output_text.pack(fill="both")
        self.output_text.config(state=tk.DISABLED)

        # -----------------------------------------------------
        # SECTION 3 — IP HELPER
        # -----------------------------------------------------
        helper_frame = tk.LabelFrame(
            container, text=" IP Helper Configuration ",
            font=('Arial', 12, 'bold'),
            bg="#f7fbff", fg="#003459",
            padx=10, pady=10
        )
        helper_frame.pack(fill="x", pady=10)

        tk.Label(
            helper_frame, text="Target DHCP Server IP:",
            font=('Arial', 10, 'bold'), bg="#f7fbff"
        ).grid(row=0, column=0, padx=5)

        self.ip_helper_entry = tk.Entry(helper_frame, width=25, font=('Arial', 11))
        self.ip_helper_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            helper_frame, text="Apply IP Helper",
            font=('Arial', 11, 'bold'), bg="#1e88e5", fg="white",
            width=18, command=self.start_ip_helper_thread
        ).grid(row=0, column=2, padx=10)

        # -----------------------------------------------------
        # SECTION 4 — DHCP CONFIG WINDOW
        # -----------------------------------------------------
        dhcp_frame = tk.Frame(container, bg="#e9f2fa")
        dhcp_frame.pack(fill="x", pady=10)

        tk.Button(
            dhcp_frame, text="⚙️ Open DHCP Configuration",
            font=('Arial', 13, 'bold'),
            bg="#ff9800", fg="white",
            width=30, command=self.open_dhcp_window
        ).pack()
  # زر الرجوع (Back Button)
        tk.Button(
            dhcp_frame, 
            text="← Back to Welcome",
            font=('Arial', 11, 'bold'), 
            bg="#cc3333", 
            fg="white",
            command=self.back_to_welcome # دالة العودة التي تم تمريرها
        ).pack(side="right", padx=8, pady=15)
    # ---------------------------------------------------------
    # LOG OUTPUT 
    # ---------------------------------------------------------
    def log(self, message):
        self.run_on_main_thread(lambda: self._log_impl(message))

    def _log_impl(self, message):
        if not self.running: return
        try:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        except Exception:
            pass 

    # ---------------------------------------------------------
    # SCAN NETWORK 
    # ---------------------------------------------------------
    def start_scan_thread(self):
        target_networks = [
            n.strip() for n in self.network_entry.get().split(',')
            if n.strip()
        ]

        if not target_networks:
            return
        
        self.scan_button.config(state=tk.DISABLED, text="Scanning...")
        self.log(f"Starting Scan on {target_networks}...")
        
        threading.Thread(
            target=self.run_scan, args=(target_networks,), daemon=True
        ).start()

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
            for category, devices in results.items():
                if devices:
                    if category not in ["Others"]: 
                        self.log(f"[{category}]: {len(devices)} found.")
                        for dev in devices:
                            self.log(f" - IP: {dev['ip']} | {dev['descr']}")
                    elif category == "Others":
                        self.log(f"[Others]: {len(devices)} found (Details Hidden).")
            self.log("-" * 60)

        except Exception as e:
            self.log(f"Scan Error: {e}")
        
        finally:
            self.run_on_main_thread(
                lambda: self.scan_button.config(state=tk.NORMAL, text="🔍 Start Scan")
            )

    # ---------------------------------------------------------
    # IP HELPER
    # ---------------------------------------------------------
    def start_ip_helper_thread(self):
        target_ip = self.ip_helper_entry.get().strip()

        if not target_ip or not self.last_scan_results:
            self.run_on_main_thread(
                lambda: messagebox.showwarning("Error", "Run Scan first & Enter IP.")
            )
            return

        self.log(f"\nApplying IP Helper {target_ip}...")
        threading.Thread(
            target=self.run_ip_helper, args=(target_ip,), daemon=True
        ).start()

    def run_ip_helper(self, target_ip):
        try:
            valid_targets = []
            for dev in self.last_scan_results.get("Routers", []) + self.last_scan_results.get("Switches", []):
               valid_targets.append(dev['ip'])
    
            if target_ip not in valid_targets:
                self.run_on_main_thread(lambda: self._show_helper_warning(target_ip))
                return

            logs = backendFinalVersion.run_ip_helper_logic(
                target_ip,
                self.last_scan_results,
                self.SSH_USER, self.SSH_PASS, self.SSH_SECRET
            )
            for msg in logs:
                self.log(msg)
    
        except Exception as e:
            self.log(f"Config Error: {e}")

    def _show_helper_warning(self, target_ip):
        if not self.running: return
        
        warn_win = tk.Toplevel(self.root)
        warn_win.title("⚠️ IP Helper Warning")
        warn_win.geometry("400x200")
        warn_win.configure(bg="#fff3cd")

        tk.Label(
            warn_win,
            text=f"❌This IP {target_ip} NOT A ROUTER, use The IP OF Router",
            font=("Arial", 12, "bold"),
            bg="#fff3cd", fg="#721c24",
            wraplength=350, justify="center"
        ).pack(expand=True, pady=40)

        tk.Button(
            warn_win, text="Close",
            font=("Arial", 11, "bold"),
            bg="#f5c6cb", fg="black",
            command=warn_win.destroy
        ).pack(pady=10)


    # ---------------------------------------------------------
    # DHCP WINDOW 
    # ---------------------------------------------------------
    def open_dhcp_window(self):
        if not self.last_scan_results.get("Routers"):
            self.run_on_main_thread(
                lambda: messagebox.showwarning(
                    "No Routers", "No Routers found in scan results! Cannot configure DHCP."
                )
            )
            return
        
        self.run_on_main_thread(self._open_dhcp_window_impl)

    def _open_dhcp_window_impl(self):
        if not self.running: return
        dhcp_win = tk.Toplevel(self.root)
        dhcp_win.title("DHCP Configuration & Management")
        dhcp_win.geometry("600x650")
        dhcp_win.configure(bg="#eef5ff")

        # =================== BASIC POOL ===================
        pool_frame = tk.LabelFrame(
            dhcp_win, text=" Step 1: Basic DHCP Pool ",
            padx=10, pady=10, bg="#f7fbff",
            font=('Arial', 10, 'bold')
        )
        pool_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(pool_frame, text="Pool Name:", bg="#f7fbff").grid(row=0, column=0)
        e_name = tk.Entry(pool_frame); e_name.grid(row=0, column=1)
        e_name.insert(0, "LAN_POOL")

        tk.Label(pool_frame, text="Network:", bg="#f7fbff").grid(row=0, column=2)
        e_net = tk.Entry(pool_frame); e_net.grid(row=0, column=3)
        e_net.insert(0, "192.168.20.0")

        tk.Label(pool_frame, text="Gateway:", bg="#f7fbff").grid(row=1, column=0)
        e_gw = tk.Entry(pool_frame); e_gw.grid(row=1, column=1)
        e_gw.insert(0, "192.168.20.1")

        tk.Label(pool_frame, text="DNS:", bg="#f7fbff").grid(row=1, column=2)
        e_dns = tk.Entry(pool_frame); e_dns.grid(row=1, column=3)
        e_dns.insert(0, "8.8.8.8")

        tk.Button(
            pool_frame, text="Apply Pool Config",
            bg="orange", fg="black",
            command=lambda: self._thread_wrapper_pool({
                'pool_name': e_name.get(),
                'network': e_net.get(),
                'netmask': "255.255.255.0",
                'default_router': e_gw.get(),
                'dns_server': e_dns.get()
            })
        ).grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

        # =================== EXCLUSIONS ===================
        excl_frame = tk.LabelFrame(
            dhcp_win, text=" Step 2: Exclude IP Ranges ",
            padx=10, pady=10, bg="#f7fbff"
        )
        excl_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(excl_frame, text="Start IP:", bg="#f7fbff").grid(row=0, column=0)
        e_ex_start = tk.Entry(excl_frame, width=15)
        e_ex_start.grid(row=0, column=1)

        tk.Label(excl_frame, text="End IP:", bg="#f7fbff").grid(row=0, column=2)
        e_ex_end = tk.Entry(excl_frame, width=15)
        e_ex_end.grid(row=0, column=3)

        lb_excl = tk.Listbox(excl_frame, height=4, width=50)
        lb_excl.grid(row=2, column=0, columnspan=4, pady=5)

        tk.Button(
            excl_frame, text="Add Exclusion",
            command=lambda: self.add_exclusion(e_ex_start, e_ex_end, lb_excl)
        ).grid(row=1, column=0, columnspan=4, pady=5, sticky='ew')

        # =================== RESERVATIONS ===================
        res_frame = tk.LabelFrame(
            dhcp_win, text=" Step 3: Static Reservations ",
            padx=10, pady=10, bg="#f7fbff"
        )
        res_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(res_frame, text="IP Address:", bg="#f7fbff").grid(row=0, column=0)
        e_res_ip = tk.Entry(res_frame, width=20)
        e_res_ip.grid(row=0, column=1)

        tk.Label(res_frame, text="MAC Address:", bg="#f7fbff").grid(row=1, column=0)
        e_res_mac = tk.Entry(res_frame, width=20)
        e_res_mac.grid(row=1, column=1)

        lb_res = tk.Listbox(res_frame, height=4, width=50)
        lb_res.grid(row=3, column=0, columnspan=3, pady=5)

        tk.Button(
            res_frame, text="Add Reservation",
            command=lambda: self.add_reservation(e_res_ip, e_res_mac, lb_res)
        ).grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

    # ---------------------------------------------------------
    # DHCP HELPERS 
    # ---------------------------------------------------------
    def add_exclusion(self, e_start, e_end, listbox):
        start = e_start.get().strip()
        end = e_end.get().strip()
        if not start:
            return
        self.run_on_main_thread(lambda: listbox.insert(tk.END, f"{start} - {end}"))

        threading.Thread(
            target=self._thread_wrapper_exclude,
            args=(start, end), daemon=True
        ).start()

    def add_reservation(self, e_ip, e_mac, listbox):
        ip = e_ip.get().strip()
        mac = e_mac.get().strip()

        if not ip or not mac:
            return

        self.run_on_main_thread(lambda: listbox.insert(tk.END, f"IP: {ip} | MAC: {mac}"))

        threading.Thread(
            target=self._thread_wrapper_reserve,
            args=(ip, mac), daemon=True
        ).start()

    # ---------------------------------------------------------
    # THREAD WRAPPERS 
    # ---------------------------------------------------------
    def _thread_wrapper_pool(self, params):
        try:
            logs = backendFinalVersion.run_dhcp_pool_logic(
                params, self.last_scan_results,
                self.SSH_USER, self.SSH_PASS, self.SSH_SECRET
            )
            for msg in logs:
                self.log(msg)
        except Exception as e:
            self.log(f"Pool Error: {e}")

    def _thread_wrapper_exclude(self, start, end):
        try:
            logs = backendFinalVersion.run_exclude_logic(
                start, end, self.last_scan_results,
                self.SSH_USER, self.SSH_PASS, self.SSH_SECRET
            )
            for msg in logs:
                self.log(msg)
        except Exception as e:
            self.log(f"Exclude Error: {e}")

    def _thread_wrapper_reserve(self, ip, mac):
        try:
            logs = backendFinalVersion.run_reservation_logic(
                ip, mac, self.last_scan_results,
                self.SSH_USER, self.SSH_PASS, self.SSH_SECRET
            )
            for msg in logs:
                self.log(msg)
        except Exception as e:
            self.log(f"Reservation Error: {e}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    def dummy_callback():
        print("Back button pressed in standalone mode.")

    app = NetworkApp(root, back_callback=dummy_callback)
    root.mainloop()