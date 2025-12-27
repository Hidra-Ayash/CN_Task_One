import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.last_scan_results = {}

        # بيانات الدخول
        self.SSH_USER = "admin"
        self.SSH_PASS = "cisco123"
        self.SSH_SECRET = "cisco"
        
        # ألوان حديثة
        self.PRIMARY_COLOR = "#004d80"   # Dark Blue
        self.SECONDARY_COLOR = "#1e88e5" # Light Blue
        self.BG_LIGHT = "#f7fbff"        # Very Light Blue
        self.BG_DARK = "#e9f2fa"         # Slightly Darker
        self.ACCENT_SCAN = "#2e8b57"     # Green
        self.ACCENT_DHCP = "#ff9800"     # Orange

        self.setup_gui()

    # ---------------- GUI SETUP ----------------
    def setup_gui(self):
        self.root.title("🌐 Network Management System")
        self.root.geometry("1100x780")
        self.root.minsize(900, 700)
        self.root.configure(bg=self.BG_DARK)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # ===== HEADER =====
        header = tk.Frame(self.root, bg=self.PRIMARY_COLOR, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="💻 Network Management System",
            font=("Segoe UI", 24, "bold"),
            bg=self.PRIMARY_COLOR,
            fg="white"
        ).grid(row=0, column=0, pady=15)

        # ===== MAIN CONTAINER =====
        container = tk.Frame(self.root, bg=self.BG_DARK)
        container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # ===== SCAN NETWORK =====
        scan_frame = tk.LabelFrame(container, text="🌐 Scan Network", font=('Segoe UI', 12, 'bold'),
                                   bg=self.BG_LIGHT, fg=self.PRIMARY_COLOR, padx=15, pady=15)
        scan_frame.grid(row=0, column=0, sticky="ew", pady=10)
        scan_frame.grid_columnconfigure(1, weight=1)

        tk.Label(scan_frame, text="Target Networks (CIDR List):", font=('Segoe UI', 11), bg=self.BG_LIGHT).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.network_entry = tk.Entry(scan_frame, font=('Segoe UI', 11), relief=tk.FLAT, bd=2)
        self.network_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.network_entry.insert(0, "192.168.20.0/24, 192.168.31.0/24, 192.168.32.0/24")

        tk.Button(scan_frame, text="🔍 Start Scan", font=('Segoe UI', 11, 'bold'),
                  bg=self.ACCENT_SCAN, fg="white", relief=tk.FLAT, width=15,
                  activebackground="#246b45", command=self.start_scan_thread).grid(row=0, column=2, padx=10, pady=5)

        # ===== OUTPUT LOG =====
        output_frame = tk.LabelFrame(container, text="📝 Scan Results / Logs", font=('Segoe UI', 12, 'bold'),
                                     bg=self.BG_LIGHT, fg=self.PRIMARY_COLOR, padx=10, pady=10)
        output_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, font=('Consolas', 10),
                                                     relief=tk.FLAT, bd=2, bg="white")
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_text.config(state=tk.DISABLED)

        # ===== IP HELPER =====
        helper_frame = tk.LabelFrame(container, text="⚙️ IP Helper Configuration", font=('Segoe UI', 12, 'bold'),
                                     bg=self.BG_LIGHT, fg=self.PRIMARY_COLOR, padx=15, pady=15)
        helper_frame.grid(row=2, column=0, sticky="ew", pady=10)
        helper_frame.grid_columnconfigure(1, weight=1)

        tk.Label(helper_frame, text="Target DHCP Server IP:", font=('Segoe UI', 11), bg=self.BG_LIGHT).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.ip_helper_entry = tk.Entry(helper_frame, font=('Segoe UI', 11), relief=tk.FLAT, bd=2)
        self.ip_helper_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Button(helper_frame, text="Apply IP Helper", font=('Segoe UI', 11, 'bold'),
                  bg=self.SECONDARY_COLOR, fg="white", relief=tk.FLAT, width=18,
                  activebackground="#1665b3", command=self.start_ip_helper_thread).grid(row=0, column=2, padx=10, pady=5)

        # ===== DHCP CONFIG BUTTON =====
        dhcp_frame = tk.Frame(container, bg=self.BG_DARK)
        dhcp_frame.grid(row=3, column=0, sticky="ew", pady=10)
        dhcp_frame.grid_columnconfigure(0, weight=1)

        tk.Button(dhcp_frame, text="🛠️ Open DHCP Configuration", font=('Segoe UI', 13, 'bold'),
                  bg=self.ACCENT_DHCP, fg="white", relief=tk.FLAT, width=30, height=2,
                  activebackground="#e07a00", command=self.open_dhcp_window).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # ---------------- LOG ----------------
    def log(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    # ---------------- SCAN NETWORK ----------------
    def start_scan_thread(self):
        target_networks = [n.strip() for n in self.network_entry.get().split(',') if n.strip()]
        if not target_networks:
            messagebox.showwarning("Input Error", "Please enter target networks.")
            return
        self.log(f"Starting Scan on {target_networks}...")
        threading.Thread(target=self.run_scan, args=(target_networks,)).start()

    def run_scan(self, target_networks):
        try:
            # Mock results
            results = {
                "Routers": [{'ip': '192.168.20.1', 'descr': 'Core Router R1'}],
                "Switches": [{'ip': '192.168.20.10', 'descr': 'Access SW A1'}]
            }
            self.last_scan_results = results

            self.log("-" * 60)
            for category, devices in results.items():
                if devices:
                    self.log(f"[{category}]: {len(devices)} found.")
                    for dev in devices:
                        self.log(f" - IP: {dev['ip']} | {dev['descr']}")
            self.log("-" * 60)
        except Exception as e:
            self.log(f"Scan Error: {e}")

    # ---------------- IP HELPER ----------------
    def start_ip_helper_thread(self):
        target_ip = self.ip_helper_entry.get().strip()
        if not target_ip or not self.last_scan_results:
            messagebox.showwarning("Error", "Run Scan first & Enter IP.")
            return
        self.log(f"\nApplying IP Helper {target_ip}...")
        threading.Thread(target=self.run_ip_helper, args=(target_ip,)).start()

    def run_ip_helper(self, target_ip):
        try:
            self.log(f"Applied IP helper address {target_ip} to relevant interfaces.")
        except Exception as e:
            self.log(f"Config Error: {e}")

    # ---------------- DHCP WINDOW ----------------
    def open_dhcp_window(self):
        if not self.last_scan_results.get("Routers"):
            messagebox.showwarning("No Routers", "No Routers found in scan results! Cannot configure DHCP.")
            return

        dhcp_win = tk.Toplevel(self.root)
        dhcp_win.title("DHCP Configuration & Management")
        dhcp_win.geometry("650x700")
        dhcp_win.configure(bg=self.BG_DARK)
        dhcp_win.grid_columnconfigure(0, weight=1)
        dhcp_win.grid_rowconfigure(3, weight=1)

        # --- DHCP Pool ---
        pool_frame = tk.LabelFrame(dhcp_win, text="1️⃣ Basic DHCP Pool", padx=15, pady=15,
                                   bg=self.BG_LIGHT, fg=self.PRIMARY_COLOR, font=('Segoe UI', 11, 'bold'))
        pool_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=20)
        pool_frame.grid_columnconfigure(1, weight=1)
        pool_frame.grid_columnconfigure(3, weight=1)

        e_name = self._create_dhcp_entry(pool_frame, "Pool Name:", 0, 0, "LAN_POOL")
        e_net  = self._create_dhcp_entry(pool_frame, "Network:", 0, 2, "192.168.20.0")
        e_gw   = self._create_dhcp_entry(pool_frame, "Gateway:", 1, 0, "192.168.20.1")
        e_dns  = self._create_dhcp_entry(pool_frame, "DNS:", 1, 2, "8.8.8.8")

        tk.Button(pool_frame, text="✅ Apply Pool Config", font=('Segoe UI', 11, 'bold'),
                  bg=self.ACCENT_DHCP, fg="white", relief=tk.FLAT, height=2,
                  command=lambda: self._thread_wrapper_pool({
                      'pool_name': e_name.get(),
                      'network': e_net.get(),
                      'netmask': "255.255.255.0",
                      'default_router': e_gw.get(),
                      'dns_server': e_dns.get()
                  })).grid(row=2, column=0, columnspan=4, pady=(20, 10), padx=5, sticky="ew")

        # --- EXCLUSIONS ---
        excl_frame = tk.LabelFrame(dhcp_win, text="2️⃣ Exclude IP Ranges", padx=15, pady=15,
                                   bg=self.BG_LIGHT, fg=self.PRIMARY_COLOR, font=('Segoe UI', 11, 'bold'))
        excl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=20)
        excl_frame.grid_columnconfigure(1, weight=1)
        excl_frame.grid_columnconfigure(3, weight=1)

        tk.Label(excl_frame, text="Start IP:", bg=self.BG_LIGHT).grid(row=0, column=0, padx=5, pady=5)
        e_ex_start = tk.Entry(excl_frame, font=('Segoe UI', 10), relief=tk.FLAT, bd=2)
        e_ex_start.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(excl_frame, text="End IP:", bg=self.BG_LIGHT).grid(row=0, column=2, padx=5, pady=5)
        e_ex_end = tk.Entry(excl_frame, font=('Segoe UI', 10), relief=tk.FLAT, bd=2)
        e_ex_end.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        lb_excl = tk.Listbox(excl_frame, height=4, font=('Consolas', 10), relief=tk.FLAT, bd=2)
        lb_excl.grid(row=2, column=0, columnspan=4, pady=5, padx=5, sticky="ew")

        tk.Button(excl_frame, text="➕ Add Exclusion & Apply", font=('Segoe UI', 10, 'bold'),
                  bg="#f44336", fg="white", relief=tk.FLAT,
                  command=lambda: self.add_exclusion(e_ex_start, e_ex_end, lb_excl)).grid(row=1, column=0, columnspan=4, pady=10, padx=5, sticky='ew')

        # --- RESERVATIONS ---
        res_frame = tk.LabelFrame(dhcp_win, text="3️⃣ Static Reservations", padx=15, pady=15,
                                  bg=self.BG_LIGHT, fg=self.PRIMARY_COLOR, font=('Segoe UI', 11, 'bold'))
        res_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=20)
        res_frame.grid_columnconfigure(1, weight=1)

        tk.Label(res_frame, text="IP Address:", bg=self.BG_LIGHT).grid(row=0, column=0, padx=5, pady=5)
        e_res_ip = tk.Entry(res_frame, font=('Segoe UI', 10), relief=tk.FLAT, bd=2)
        e_res_ip.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(res_frame, text="MAC Address:", bg=self.BG_LIGHT).grid(row=1, column=0, padx=5, pady=5)
        e_res_mac = tk.Entry(res_frame, font=('Segoe UI', 10), relief=tk.FLAT, bd=2)
        e_res_mac.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        lb_res = tk.Listbox(res_frame, height=4, font=('Consolas', 10), relief=tk.FLAT, bd=2)
        lb_res.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="ew")

        tk.Button(res_frame, text="💾 Add Reservation & Apply", font=('Segoe UI', 10, 'bold'),
                  bg=self.SECONDARY_COLOR, fg="white", relief=tk.FLAT,
                  command=lambda: self.add_reservation(e_res_ip, e_res_mac, lb_res)).grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky='ew')

    # ------------------- HELPERS -------------------
    def _create_dhcp_entry(self, parent_frame, label_text, row, col, default_value=""):
        tk.Label(parent_frame, text=label_text, bg=self.BG_LIGHT, anchor="w", width=10).grid(row=row, column=col, padx=(10, 0), pady=5, sticky="w")
        entry = tk.Entry(parent_frame, font=('Segoe UI', 10), relief=tk.FLAT, bd=2)
        entry.grid(row=row, column=col + 1, padx=(0, 10), pady=5, sticky="ew")
        entry.insert(0, default_value)
        return entry

    # ------------------- DHCP LOGIC -------------------
    def add_exclusion(self, e_start, e_end, listbox):
        start = e_start.get().strip()
        end = e_end.get().strip()
        if not start:
            messagebox.showwarning("Input Missing", "Please enter a Start IP for exclusion.")
            return
        listbox.insert(tk.END, f"❌ {start} - {end or 'Single IP'}")
        threading.Thread(target=self._thread_wrapper_exclude, args=(start, end)).start()
        e_start.delete(0, tk.END)
        e_end.delete(0, tk.END)

    def add_reservation(self, e_ip, e_mac, listbox):
        ip = e_ip.get().strip()
        mac = e_mac.get().strip()
        if not ip or not mac:
            messagebox.showwarning("Input Missing", "Please enter both IP and MAC addresses.")
            return
        listbox.insert(tk.END, f"📌 IP: {ip} | MAC: {mac}")
        threading.Thread(target=self._thread_wrapper_reserve, args=(ip, mac)).start()
        e_ip.delete(0, tk.END)
        e_mac.delete(0, tk.END)

    # ------------------- THREAD WRAPPERS -------------------
    def _thread_wrapper_pool(self, params):
        try:
            self.log(f"Successfully configured DHCP Pool: {params['pool_name']}")
        except Exception as e:
            self.log(f"Pool Error: {e}")

    def _thread_wrapper_exclude(self, start, end):
        try:
            self.log(f"Excluded IP range: {start} to {end or start}")
        except Exception as e:
            self.log(f"Exclude Error: {e}")

    def _thread_wrapper_reserve(self, ip, mac):
        try:
            self.log(f"Added static reservation for IP {ip} (MAC: {mac})")
        except Exception as e:
            self.log(f"Reservation Error: {e}")

# ------------------- MAIN -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()
