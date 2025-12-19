import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from PIL import Image, ImageTk 
import sys
import VPN_GUI  # استيراد ملف الواجهة المنفصل

# محاولة استيراد الملفات الأخرى
try:
    import backendFinalVersion
    from Main_GUI import NetworkApp
except ImportError:
    class MockBackend:
        def run_dns_config_logic(self, *args):
            import time
            time.sleep(1)
            return ["Mock configuration applied."]
    backendFinalVersion = MockBackend()
    
    class NetworkApp:
        def __init__(self, root, back_callback):
            self.root = root
            self.back_callback = back_callback
            ctk.CTkLabel(root, text="Mock DHCP Interface").pack(pady=20)
            ctk.CTkButton(root, text="Back", command=back_callback).pack()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ---------------------------------------------------------
# وظيفة تحميل الخلفية بشكل آمن
# ---------------------------------------------------------
def safe_load_image(path):
    try:
        return Image.open(path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# ---------------------------------------------------------
# دالة تشغيل واجهة VPN (الربط الجديد)
# ---------------------------------------------------------
def launch_vpn_interface():
    # استدعاء دالة فتح نافذة VPN من الملف المنفصل
    VPN_GUI.open_vpn_window(welcome_root)

# ---------------------------------------------------------
# DNS Interface Window
# ---------------------------------------------------------
def open_dns_interface_window():
    welcome_root.withdraw()
    dns_win = tk.Toplevel(welcome_root)
    dns_win.minsize(900, 700)
    dns_win.geometry("1000x700")
    dns_win.title("Unified Network Configuration Tool DNS")
    dns_win.configure(bg="#f0f8ff")

    def go_back_to_welcome():
        dns_win.destroy()
        welcome_root.deiconify()

    main_frame = tk.Frame(dns_win, bg="#f0f8ff", padx=30, pady=30)
    main_frame.pack(fill="both", expand=True)

    title_label = tk.Label(main_frame, text="🌐 Unified Network Settings (DNS)", 
                          font=('Segoe UI', 24, 'bold'), bg="#f0f8ff", fg="#1e88e5")
    title_label.pack(pady=(20, 40))

    network_config_frame = tk.LabelFrame(main_frame, text=" ⚙️ Core Network Configuration ",
                                        font=('Arial', 14, 'bold'), bg="#ffffff", fg="#34495e",
                                        padx=40, pady=40, highlightthickness=2)
    network_config_frame.pack(fill="x", padx=100, pady=20)

    # الحقول (Router & DNS)
    tk.Label(network_config_frame, text="Router Gateway IP:", font=('Arial', 12, 'bold'), bg="#ffffff").grid(row=0, column=0, padx=20, pady=15, sticky="w")
    router_entry = tk.Entry(network_config_frame, width=35, font=('Arial', 12))
    router_entry.grid(row=0, column=1, padx=20, pady=15, sticky="we")

    tk.Label(network_config_frame, text="Primary DNS Server IP:", font=('Arial', 12, 'bold'), bg="#ffffff").grid(row=1, column=0, padx=20, pady=15, sticky="w")
    dns_entry = tk.Entry(network_config_frame, width=35, font=('Arial', 12))
    dns_entry.grid(row=1, column=1, padx=20, pady=15, sticky="we")

    def apply_config():
        router_ip = router_entry.get()
        primary_dns = dns_entry.get()
        def run_thread():
            apply_button.config(state=tk.DISABLED, text="Applying...")
            try:
                logs = backendFinalVersion.run_dns_config_logic(router_ip, primary_dns, "admin", "cisco123", "cisco")
                messagebox.showinfo("Result", "\n".join(logs))
            finally:
                apply_button.config(state=tk.NORMAL, text="🚀 Apply All Settings")
        threading.Thread(target=run_thread).start()

    apply_button = tk.Button(network_config_frame, text="🚀 Apply All Settings", command=apply_config,
                            font=('Arial', 13, 'bold'), bg="#2ecc71", fg="white", pady=8)
    apply_button.grid(row=2, column=0, columnspan=2, pady=30)

    tk.Button(dns_win, text="⬅️ Back", font=('Arial', 11, 'bold'), bg="#e74c3c", fg="white",
              command=go_back_to_welcome).place(relx=0.97, rely=0.97, anchor="se")

# ---------------------------------------------------------
# MAIN EXECUTION BLOCK (خلفية متجاوبة)
# ---------------------------------------------------------
bg_image = None
canvas_main = None
bg_photo_main = None
canvas_bg_main = None
header_window = None
button_frame_window = None
btn_exit = None

def resize_bg_main(event=None):
    global bg_photo_main, bg_image, canvas_main, canvas_bg_main
    global header_window, button_frame_window, welcome_root, WINDOW_WIDTH, WINDOW_HEIGHT
    
    if event is not None and event.widget != welcome_root:
        return 
        
    new_width = welcome_root.winfo_width()
    new_height = welcome_root.winfo_height()
        
    if bg_image:
        try:
            resized = bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            bg_photo_main = ImageTk.PhotoImage(resized)
            canvas_main.itemconfig(canvas_bg_main, image=bg_photo_main)
        except: pass
    
    if header_window is not None:
        canvas_main.coords(header_window, new_width // 2, int(new_height * 0.15))
    if button_frame_window is not None:
        canvas_main.coords(button_frame_window, new_width // 2, int(new_height * 0.52))
    if btn_exit is not None:
        btn_exit.place(relx=0.97, rely=0.97, anchor="se")

if __name__ == "__main__":
    welcome_root = ctk.CTk()
    welcome_root.title("Computer Network Management Dashboard")
    WINDOW_WIDTH, WINDOW_HEIGHT = 700, 600
    welcome_root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    bg_image = safe_load_image("background_main.jpg")
    background_color = "#FFFFFF" if bg_image else "#f5f7fa"
    canvas_main = ctk.CTkCanvas(welcome_root, highlightthickness=0, bg=background_color)
    canvas_main.pack(fill="both", expand=True)
    
    if bg_image:
        bg_photo_main = ImageTk.PhotoImage(bg_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT)))
        canvas_bg_main = canvas_main.create_image(0, 0, image=bg_photo_main, anchor="nw")

    welcome_root.bind("<Configure>", resize_bg_main)

    network_app_root = tk.Tk()
    network_app_root.withdraw()
    app_instance = NetworkApp(network_app_root, back_callback=lambda: [network_app_root.withdraw(), welcome_root.deiconify()])

    # --- UI Elements ---
    header_label = ctk.CTkLabel(master=welcome_root, text="Network Management Control Center",
                               font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
                               text_color="black" if bg_image else "#1F6AA5", fg_color="transparent")
    header_window = canvas_main.create_window(WINDOW_WIDTH // 2, 100, window=header_label)

    button_frame = ctk.CTkFrame(welcome_root, fg_color="transparent", corner_radius=18, border_color="#1F6AA5", border_width=2)
    button_frame_window = canvas_main.create_window(WINDOW_WIDTH // 2, 350, window=button_frame)
    
    # زر DHCP (أخضر)
    ctk.CTkButton(master=button_frame, text="DHCP Configuration", font=("Arial", 18, "bold"),
                  width=350, height=55, corner_radius=12, fg_color="#0CC43A", hover_color="#09a632",
                  command=lambda: [welcome_root.withdraw(), network_app_root.deiconify()]).pack(pady=(20, 10), padx=30)

    # زر DNS (أزرق)
    ctk.CTkButton(master=button_frame, text="DNS Configuration", font=("Arial", 18, "bold"),
                  width=350, height=55, corner_radius=12, fg_color="#3498db", hover_color="#2980b9",
                  command=open_dns_interface_window).pack(pady=10, padx=30)

    # زر VPN (بنفسجي - الإضافة الجديدة)
    ctk.CTkButton(master=button_frame, text="VPN Configuration", font=("Arial", 18, "bold"),
                  width=350, height=55, corner_radius=12, fg_color="#8e44ad", hover_color="#732d91",
                  command=launch_vpn_interface).pack(pady=(10, 20), padx=30)

    # زر الخروج
    btn_exit = ctk.CTkButton(master=welcome_root, text="Exit", font=("Arial", 14, "bold"),
                            width=100, height=35, corner_radius=10, fg_color="#CC0000",
                            command=lambda: sys.exit())
    btn_exit.place(relx=0.97, rely=0.97, anchor="se") 

    welcome_root.update()
    resize_bg_main(None)
    welcome_root.mainloop()