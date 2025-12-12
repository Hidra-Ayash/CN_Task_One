import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from Main_GUI import NetworkApp 
from tkinter import ttk

ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue") 

# الدالة التي تنشئ وتفتح نافذة DNS
def open_dns_interface_window():
    
    welcome_root.withdraw()

    # إنشاء النافذة الفرعية (TopLevel)
    dns_win = tk.Toplevel(welcome_root)
    dns_win.minsize(800, 600)
    dns_win.geometry("900x600")
    dns_win.title("DNS Configuration Tool")
    dns_win.configure(bg="#f0f8ff")
    # dns_win.transient(welcome_root) # يمكن إبقاء النافذة ثابتة فوق الرئيسية

    def go_back_to_welcome():
        dns_win.destroy()
        welcome_root.deiconify() 

    main_frame = tk.Frame(dns_win, bg="#f0f8ff", padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    title_label = tk.Label(
        main_frame, 
        text="DNS Configuration", 
        font=('Arial', 18, 'bold'), 
        bg="#f0f8ff", 
        fg="#2c5e50"
    )
    title_label.pack(pady=(0, 30))

    # إطار لخانة IP Router
    router_frame = tk.LabelFrame(
        main_frame, 
        text=" Router Configuration ", 
        font=('Arial', 12, 'bold'),
        bg="#f0f8ff",
        fg="#2980b9",
        relief="groove",
        borderwidth=2,
        padx=15,
        pady=15
    )
    router_frame.pack(fill="x", padx=20, pady=10)

    # عناصر Router
    router_label = tk.Label(
        router_frame, 
        text="Router IP Address:", 
        font=('Arial', 11), 
        bg="#f0f8ff"
    )
    router_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    router_entry = tk.Entry(
        router_frame, 
        width=25, 
        font=('Arial', 11),
        relief="solid",
        borderwidth=1
    )
    router_entry.grid(row=0, column=1, padx=10, pady=10)
    router_entry.focus()

    router_button = tk.Button(
        router_frame, 
        text="Apply Router IP", 
        font=('Arial', 11, 'bold'),
        bg="#3498db",
        fg="white",
        relief="raised",
        padx=15,
        pady=5
    )
    router_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")

    # إطار لخانة DNS
    dns_frame = tk.LabelFrame(
        main_frame, 
        text=" DNS Configuration ", 
        font=('Arial', 12, 'bold'),
        bg="#f0f8ff",
        fg="#2980b9",
        relief="groove",
        borderwidth=2,
        padx=15,
        pady=15
    )
    dns_frame.pack(fill="x", padx=20, pady=20)

    # عناصر DNS
    dns_label = tk.Label(
        dns_frame, 
        text="DNS Server IP:", 
        font=('Arial', 11), 
        bg="#f0f8ff"
    )
    dns_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    dns_entry = tk.Entry(
        dns_frame, 
        width=25, 
        font=('Arial', 11),
        relief="solid",
        borderwidth=1
    )
    dns_entry.grid(row=0, column=1, padx=10, pady=10)

    dns_button = tk.Button(
        dns_frame, 
        text="Apply DNS IP", 
        font=('Arial', 11, 'bold'),
        bg="#3498db",
        fg="white",
        relief="raised",
        padx=15,
        pady=5
    )
    dns_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")

    # ضبط توسيط جميع العناصر
    for frame in [router_frame, dns_frame]:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    # زر العودة (back) في الزاوية السفلية اليمنى
    close_button = tk.Button(
        dns_win,
        text="back",
        font=('Arial', 10, 'bold'), 
        bg="#1e88e5", 
        fg="white",
        relief="raised",
        width=8, 
        height=1,
        command=go_back_to_welcome
    )
    close_button.place(relx=0.98, rely=0.98, anchor="se")
    
    # تمت إزالة dns_win.mainloop() هنا 


if __name__ == "__main__":
    
    welcome_root = ctk.CTk()
    welcome_root.title("Computer Network Management")
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 450
    welcome_root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") 
    welcome_root.resizable(False, False) 
    
    welcome_root.configure(fg_color="#f0f0f0") 
    
    def show_welcome_window():
        welcome_root.deiconify()

    root = tk.Tk()
    app_instance = NetworkApp(root, back_callback=show_welcome_window) 
    app_instance.root.withdraw()
    
    def open_network_scan_interface(root_app_instance):
        welcome_root.withdraw() 
        root_app_instance.root.deiconify() 

    def exit_app(root_app_instance):
        root_app_instance.root.destroy()
        welcome_root.destroy()
    
    header_label = ctk.CTkLabel(
        master=welcome_root, 
        text="Computer Network Management", 
        font=ctk.CTkFont(family="Arial", size=26, weight="bold"), 
        text_color="#1F6AA5", 
        fg_color="transparent" 
    )
    header_label.pack(pady=(80, 50)) 

    button_frame = ctk.CTkFrame(welcome_root, fg_color="white", corner_radius=10)
    button_frame.pack(pady=30, padx=50, fill="x")

    btn_dhcp = ctk.CTkButton(
        master=button_frame, 
        text="DHCP", 
        font=ctk.CTkFont(family="Arial", size=16), 
        width=300, 
        height=50,
        corner_radius=15, 
        fg_color="#006400", 
        hover_color="#3CB371", 
        command=lambda: open_network_scan_interface(app_instance) 
    )
    btn_dhcp.pack(pady=(20, 10), padx=20) 
    
    btn_dns = ctk.CTkButton(
        master=button_frame, 
        text="DNS", 
        font=ctk.CTkFont(family="Arial", size=16), 
        width=300, 
        height=50,
        corner_radius=15, 
        fg_color="#FFD700", 
        hover_color="#FFBF00", 
        text_color="black",
        command=open_dns_interface_window 
    )
    btn_dns.pack(pady=(10, 20), padx=20) 
    
    btn_exit = ctk.CTkButton(
        master=welcome_root, 
        text="Exit", 
        font=ctk.CTkFont(family="Arial", size=12, weight="bold"), 
        width=80, 
        height=30,
        corner_radius=10,
        fg_color="#CC0000", 
        hover_color="#B22222",
        command=lambda: exit_app(app_instance)
    )
    btn_exit.place(relx=0.95, rely=0.95, anchor="se")

    welcome_root.mainloop()