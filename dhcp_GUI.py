import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import backendFinalVersion # نفترض أن هذا الملف موجود

# ملاحظة: يجب أن تكون هذه المتغيرات عامة (Global) أو يتم تمريرها للدالة
# لكي يعمل منطق الباك إند (backendFinalVersion) بشكل صحيح.

# بيانات الدخول يتم جلبها من الواجهة الرئيسية
SSH_USER = "admin"
SSH_PASS = "cisco123"
SSH_SECRET = "cisco"
last_scan_results = {} # نتائج الفحص الأخيرة يتم جلبها من الواجهة الرئيسية


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
    
    # دالة زر الرجوع
    def go_back():
        dhcp_win.destroy()  # إغلاق نافذة DHCP
        back_callback()   # استدعاء دالة إظهار القائمة الرئيسية

    # -----------------------------------------------------------------
    # دالة Log (مبسطة لتعرض الرسائل في الواجهة الرئيسية)
    def log_and_display(message):
        # في بيئة الإنتاج، يجب أن يتم إرسال هذا إلى log في الواجهة الرئيسية
        print(f"[DHCP LOG]: {message}")
        messagebox.showinfo("DHCP Action", message)

    # دالة wrapper لـ Pool (نسخة معدلة من الكود الأصلي)
    def _thread_wrapper_pool(params):
        try:
            # هنا يجب استدعاء دالة log_and_display
            logs = backendFinalVersion.run_dhcp_pool_logic(
                params, last_scan_results,
                SSH_USER, SSH_PASS, SSH_SECRET
            )
            for msg in logs:
                log_and_display(msg)
        except Exception as e:
            log_and_display(f"Pool Error: {e}")

    # دالة add_exclusion (نسخة معدلة من الكود الأصلي)
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

    # دالة wrapper لـ Exclude (نسخة معدلة من الكود الأصلي)
    def _thread_wrapper_exclude(start, end):
        try:
            logs = backendFinalVersion.run_exclude_logic(
                start, end, last_scan_results,
                SSH_USER, SSH_PASS, SSH_SECRET
            )
            for msg in logs:
                log_and_display(msg)
        except Exception as e:
            log_and_display(f"Exclude Error: {e}")

    # دالة add_reservation (نسخة معدلة من الكود الأصلي)
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

    # دالة wrapper لـ Reserve (نسخة معدلة من الكود الأصلي)
    def _thread_wrapper_reserve(ip, mac):
        try:
            logs = backendFinalVersion.run_reservation_logic(
                ip, mac, last_scan_results,
                SSH_USER, SSH_PASS, SSH_SECRET
            )
            for msg in logs:
                log_and_display(msg)
        except Exception as e:
            log_and_display(f"Reservation Error: {e}")

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

    # 5. زر الرجوع (صغير جداً وفي الزاوية اليمنى السفلية)
    btn_back = tk.Button(
        dhcp_win, text="← Back", 
        command=go_back,
        bg="#ff4d4d", # لون مميز
        fg="white", 
        font=("Arial", 9, "bold"),
        width=8,
        height=1
    )
    # استخدام place لوضعه في الزاوية
    btn_back.place(relx=0.98, rely=0.98, anchor="se") 
    
    dhcp_win.transient(root_window) # لجعل النافذة الفرعية تظهر فوق الرئيسية

# ملاحظة: تم حذف قسم الـ main من هذا الملف