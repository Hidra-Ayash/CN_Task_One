import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from PIL import Image, ImageTk 
import sys

# افتراض وجود الملفات الأخرى (لم يتم تعديلها بناءً على طلبك)
try:
    import backendFinalVersion
    from Main_GUI import NetworkApp
except ImportError:
    # إضافة محاكاة (Mock) مؤقتة في حالة عدم وجود الملفات لضمان التشغيل
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
    """تحميل الصورة بأمان مع معالجة خطأ عدم العثور على الملف."""
    try:
        # ملاحظة: إذا كنت تستخدم صيغة صورة غير JPG (مثل PNG) تأكد من أن PIL يدعمها في بيئتك.
        return Image.open(path)
    except FileNotFoundError:
        print(f"Warning: Background image '{path}' not found. Using solid background.")
        return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# ---------------------------------------------------------
# DNS Interface Window (لم يتم تعديلها بناءً على طلبك)
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

    # Frame
    main_frame = tk.Frame(dns_win, bg="#f0f8ff", padx=30, pady=30)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = tk.Label(
        main_frame,
        text="🌐 Unified Network Settings (DNS)",
        font=('Segoe UI', 24, 'bold'),
        bg="#f0f8ff",
        fg="#1e88e5"
    )
    title_label.pack(pady=(20, 40))

    # Config Frame
    network_config_frame = tk.LabelFrame(
        main_frame,
        text=" ⚙️ Core Network Configuration ",
        font=('Arial', 14, 'bold'),
        bg="#ffffff",
        fg="#34495e",
        relief="flat",
        borderwidth=0,
        highlightbackground="#bdc3c7",
        highlightthickness=2,
        padx=40,
        pady=40
    )
    network_config_frame.pack(fill="x", padx=100, pady=20)

    # Router IP
    router_label = tk.Label(
        network_config_frame,
        text="Router Gateway IP:",
        font=('Arial', 12, 'bold'),
        bg="#ffffff",
        fg="#2c3e50"
    )
    router_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

    router_entry = tk.Entry(
        network_config_frame,
        width=35,
        font=('Arial', 12),
        relief="groove",
        borderwidth=2
    )
    router_entry.grid(row=0, column=1, padx=20, pady=15, ipady=3, sticky="we")
    router_entry.focus()

    # DNS IP
    dns_label = tk.Label(
        network_config_frame,
        text="Primary DNS Server IP:",
        font=('Arial', 12, 'bold'),
        bg="#ffffff",
        fg="#2c3e50"
    )
    dns_label.grid(row=1, column=0, padx=20, pady=15, sticky="w")

    dns_entry = tk.Entry(
        network_config_frame,
        width=35,
        font=('Arial', 12),
        relief="groove",
        borderwidth=2
    )
    dns_entry.grid(row=1, column=1, padx=20, pady=15, ipady=3, sticky="we")

    # Threaded function
    def run_thread(router_ip, primary_dns):
        # استخدام config بدلاً من ctk.configure لأننا في نافذة tk.Toplevel
        apply_button.config(state=tk.DISABLED, text="Applying...")
        try:
            logs = backendFinalVersion.run_dns_config_logic(
                router_ip, primary_dns,"admin","cisco123","cisco"
            )
            final_msg = "\n".join(logs)
            messagebox.showinfo("Configuration Result", final_msg)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            apply_button.config(state=tk.NORMAL, text="🚀 Apply All Settings")

    # Apply button handler
    def apply_config():
        router_ip = router_entry.get()
        primary_dns = dns_entry.get()
        threading.Thread(target=run_thread, args=(router_ip, primary_dns)).start()

    # Apply Button
    apply_button = tk.Button(
        network_config_frame,
        text="🚀 Apply All Settings",
        command=apply_config,
        font=('Arial', 13, 'bold'),
        bg="#2ecc71",
        fg="white",
        relief="raised",
        activebackground="#27ae60",
        padx=20,
        pady=8
    )
    apply_button.grid(row=2, column=0, columnspan=2, padx=20, pady=(30, 10), sticky="s")

    network_config_frame.grid_columnconfigure(0, weight=1)
    network_config_frame.grid_columnconfigure(1, weight=1)

    # Back Button
    close_button = tk.Button(
        dns_win,
        text="⬅️ Back",
        font=('Arial', 11, 'bold'),
        bg="#e74c3c",
        fg="white",
        relief="flat",
        activebackground="#c0392b",
        width=10,
        height=1,
        command=go_back_to_welcome
    )
    close_button.place(relx=0.97, rely=0.97, anchor="se")

# ---------------------------------------------------------
# MAIN EXECUTION BLOCK (خلفية صورة متجاوبة)
# ---------------------------------------------------------
# تعريف المتغيرات عالمياً قبل الدالة resize_bg_main
bg_image = None
canvas_main = None
bg_photo_main = None
canvas_bg_main = None
header_window = None
button_frame_window = None
btn_exit = None # يجب تعريف هذا الزر أيضاً

def resize_bg_main(event=None):
    # **********************************************
    # استخدام 'global' لجميع المتغيرات المشتركة
    # **********************************************
    global bg_photo_main, bg_image, canvas_main, canvas_bg_main
    global header_window, button_frame_window, welcome_root, WINDOW_WIDTH, WINDOW_HEIGHT
    
    # التحقق من أن الحدث يأتي من النافذة الرئيسية
    if event is not None and event.widget != welcome_root:
        return 
        
    new_width = welcome_root.winfo_width() if welcome_root.winfo_width() > 0 else WINDOW_WIDTH
    new_height = welcome_root.winfo_height() if welcome_root.winfo_height() > 0 else WINDOW_HEIGHT
        
    if bg_image:
        try:
            resized = bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            bg_photo_main = ImageTk.PhotoImage(resized)
            canvas_main.itemconfig(canvas_bg_main, image=bg_photo_main)
        except Exception as e:
            pass
    
    # تحديث مواقع العناصر فوق الخلفية
    
    # تحديث مكان العنوان
    if header_window is not None:
        canvas_main.coords(header_window, new_width // 2, int(new_height * 0.2))
    
    # تحديث مكان إطار الأزرار
    if button_frame_window is not None:
        canvas_main.coords(button_frame_window, new_width // 2, int(new_height * 0.55))
    
    # تحديث مكان زر الخروج (يستخدم place مباشرة)
    if btn_exit is not None:
        btn_exit.place(relx=0.97, rely=0.97, anchor="se")


if __name__ == "__main__":
    welcome_root = ctk.CTk()
    welcome_root.title("Computer Network Management")
    WINDOW_WIDTH = 650
    WINDOW_HEIGHT = 500
    welcome_root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    welcome_root.resizable(True, True)
    
    # تحميل صورة الخلفية
    bg_image = safe_load_image("background_main.jpg")

    # **********************************************
    # تطبيق الخلفية المتجاوبة (التصحيح الرئيسي هنا)
    # **********************************************
    
    # إذا كانت الصورة موجودة، نستخدم لوناً صالحاً (مثل الأبيض #FFFFFF).
    # إذا لم تكن الصورة موجودة، نستخدم اللون الاحتياطي #f5f7fa.
    background_color = "#FFFFFF" if bg_image else "#f5f7fa"
    canvas_main = ctk.CTkCanvas(welcome_root, highlightthickness=0, bg=background_color)
    canvas_main.pack(fill="both", expand=True)
    
    if bg_image:
        initial_width, initial_height = WINDOW_WIDTH, WINDOW_HEIGHT
        resized_img_main = bg_image.resize((initial_width, initial_height), Image.Resampling.LANCZOS)
        bg_photo_main = ImageTk.PhotoImage(resized_img_main)
        canvas_bg_main = canvas_main.create_image(0, 0, image=bg_photo_main, anchor="nw")

    welcome_root.bind("<Configure>", resize_bg_main)

    network_app_root = tk.Tk()
    network_app_root.withdraw()

    def back_to_welcome_window():
        network_app_root.withdraw()
        welcome_root.deiconify()

    app_instance = NetworkApp(network_app_root, back_callback=back_to_welcome_window)

    def open_network_scan_interface(root_app_instance):
        welcome_root.withdraw()
        network_app_root.deiconify()

    def exit_app(root_app_instance):
        try:
            network_app_root.destroy()
        except Exception:
            pass
        welcome_root.destroy()
    # ----------------------------------------------

    header_label = ctk.CTkLabel(
        master=welcome_root,
        text="Welcome To The Network Management Program",
        font=ctk.CTkFont(family="Arial", size=25, weight="bold"),
        text_color="black" if bg_image else "#1F6AA5",
        fg_color="transparent"
    )
    # وضع العنوان فوق Canvas باستخدام create_window
    header_window = canvas_main.create_window(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.2), window=header_label)

    # إطار الأزرار (شفاف ليظهر الخلفية)
    # ملاحظة: تم تغيير fg_color لـ CTkFrame ليكون شفافاً ليظهر الصورة
    button_frame = ctk.CTkFrame(
        welcome_root, 
        fg_color="transparent", 
        corner_radius=18,
        border_color="#1F6AA5",
        border_width=3
    )
    # وضع الإطار فوق Canvas باستخدام create_window
    button_frame_window = canvas_main.create_window(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT * 0.55), window=button_frame)
    
    button_frame.grid_columnconfigure(0, weight=1)

    # زر DHCP
    btn_dhcp = ctk.CTkButton(
        master=button_frame,
        text="DHCP Configuration",
        font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
        width=350,
        height=55,
        corner_radius=12,
        fg_color="#0CC43A",
        hover_color="#09a632",
        command=lambda: open_network_scan_interface(app_instance)
    )
    btn_dhcp.pack(pady=(30, 15), padx=30)

    # زر DNS
    btn_dns = ctk.CTkButton(
        master=button_frame,
        text="DNS Configuration",
        font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
        width=350,
        height=55,
        corner_radius=12,
        fg_color="#3498db",
        hover_color="#2980b9",
        text_color="white",
        command=open_dns_interface_window
    )
    btn_dns.pack(pady=(15, 30), padx=30)

    # زر الخروج
    btn_exit = ctk.CTkButton(
        master=welcome_root,
        text="Exit",
        font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
        width=100,
        height=35,
        corner_radius=10,
        fg_color="#CC0000",
        hover_color="#B22222",
        command=lambda: exit_app(app_instance)
    )
    btn_exit.place(relx=0.97, rely=0.97, anchor="se") 
    
    # الاستدعاء الأولي لتعيين الخلفية والمواقع بعد إنشاء جميع العناصر
    welcome_root.update()
    resize_bg_main(None)

    welcome_root.mainloop()