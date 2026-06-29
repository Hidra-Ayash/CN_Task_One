import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion 
import config
import ipaddress
import re

# Login credentials (centralized)
SSH_USER = getattr(config, 'SSH_USER', 'admin')
SSH_PASS = getattr(config, 'SSH_PASS', 'cisco123')
SSH_SECRET = getattr(config, 'SSH_SECRET', 'cisco')
last_scan_results = {} 

def run_dhcp_gui(root_window, back_callback, scan_results):
    """
    هذه الدالة تستقبل النافذة الرئيسية (root_window) ودالة الرجوع (back_callback)
    ونتائج الفحص (scan_results) لتشغيل الواجهة.
    """
    
    global last_scan_results
    last_scan_results = scan_results

    dhcp_win = tk.Toplevel(root_window)
    dhcp_win.title("DHCP Configuration & Management")
    dhcp_win.geometry("600x650")
    dhcp_win.configure(bg="#eef5ff")
    
    def go_back():
        dhcp_win.destroy()  # إغلاق نافذة DHCP
        back_callback()   
        

    # -----------------------------------------------------------------
    # دالة Log (لعرض الرسائل في الواجهة الرئيسية)
    def log_and_display(message):
        # Log messages only; final dialogs are shown by wrapper functions
        import logging
        logging.info(f"[DHCP LOG]: {message}")

    def _thread_wrapper_pool(params):
        try:
            logs = backendFinalVersion.run_dhcp_pool_logic(
                params, last_scan_results,
                SSH_USER, SSH_PASS, SSH_SECRET
            )
            import logging
            for msg in logs:
                logging.info(msg)

            joined = "\n".join(logs) if isinstance(logs, list) else str(logs)
            lower = joined.lower()
            if any(k in lower for k in ("error", "failure", "failed", "no routers", "exception")):
                dhcp_win.after(0, lambda: messagebox.showerror("DHCP Pool", f"Failed to apply DHCP pool"))
            else:
                dhcp_win.after(0, lambda: messagebox.showinfo("DHCP Pool", f"DHCP pool applied successfully"))

        except Exception as e:
            dhcp_win.after(0, lambda: messagebox.showerror("DHCP Pool", f"Exception: {e}"))

    def add_exclusion(e_start, e_end, listbox):
        start = e_start.get().strip()
        end = e_end.get().strip()
        if not start:
            dhcp_win.after(0, lambda: messagebox.showwarning("Input Required", "Please enter start IP."))
            return

        # Validate IP addresses
        try:
            ipaddress.ip_address(start)
            if end:
                ipaddress.ip_address(end)
        except Exception:
            dhcp_win.after(0, lambda: messagebox.showwarning("Invalid Input", "Please enter valid IP addresses."))
            return

        listbox.insert(tk.END, f"{start} - {end}")

        threading.Thread(
            target=_thread_wrapper_exclude,
            args=(start, end),
            daemon=True
        ).start()


    def _thread_wrapper_exclude(start, end):
        try:
            logs = backendFinalVersion.run_exclude_logic(
                start, end, last_scan_results,
                SSH_USER, SSH_PASS, SSH_SECRET
            )
            import logging
            for msg in logs:
                logging.info(msg)

            joined = "\n".join(logs) if isinstance(logs, list) else str(logs)
            lower = joined.lower()
            if any(k in lower for k in ("error", "failure", "failed", "exception")):
                dhcp_win.after(0, lambda: messagebox.showerror("DHCP Exclusion", f"Failed to add exclusion:\n{joined}"))
            else:
                dhcp_win.after(0, lambda: messagebox.showinfo("DHCP Exclusion", f"Exclusion added successfully.\n{joined}"))

        except Exception as e:
            dhcp_win.after(0, lambda: messagebox.showerror("DHCP Exclusion", f"Exception: {e}"))

    def add_reservation(e_ip, e_mac, listbox):
        ip = e_ip.get().strip()
        mac = e_mac.get().strip()

        if not ip or not mac:
            dhcp_win.after(0, lambda: messagebox.showwarning("Input Required", "Please enter IP and MAC address."))
            return

        # Validate IP
        try:
            ipaddress.ip_address(ip)
        except Exception:
            dhcp_win.after(0, lambda: messagebox.showwarning("Invalid Input", "Please enter a valid IP address."))
            return

        # Validate MAC
        cleaned_mac = mac.replace(':', '').replace('-', '').lower()
        if len(cleaned_mac) != 12 or not all(c in '0123456789abcdef' for c in cleaned_mac):
            dhcp_win.after(0, lambda: messagebox.showwarning("Invalid Input", "Please enter a valid MAC address."))
            return

        listbox.insert(tk.END, f"IP: {ip} | MAC: {mac}")

        threading.Thread(
            target=_thread_wrapper_reserve,
            args=(ip, mac),
            daemon=True
        ).start()

    def _thread_wrapper_reserve(ip, mac):
        try:
            logs = backendFinalVersion.run_reservation_logic(
                ip, mac, last_scan_results,
                SSH_USER, SSH_PASS, SSH_SECRET
            )
            import logging
            for msg in logs:
                logging.info(msg)

            joined = "\n".join(logs) if isinstance(logs, list) else str(logs)
            lower = joined.lower()
            if any(k in lower for k in ("error", "failure", "failed", "exception")):
                dhcp_win.after(0, lambda: messagebox.showerror("DHCP Reservation", f"Failed to add reservation"))
            else:
                dhcp_win.after(0, lambda: messagebox.showinfo("DHCP Reservation", f"Reservation added successfully."))

        except Exception as e:
            dhcp_win.after(0, lambda: messagebox.showerror("DHCP Reservation", f"Exception: {e}"))

    # -----------------------------------------------------------------
    # =================== تصميم الواجهة (من كودك الأصلي) ===================
    # -----------------------------------------------------------------

    # =================== BASIC POOL ===================
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

    def apply_pool_click():
        pool_name = e_name.get().strip()
        network = e_net.get().strip()
        default_router = e_gw.get().strip()
        dns_server = e_dns.get().strip()

        if not pool_name or not network or not default_router or not dns_server:
            dhcp_win.after(0, lambda: messagebox.showwarning("Input Required", "Please fill all DHCP Pool fields."))
            return

        try:
            ipaddress.ip_address(network)
            ipaddress.ip_address(default_router)
            ipaddress.ip_address(dns_server)
        except Exception:
            dhcp_win.after(0, lambda: messagebox.showwarning("Invalid Input", "Please enter valid IPv4 addresses."))
            return

        threading.Thread(
            target=lambda: _thread_wrapper_pool({
                'pool_name': pool_name,
                'network': network,
                'netmask': "255.255.255.0",
                'default_router': default_router,
                'dns_server': dns_server
            }),
            daemon=True
        ).start()

    tk.Button(
        pool_frame, text="Apply Pool Config",
        bg="orange", fg="black",
        command=apply_pool_click
    ).grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

    # =================== EXCLUSIONS ===================
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

    # =================== RESERVATIONS ===================
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
        bg="#ff4d4d", # لون مميز
        fg="white", 
        font=("Arial", 9, "bold"),
        width=8,
        height=1
    )
    btn_back.place(relx=0.98, rely=0.98, anchor="se") 
    
    dhcp_win.transient(root_window) 
