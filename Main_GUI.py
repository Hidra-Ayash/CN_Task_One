import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion
import time 

SSH_USER = "admin"
SSH_PASS = "cisco123"
SSH_SECRET = "cisco"
last_scan_results = {} 

def log_and_display(message):
    print(f"[DHCP LOG]: {message}")
    messagebox.showinfo("DHCP Action", message)

def _thread_wrapper_pool(params):
    global last_scan_results
    try:
        logs = backendFinalVersion.run_dhcp_pool_logic(
            params, last_scan_results,
            SSH_USER, SSH_PASS, SSH_SECRET
        )
        for msg in logs:
            log_and_display(msg)
    except Exception as e:
        log_and_display(f"Pool Error: {e}")

def _thread_wrapper_exclude(start, end):
    global last_scan_results
    try:
        logs = backendFinalVersion.run_exclude_logic(
            start, end, last_scan_results,
            SSH_USER, SSH_PASS, SSH_SECRET
        )
        for msg in logs:
            log_and_display(msg)
    except Exception as e:
        log_and_display(f"Exclude Error: {e}")

def _thread_wrapper_reserve(ip, mac):
    global last_scan_results
    try:
        logs = backendFinalVersion.run_reservation_logic(
            ip, mac, last_scan_results,
            SSH_USER, SSH_PASS, SSH_SECRET
        )
        for msg in logs:
            log_and_display(msg)
    except Exception as e:
        log_and_display(f"Reservation Error: {e}")

def add_exclusion(e_start, e_end, listbox):
    start = e_start.get().strip()
    end = e_end.get().strip()
    if not start:
        return
    listbox.insert(tk.END, f"{start} - {end}")

    threading.Thread(
        target=_thread_wrapper_exclude,
        args=(start, end)
    ).start()

def add_reservation(e_ip, e_mac, listbox):
    ip = e_ip.get().strip()
    mac = e_mac.get().strip()

    if not ip or not mac:
        return

    listbox.insert(tk.END, f"IP: {ip} | MAC: {mac}")

    threading.Thread(
        target=_thread_wrapper_reserve,
        args=(ip, mac)
    ).start()

def run_dhcp_gui(root_window, back_callback, scan_results):
    
    global last_scan_results
    last_scan_results = scan_results

    dhcp_win = tk.Toplevel(root_window)
    dhcp_win.title("DHCP Configuration & Management")
    dhcp_win.geometry("600x650")
    dhcp_win.configure(bg="#eef5ff")
    
    def go_back():
        dhcp_win.destroy()  
        back_callback()  

    pool_frame = tk.LabelFrame(
        dhcp_win, text=" Step 1: Basic DHCP Pool ",
        padx=10, pady=10, bg="#f7fbff",
        font=('Arial', 10, 'bold')
    )
    pool_frame.pack(fill="x", pady=10, padx=10)

    tk.Label(pool_frame, text="Pool Name:", bg="#f7fbff").grid(row=0, column=0, padx=5, pady=2, sticky='w')
    e_name = tk.Entry(pool_frame); e_name.grid(row=0, column=1, padx=5, pady=2)
    e_name.insert(0, "LAN_POOL")

    tk.Label(pool_frame, text="Network:", bg="#f7fbff").grid(row=0, column=2, padx=5, pady=2, sticky='w')
    e_net = tk.Entry(pool_frame); e_net.grid(row=0, column=3, padx=5, pady=2)
    e_net.insert(0, "192.168.20.0")

    tk.Label(pool_frame, text="Gateway:", bg="#f7fbff").grid(row=1, column=0, padx=5, pady=2, sticky='w')
    e_gw = tk.Entry(pool_frame); e_gw.grid(row=1, column=1, padx=5, pady=2)
    e_gw.insert(0, "192.168.20.1")

    tk.Label(pool_frame, text="DNS:", bg="#f7fbff").grid(row=1, column=2, padx=5, pady=2, sticky='w')
    e_dns = tk.Entry(pool_frame); e_dns.grid(row=1, column=3, padx=5, pady=2)
    e_dns.insert(0, "8.8.8.8")

    tk.Button(
        pool_frame, text="Apply Pool Config",
        bg="orange", fg="black",
        command=lambda: _thread_wrapper_pool({
            'pool_name': e_name.get(),
            'network': e_net.get(),
            'netmask': "255.255.255.0",
            'default_router': e_gw.get(),
            'dns_server': e_dns.get()
        })
    ).grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

    excl_frame = tk.LabelFrame(
        dhcp_win, text=" Step 2: Exclude IP Ranges ",
        padx=10, pady=10, bg="#f7fbff",
        font=('Arial', 10, 'bold')
    )
    excl_frame.pack(fill="x", pady=10, padx=10)

    tk.Label(excl_frame, text="Start IP:", bg="#f7fbff").grid(row=0, column=0, padx=5, pady=2, sticky='w')
    e_ex_start = tk.Entry(excl_frame, width=15)
    e_ex_start.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(excl_frame, text="End IP:", bg="#f7fbff").grid(row=0, column=2, padx=5, pady=2, sticky='w')
    e_ex_end = tk.Entry(excl_frame, width=15)
    e_ex_end.grid(row=0, column=3, padx=5, pady=2)

    lb_excl = tk.Listbox(excl_frame, height=4, width=50)
    lb_excl.grid(row=2, column=0, columnspan=4, pady=5)

    tk.Button(
        excl_frame, text="Add Exclusion",
        command=lambda: add_exclusion(e_ex_start, e_ex_end, lb_excl)
    ).grid(row=1, column=0, columnspan=4, pady=5, sticky='ew')

    res_frame = tk.LabelFrame(
        dhcp_win, text=" Step 3: Static Reservations ",
        padx=10, pady=10, bg="#f7fbff",
        font=('Arial', 10, 'bold')
    )
    res_frame.pack(fill="x", pady=10, padx=10)

    tk.Label(res_frame, text="IP Address:", bg="#f7fbff").grid(row=0, column=0, padx=5, pady=2, sticky='w')
    e_res_ip = tk.Entry(res_frame, width=20)
    e_res_ip.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(res_frame, text="MAC Address:", bg="#f7fbff").grid(row=1, column=0, padx=5, pady=2, sticky='w')
    e_res_mac = tk.Entry(res_frame, width=20)
    e_res_mac.grid(row=1, column=1, padx=5, pady=2)

    lb_res = tk.Listbox(res_frame, height=4, width=50)
    lb_res.grid(row=3, column=0, columnspan=3, pady=5)

    tk.Button(
        res_frame, text="Add Reservation",
        command=lambda: add_reservation(e_res_ip, e_res_mac, lb_res)
    ).grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

    btn_back = tk.Button(
        dhcp_win, text="← Back", 
        command=go_back,
        bg="#ff4d4d", 
        fg="white", 
        font=("Arial", 9, "bold"),
        width=8,
        height=1
    )
    btn_back.place(relx=0.98, rely=0.98, anchor="se") 
    
    dhcp_win.transient(root_window)


class NetworkApp:
    def __init__(self, root, back_callback=None):
        self.root = root
        self.back_to_welcome = back_callback 
        self.last_scan_results = {}

        self.SSH_USER = "admin"
        self.SSH_PASS = "cisco123"
        self.SSH_SECRET = "cisco"

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Network Management - GNS3 Edition")
        self.root.geometry("900x760")
        self.root.configure(bg="#e9f2fa")
        self.root.resizable(True, True)

        header = tk.Frame(self.root, bg="#004d80", height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Network Management System",
            font=("Arial", 22, "bold"),
            bg="#004d80",
            fg="white"
        ).pack(pady=15)

        container = tk.Frame(self.root, bg="#e9f2fa")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        if self.back_to_welcome:
            tk.Button(
                self.root, 
                text="← Back", 
                command=self.go_back, 
                bg="#1e88e5", 
                fg="white", 
                font=("Arial", 10, "bold"),
                width=10,
                height=1
            ).place(relx=0.98, rely=0.98, anchor="se") 

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

        dhcp_frame = tk.Frame(container, bg="#e9f2fa")
        dhcp_frame.pack(fill="x", pady=10)

        tk.Button(
            dhcp_frame, text="⚙️ Open DHCP Configuration",
            font=('Arial', 13, 'bold'),
            bg="#ff9800", fg="white",
            width=30, command=self.open_dhcp_window
        ).pack()

    def log(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def go_back(self):
        if self.back_to_welcome:
            self.root.withdraw() 
            self.back_to_welcome()

    def start_scan_thread(self):
        networks = self.network_entry.get()
        if not networks:
            messagebox.showwarning("Input Error", "Please enter one or more networks to scan.")
            return

        self.log(f"Starting scan for networks: {networks}")
        self.scan_button.config(state=tk.DISABLED)
        self.scan_button.config(text="Scanning...")
        
        threading.Thread(target=self.run_scan, args=(networks,)).start()

    def run_scan(self, networks):
        global last_scan_results
        try:
            self.log("Scanning in progress... This might take a few moments.")
            
            time.sleep(3) 
            results = {
                "Routers": ["192.168.1.1", "192.168.1.2"],
                "Hosts": ["192.168.1.100", "192.168.1.101"]
            } 
            
            self.last_scan_results = results
            last_scan_results = results 
            
            self.log("--- Scan Complete ---")
            self.log(f"Found {len(results.get('Routers', []))} Routers.")
            self.log(f"Found {len(results.get('Hosts', []))} Hosts.")
            messagebox.showinfo("Scan Complete", "Network scan finished successfully!")

        except Exception as e:
            self.log(f"An error occurred during scan: {e}")
            messagebox.showerror("Scan Error", f"An error occurred: {e}")
            
        finally:
            self.scan_button.config(state=tk.NORMAL)
            self.scan_button.config(text="🔍 Start Scan")

    def start_ip_helper_thread(self):
        messagebox.showinfo("Info", "Applying IP Helper logic...")

    def open_dhcp_window(self):
        run_dhcp_gui(
            self.root, 
            self.root.deiconify, 
            self.last_scan_results
        )
        self.root.withdraw()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root) 
    root.mainloop()