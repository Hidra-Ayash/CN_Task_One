import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from PIL import Image, ImageTk, ImageDraw
import sys
import math
import VPN_GUI
import VLAN_Routing
import config
import backendFinalVersion
import ipaddress

try:
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

# إعدادات الواجهة المستقبلية
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

SPACE_DARK = "#050b14"
SPACE_MID = "#0a1628"
SPACE_LIGHT = "#0f2138"
NEON_BLUE = "#00d4ff"
NEON_CYAN = "#00ffff"
NEON_PURPLE = "#b300ff"
SILVER = "#c0c0c0"
HOLO_GREEN = "#00ff88"
WARP_CORE = "#ff3366"
STAR_WHITE = "#e8eef2"
DEEP_SPACE = "#01050f"

def safe_load_image(path):
    try:
        return Image.open(path)
    except Exception:
        return None

def launch_vpn_interface():
    # ensure call runs from main thread when invoked
    try:
        welcome_root.after(0, lambda: VPN_GUI.open_vpn_window(welcome_root))
    except Exception:
        VPN_GUI.open_vpn_window(welcome_root)

def launch_advanced_automation():
    try:
        welcome_root.after(0, lambda: VLAN_Routing.open_automation_window(welcome_root))
    except Exception:
        VLAN_Routing.open_automation_window(welcome_root)

# ---------------------------------------------------------
# دوال مساعدة للواجهة 
# ---------------------------------------------------------
def create_futuristic_canvas(parent):
    """إنشاء خلفية فضائية مع نجوم متحركة"""
    canvas = tk.Canvas(parent, highlightthickness=0, bg=DEEP_SPACE)
    import random
    for _ in range(150):
        x = random.randint(0, 2000)
        y = random.randint(0, 2000)
        brightness = random.randint(100, 255)
        color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
        canvas.create_oval(x-1, y-1, x+1, y+1, fill=color, outline="", tags="star")
    return canvas

def create_futuristic_button(parent, text, command, color=NEON_BLUE):
    """إنشاء زر مستقبلي بتأثير توهج"""
    btn_frame = tk.Frame(parent, bg=DEEP_SPACE)
    button = ctk.CTkButton(
        btn_frame,
        text=text,
        font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        width=340,
        height=50,
        corner_radius=25,
        fg_color="transparent",
        hover_color=color + "33",
        text_color=color,
        border_width=2,
        border_color=color,
        command=command
    )
    button.pack()
    return btn_frame

# ---------------------------------------------------------
# نافذة DNS   
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
                                        font=('Arial', 12, 'bold'), bg="#ffffff", fg="#34495e",
                                        padx=40, pady=40, highlightthickness=2)
    network_config_frame.pack(fill="x", padx=100, pady=20)

    tk.Label(network_config_frame, text="Router Gateway IP:", font=('Arial', 11, 'bold'), bg="#ffffff").grid(row=0, column=0, padx=20, pady=15, sticky="w")
    router_entry = tk.Entry(network_config_frame, width=35, font=('Arial', 12))
    router_entry.grid(row=0, column=1, padx=20, pady=15, sticky="we")

    tk.Label(network_config_frame, text="Primary DNS Server IP:", font=('Arial', 11, 'bold'), bg="#ffffff").grid(row=1, column=0, padx=20, pady=15, sticky="w")
    dns_entry = tk.Entry(network_config_frame, width=35, font=('Arial', 12))
    dns_entry.grid(row=1, column=1, padx=20, pady=15, sticky="we")

    def apply_config():
        router_ip = router_entry.get().strip()
        primary_dns = dns_entry.get().strip()

        if not router_ip or not primary_dns:
            welcome_root.after(0, lambda: messagebox.showwarning("Input Required", "Please enter Router IP and Primary DNS."))
            return

        try:
            ipaddress.ip_address(router_ip)
            ipaddress.ip_address(primary_dns)
        except Exception:
            welcome_root.after(0, lambda: messagebox.showwarning("Invalid Input", "Please enter valid IPv4 addresses."))
            return

        def run_thread():
            try:
                welcome_root.after(0, lambda: apply_button.config(state=tk.DISABLED, text="Applying..."))
            except Exception:
                pass

            try:
                logs = backendFinalVersion.run_dns_config_logic(
                    router_ip, primary_dns,
                    config.SSH_USER, config.SSH_PASS, config.SSH_SECRET
                )

                joined = "\n".join(logs) if isinstance(logs, list) else str(logs)
                lower = joined.lower()
                if any(k in lower for k in ("error", "failure", "failed", "exception")):
                    welcome_root.after(0, lambda: messagebox.showerror("DNS Config", f"Failed to apply DNS config:\n{joined}"))
                else:
                    welcome_root.after(0, lambda: messagebox.showinfo("DNS Config", f"DNS applied successfully.\n{joined}"))

            except Exception as e:
                welcome_root.after(0, lambda: messagebox.showerror("DNS Config", f"Exception: {e}"))

            finally:
                try:
                    welcome_root.after(0, lambda: apply_button.config(state=tk.NORMAL, text="🚀 Apply All Settings"))
                except Exception:
                    pass

        threading.Thread(target=run_thread, daemon=True).start()

    apply_button = tk.Button(network_config_frame, text="🚀 Apply All Settings", command=apply_config,
                            font=('Arial', 12, 'bold'), bg="#2ecc71", fg="white", pady=8)
    apply_button.grid(row=2, column=0, columnspan=2, pady=30)

    tk.Button(dns_win, text="⬅️ Back", font=('Arial', 11, 'bold'), bg="#e74c3c", fg="white",
              command=go_back_to_welcome).place(relx=0.97, rely=0.97, anchor="se")

# ---------------------------------------------------------
# النافذة الرئيسية - التصميم المتجاوب والمتماسك
# ---------------------------------------------------------
if __name__ == "__main__":
    welcome_root = ctk.CTk()
    welcome_root.title("◆ SPACE NETWORK COMMAND CENTER ◆")
    
    # 1. منع تكبير النافذة للحفاظ على ثبات التصميم
    welcome_root.resizable(False, False)
    
    # 2. أبعاد متناسقة للنافذة
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 620
    welcome_root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    welcome_root.configure(fg_color=DEEP_SPACE)
    
    space_canvas = create_futuristic_canvas(welcome_root)
    space_canvas.pack(fill="both", expand=True)
    
    # 3. الإطار الرئيسي
    main_frame = tk.Frame(space_canvas, bg=DEEP_SPACE)
    main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.9)
    
    command_header = tk.Frame(main_frame, bg=SPACE_MID)
    command_header.pack(fill="x", pady=(0, 15))
    
    tk.Frame(command_header, bg=NEON_BLUE, height=2).pack(fill="x")
    
    header_content = tk.Frame(command_header, bg=SPACE_MID)
    header_content.pack(pady=10)
    
    tk.Label(header_content, text="◢ SPACE NETWORK COMMAND CENTER ◣",
             font=("Segoe UI", 22, "bold"), bg=SPACE_MID, fg=NEON_CYAN).pack()
    
    tk.Label(header_content, text="◆ ADVANCED NETWORK CONTROL SYSTEM ◆ v2.6 ◆",
             font=("Courier New", 10), bg=SPACE_MID, fg=SILVER).pack(pady=(5, 0))
    
    tk.Frame(command_header, bg=NEON_BLUE, height=1).pack(fill="x")
    
    content_container = tk.Frame(main_frame, bg=DEEP_SPACE)
    content_container.pack(expand=True)
    
    console_frame = tk.Frame(content_container, bg=DEEP_SPACE)
    console_frame.pack(fill="x")
    
    network_app_root = tk.Tk()
    network_app_root.withdraw()
    app_instance = NetworkApp(network_app_root, back_callback=lambda: [network_app_root.withdraw(), welcome_root.deiconify()])
    
    create_futuristic_button(console_frame, "🛸  DHCP CONFIGURATION MODULE", 
                             lambda: [welcome_root.withdraw(), network_app_root.deiconify()], HOLO_GREEN).pack(pady=8)
    
    create_futuristic_button(console_frame, "🌌  DNS CONFIGURATION MODULE", 
                             open_dns_interface_window, NEON_BLUE).pack(pady=8)
    
    create_futuristic_button(console_frame, "🔮  VPN CONFIGURATION MODULE", 
                             launch_vpn_interface, NEON_PURPLE).pack(pady=8)
    
    create_futuristic_button(console_frame, "⚡  VLAN & OSPF AUTOMATION", 
                             launch_advanced_automation, WARP_CORE).pack(pady=8)
    
    control_panel = tk.Frame(  bg=SPACE_MID, height=75)
    control_panel.pack(fill="x", pady=(15, 0)) 
    control_panel.pack_propagate(False)
    
    # زر الخروج
    exit_button = ctk.CTkButton(
        control_panel,
        text="◆ POWER OFF ◆",
        font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        width=130,
        height=35,
        corner_radius=15,
        fg_color=WARP_CORE,
        hover_color="#c02a50",
        text_color="white",
        command=lambda: sys.exit()
    )
    exit_button.pack(side="right", padx=20, pady=10)
    
    # مؤشرات حالة
    status_text = tk.Label(
        control_panel,
        text="◆ ALL SYSTEMS OPERATIONAL ◆",
        font=("Courier New",13 , "bold"),
        bg=SPACE_MID,
        fg=HOLO_GREEN
    )
    status_text.pack(side="left", padx=20, pady=12)
    
    def blink():
        if status_text.winfo_exists():
            current = status_text.cget("fg")
            next_color = HOLO_GREEN if current == DEEP_SPACE else DEEP_SPACE
            status_text.configure(fg=next_color)
            welcome_root.after(800, blink)
    
    blink()
    welcome_root.mainloop()
