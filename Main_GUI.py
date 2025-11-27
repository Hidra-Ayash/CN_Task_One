import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion 

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.last_scan_results = {}
        # بيانات الدخول
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
        self.network_entry.insert(0, "192.168.20.0/24, 192.168.31.0/24 , 192.168.32.0/24") 
        
        btn_scan = tk.Button(frame_scan, text="🔍 Start Scan", font=('Arial', 11, 'bold'), bg="#4CAF50", fg="white", command=self.start_scan_thread)
        btn_scan.grid(row=0, column=2, padx=10)

        # --- قسم النتائج ---
        tk.Label(self.root, text="Scan Results / Logs:", font=('Arial', 11, 'bold'), bg="#e6f2ff").place(x=20, y=120)
        
        self.output_text = scrolledtext.ScrolledText(self.root, width=95, height=22, font=('Consolas', 9))
        self.output_text.place(x=20, y=145)
        self.output_text.config(state=tk.DISABLED)

        # --- قسم IP Helper ---
        lbl_ip = tk.Label(self.root, text="IP Helper (Target Server IP):", font=('Arial', 10, 'bold'), bg="#e6f2ff")
        lbl_ip.place(x=20, y=500)
        
        self.ip_helper_entry = tk.Entry(self.root, width=25, font=('Arial', 11))
        self.ip_helper_entry.place(x=20, y=525)

        btn_helper = tk.Button(self.root, text="Apply IP Helper", font=('Arial', 11), bg="#2196F3", fg="white", command=self.start_ip_helper_thread)
        btn_helper.place(x=250, y=520)

        # --- قسم DHCP ---
        btn_dhcp = tk.Button(self.root, text="⚙️ Configure DHCP Service", font=('Arial', 12, 'bold'), bg="#FF9800", fg="white", command=self.open_dhcp_window)
        btn_dhcp.place(x=20, y=600)

    def log(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    # --- Scanning & IP Helper Wrappers ---
    def start_scan_thread(self):
        target_networks = [n.strip() for n in self.network_entry.get().split(',') if n.strip()]
        if not target_networks: return
        
        self.log(f"Starting Scan on {target_networks}...")
        threading.Thread(target=self.run_scan, args=(target_networks,)).start()

    def run_scan(self, target_networks): 
        try:
            scanner = backendFinalVersion.Scan(ssh_user=self.SSH_USER, ssh_pass=self.SSH_PASS, ssh_secret=self.SSH_SECRET)
            results = scanner.scan_multiple(target_networks)
            self.last_scan_results = results 
            
            self.log("-" * 60)
            for category, devices in results.items():
                if devices:
                    self.log(f"[{category}]: {len(devices)} found.")
                    for dev in devices: self.log(f" - IP: {dev['ip']} | {dev['descr']}")
            self.log("-" * 60)
        except Exception as e: self.log(f"Scan Error: {e}")

    def start_ip_helper_thread(self):
        target_ip = self.ip_helper_entry.get().strip()
        if not target_ip or not self.last_scan_results:
             messagebox.showwarning("Error", "Run Scan first & Enter IP.")
             return
        
        self.log(f"\nApplying IP Helper {target_ip}...")
        threading.Thread(target=self.run_ip_helper, args=(target_ip,)).start()

    def run_ip_helper(self, target_ip):
        try:
            logs = backendFinalVersion.run_ip_helper_logic(target_ip, self.last_scan_results, self.SSH_USER, self.SSH_PASS, self.SSH_SECRET)
            for msg in logs: self.log(msg)
        except Exception as e: self.log(f"Config Error: {e}")


    # =========================================================
    # === MERGED DHCP WINDOW (New GUI Implementation) ===
    # =========================================================
    def open_dhcp_window(self):
        # التحقق من وجود رواتر في نتائج المسح
        if not self.last_scan_results.get("Routers"):
            messagebox.showwarning("No Routers", "No Routers found in scan results! Cannot configure DHCP.")
            return

        dhcp_win = tk.Toplevel(self.root)
        dhcp_win.title("DHCP Configuration & Management")
        dhcp_win.geometry("600x650")

        # --- Section 0: Basic Pool Config (Global) ---
        pool_frame = tk.LabelFrame(dhcp_win, text="Step 1: Basic Global Pool", padx=10, pady=10, font=('Arial', 10, 'bold'))
        pool_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid layout for basic inputs
        tk.Label(pool_frame, text="Pool Name:").grid(row=0, column=0)
        e_name = tk.Entry(pool_frame); e_name.grid(row=0, column=1)
        e_name.insert(0, "LAN_POOL")
        
        tk.Label(pool_frame, text="Network:").grid(row=0, column=2)
        e_net = tk.Entry(pool_frame); e_net.grid(row=0, column=3)
        e_net.insert(0, "192.168.20.0")

        tk.Label(pool_frame, text="Gateway:").grid(row=1, column=0)
        e_gw = tk.Entry(pool_frame); e_gw.grid(row=1, column=1)
        e_gw.insert(0, "192.168.20.1")

        tk.Label(pool_frame, text="DNS:").grid(row=1, column=2)
        e_dns = tk.Entry(pool_frame); e_dns.grid(row=1, column=3)
        e_dns.insert(0, "8.8.8.8")

        def apply_pool_config():
            params = {
                'pool_name': e_name.get(), 'network': e_net.get(),
                'netmask': "255.255.255.0", 'default_router': e_gw.get(),
                'dns_server': e_dns.get()
            }
            self.log(f"\nConfiguring Main DHCP Pool '{params['pool_name']}'...")
            threading.Thread(target=self._thread_wrapper_pool, args=(params,)).start()
            
        tk.Button(pool_frame, text="Apply Pool Config", bg="orange", command=apply_pool_config).grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

        # --- Section 1: Exclusions (From New Code) ---
        excl_frame = tk.LabelFrame(dhcp_win, text="Step 2: Exclude IPs", padx=10, pady=10)
        excl_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(excl_frame, text="Start IP:").grid(row=0, column=0)
        e_ex_start = tk.Entry(excl_frame, width=15); e_ex_start.grid(row=0, column=1)
        
        tk.Label(excl_frame, text="End IP:").grid(row=0, column=2)
        e_ex_end = tk.Entry(excl_frame, width=15); e_ex_end.grid(row=0, column=3)
        
        # Listbox for Exclusions
        lb_excl = tk.Listbox(excl_frame, height=4, width=50)
        lb_excl.grid(row=2, column=0, columnspan=4, pady=5)

        def add_exclusion():
            start = e_ex_start.get().strip()
            end = e_ex_end.get().strip()
            if not start: return
            
            # Update Listbox visual
            lb_excl.insert(tk.END, f"{start} - {end}")
            # Call Backend
            self.log(f"\nAdding Exclusion: {start} - {end}...")
            threading.Thread(target=self._thread_wrapper_exclude, args=(start, end)).start()

        tk.Button(excl_frame, text="Add Exclusion", command=add_exclusion).grid(row=1, column=0, columnspan=4, pady=5, sticky='ew')

        # --- Section 2: Static Reservations (From New Code) ---
        res_frame = tk.LabelFrame(dhcp_win, text="Step 3: Static Reservations (Bind IP to MAC)", padx=10, pady=10)
        res_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(res_frame, text="IP Address:").grid(row=0, column=0)
        e_res_ip = tk.Entry(res_frame, width=20); e_res_ip.grid(row=0, column=1)

        tk.Label(res_frame, text="MAC Address:").grid(row=1, column=0)
        e_res_mac = tk.Entry(res_frame, width=20); e_res_mac.grid(row=1, column=1)
        tk.Label(res_frame, text="(e.g. 0050.56b6.3311)").grid(row=1, column=2)

        # Listbox for Reservations
        lb_res = tk.Listbox(res_frame, height=4, width=50)
        lb_res.grid(row=3, column=0, columnspan=3, pady=5)

        def add_reservation():
            ip = e_res_ip.get().strip()
            mac = e_res_mac.get().strip()
            if not ip or not mac: return
            
            # Update Visual
            lb_res.insert(tk.END, f"IP: {ip} | MAC: {mac}")
            # Call Backend
            self.log(f"\nAdding Reservation: {ip} for {mac}...")
            threading.Thread(target=self._thread_wrapper_reserve, args=(ip, mac)).start()

        tk.Button(res_frame, text="Add Reservation", command=add_reservation).grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

    # --- Backend Thread Wrappers for DHCP ---
    def _thread_wrapper_pool(self, params):
        try:
            logs = backendFinalVersion.run_dhcp_pool_logic(params, self.last_scan_results, self.SSH_USER, self.SSH_PASS, self.SSH_SECRET)
            for msg in logs: self.log(msg)
        except Exception as e: self.log(f"Pool Error: {e}")

    def _thread_wrapper_exclude(self, start, end):
        try:
            logs = backendFinalVersion.run_exclude_logic(start, end, self.last_scan_results, self.SSH_USER, self.SSH_PASS, self.SSH_SECRET)
            for msg in logs: self.log(msg)
        except Exception as e: self.log(f"Exclude Error: {e}")

    def _thread_wrapper_reserve(self, ip, mac):
        try:
            logs = backendFinalVersion.run_reservation_logic(ip, mac, self.last_scan_results, self.SSH_USER, self.SSH_PASS, self.SSH_SECRET)
            for msg in logs: self.log(msg)
        except Exception as e: self.log(f"Reservation Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()
