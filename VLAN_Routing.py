import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import backendFinalVersion
import threading
import config

# إعداد المظهر العام
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# قائمة تخزين المهام
task_queue = []

# ألوان التصميم
COLORS = {
    "primary": "#1565C0",        # أزرق رئيسي
    "primary_hover": "#0D47A1",  # أزرق داكن
    "secondary": "#42A5F5",      # أزرق فاتح
    "success": "#2E7D32",        # أخضر
    "success_hover": "#1B5E20",
    "danger": "#C62828",         # أحمر
    "danger_hover": "#B71C1C",
    "warning": "#EF6C00",        # برتقالي
    "warning_hover": "#E65100",
    "bg_main": "#F5F7FA",        # خلفية رئيسية
    "bg_card": "#FFFFFF",        # خلفية البطاقات
    "bg_input": "#FAFAFA",       # خلفية الحقول
    "text_primary": "#1A237E",   # نص رئيسي
    "text_secondary": "#546E7A", # نص ثانوي
    "border": "#E0E6ED",         # حدود
    "list_bg": "#FAFBFC",        # خلفية القائمة
    "list_text": "#2C3E50",      # نص القائمة
}

def open_automation_window(parent_root=None):
    if parent_root:
        parent_root.withdraw()
    
    # إنشاء النافذة الرئيسية
    window = ctk.CTkToplevel() if parent_root else ctk.CTk()
    window.title("Network Automation Queue Manager")
    window.geometry("1000x760")
    window.configure(fg_color=COLORS["bg_main"])
    
    # تمركز النافذة
    window.update_idletasks()
    x = (window.winfo_screenwidth() - 1000) // 2
    y = (window.winfo_screenheight() - 760) // 2
    window.geometry(f"1000x760+{x}+{y}")

    # ============ الهيدر ============
    header_frame = ctk.CTkFrame(window, fg_color=COLORS["primary"], height=60, corner_radius=0)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    title_label = ctk.CTkLabel(
        header_frame, 
        text="Network Automation Manager",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    )
    title_label.pack(pady=15)
    
    subtitle_label = ctk.CTkLabel(
        header_frame,
        text="VLAN & OSPF Configuration Tool",
        font=("Segoe UI", 15),
        text_color="#B3E5FC"
    )
    subtitle_label.place(relx=0.5, rely=0.90, anchor="center")

    # ============ المحتوى الرئيسي ============
    main_container = ctk.CTkFrame(window, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=20, pady=10)

    # ============ التبويبات ============
    tabview = ctk.CTkTabview(
        main_container, 
        width=950, 
        height=220,
        fg_color=COLORS["bg_card"],
        segmented_button_fg_color=COLORS["bg_input"],
        segmented_button_selected_color=COLORS["primary"],
        segmented_button_selected_hover_color=COLORS["primary_hover"],
        segmented_button_unselected_color=COLORS["bg_input"],
        segmented_button_unselected_hover_color=COLORS["border"],
        text_color="black",
        corner_radius=15
    )
    tabview.pack(pady=(0, 10))
    
    tab_vlan = tabview.add("  VLAN Configuration  ")
    tab_ospf = tabview.add("  OSPF Configuration  ")

    # ============ ستايل الحقول ============
    entry_style = {
        "fg_color": COLORS["bg_input"],
        "border_color": COLORS["border"],
        "border_width": 2,
        "corner_radius": 8,
        "text_color": COLORS["text_primary"],
        "font": ("Segoe UI", 13)
    }
    
    label_style = {
        "font": ("Segoe UI", 12, "bold"),
        "text_color": COLORS["text_secondary"]
    }
    
    dropdown_style = {
        "fg_color": COLORS["bg_input"],
        "button_color": COLORS["primary"],
        "button_hover_color": COLORS["primary_hover"],
        "dropdown_fg_color": COLORS["bg_card"],
        "dropdown_hover_color": COLORS["secondary"],
        "corner_radius": 8,
        "font": ("Segoe UI", 13),
        "text_color": COLORS["text_primary"]
    }

    # ============ تبويب VLAN ============
    vlan_frame = ctk.CTkFrame(tab_vlan, fg_color="transparent")
    vlan_frame.pack(expand=True, pady=10)
    
    # قائمة الواجهات
    interfaces_list_one = [f"Gi0/{i}" for i in range(11)]
    interfaces_list_two=[f"Gi1/{i} " for i in range(11) ]
    interfaces_list = interfaces_list_one + interfaces_list_two
    # الصف الأول - Labels
    ctk.CTkLabel(vlan_frame, text="Switch IP Address", **label_style).grid(row=0, column=0, padx=10, pady=(0, 5))
    ctk.CTkLabel(vlan_frame, text="VLAN ID", **label_style).grid(row=0, column=1, padx=10, pady=(0, 5))
    ctk.CTkLabel(vlan_frame, text="VLAN Name", **label_style).grid(row=0, column=2, padx=10, pady=(0, 5))
    ctk.CTkLabel(vlan_frame, text="Interface", **label_style).grid(row=0, column=3, padx=10, pady=(0, 5))
    ctk.CTkLabel(vlan_frame, text="Mode", **label_style).grid(row=0, column=4, padx=10, pady=(0, 5)) # إضافة عنوان Mode

    # الصف الثاني - Inputs
    ip_v = ctk.CTkEntry(vlan_frame, placeholder_text="192.168.20.1", width=160, height=40, **entry_style)
    ip_v.grid(row=1, column=0, padx=10, pady=10)

    vid_v = ctk.CTkEntry(vlan_frame, placeholder_text="10", width=80, height=40, **entry_style)
    vid_v.grid(row=1, column=1, padx=10, pady=10)

    vname_v = ctk.CTkEntry(vlan_frame, placeholder_text="Sales", width=130, height=40, **entry_style)
    vname_v.grid(row=1, column=2, padx=10, pady=10)

    port_v = ctk.CTkOptionMenu(vlan_frame, values=interfaces_list, width=120, height=40, **dropdown_style)
    port_v.set("Gi0/0")
    port_v.grid(row=1, column=3, padx=10, pady=10)

    # إضافة اختيار الـ Mode
    mode_v = ctk.CTkOptionMenu(vlan_frame, values=["access", "trunk"], width=110, height=40, **dropdown_style)
    mode_v.set("access")
    mode_v.grid(row=1, column=4, padx=10, pady=10)

    # زر إضافة VLAN 
    add_vlan_btn = ctk.CTkButton(
        vlan_frame, 
        text="Add VLAN Task",
        width=220,
        height=38,
        fg_color=COLORS["success"],
        hover_color=COLORS["success_hover"],
        font=("Segoe UI", 13, "bold"),
        corner_radius=10
    )
    add_vlan_btn.grid(row=2, column=0, columnspan=5, pady=15)

 # ============ تبويب OSPF ============
    ospf_frame = ctk.CTkFrame(tab_ospf, fg_color="transparent")
    ospf_frame.pack(expand=True, pady=10)
    
    # الصف الأول - Labels
    ctk.CTkLabel(ospf_frame, text="Router IP", **label_style).grid(row=0, column=0, padx=10, pady=(0, 5))
    ctk.CTkLabel(ospf_frame, text="Process ID", **label_style).grid(row=0, column=1, padx=10, pady=(0, 5))
    ctk.CTkLabel(ospf_frame, text="Router ID", **label_style).grid(row=0, column=2, padx=10, pady=(0, 5))
    ctk.CTkLabel(ospf_frame, text="Network IP", **label_style).grid(row=0, column=3, padx=10, pady=(0, 5))
    ctk.CTkLabel(ospf_frame, text="Wildcard", **label_style).grid(row=0, column=4, padx=10, pady=(0, 5))
    ctk.CTkLabel(ospf_frame, text="Area", **label_style).grid(row=0, column=5, padx=10, pady=(0, 5))

    # الصف الثاني - Inputs
    ip_o = ctk.CTkEntry(ospf_frame, placeholder_text="192.168.32.10", width=140, height=40, **entry_style)
    ip_o.grid(row=1, column=0, padx=8, pady=10)

    pid_o = ctk.CTkEntry(ospf_frame, placeholder_text="1", width=90, height=40, **entry_style) # حقل الـ Process ID الجديد
    pid_o.grid(row=1, column=1, padx=8, pady=10)

    rid_o = ctk.CTkEntry(ospf_frame, placeholder_text="1.1.1.1", width=120, height=40, **entry_style)
    rid_o.grid(row=1, column=2, padx=8, pady=10)

    net_o = ctk.CTkEntry(ospf_frame, placeholder_text="192.168.20.0", width=140, height=40, **entry_style)
    net_o.grid(row=1, column=3, padx=8, pady=10)

    wild_o = ctk.CTkEntry(ospf_frame, placeholder_text="0.0.0.255", width=120, height=40, **entry_style) # حقل الـ Wildcard الجديد
    wild_o.grid(row=1, column=4, padx=8, pady=10)

    area_o = ctk.CTkOptionMenu(ospf_frame, values=["0", "1", "10", "100"], width=90, height=40, **dropdown_style)
    area_o.set("0")
    area_o.grid(row=1, column=5, padx=8, pady=10)

    # زر إضافة OSPF 
    add_ospf_btn = ctk.CTkButton(
        ospf_frame, 
        text="Add OSPF Task",
        width=220,
        height=38,
        fg_color=COLORS["success"],
        hover_color=COLORS["success_hover"],
        font=("Segoe UI", 13, "bold"),
        corner_radius=10
    )
    add_ospf_btn.grid(row=2, column=0, columnspan=6, pady=15)

    # ============ قسم قائمة المهام ============
    queue_section = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], corner_radius=15)
    queue_section.pack(fill="both", expand=True, pady=(0, 10))
    
    queue_header = ctk.CTkFrame(queue_section, fg_color=COLORS["primary"], corner_radius=10, height=38)
    queue_header.pack(fill="x", padx=10, pady=10)
    queue_header.pack_propagate(False)
    
    ctk.CTkLabel(
        queue_header, 
        text="Pending Tasks Queue",
        font=("Segoe UI", 14, "bold"),
        text_color="white"
    ).pack(side="left", padx=15, pady=8)
    
    task_count_label = ctk.CTkLabel(
        queue_header,
        text="0 tasks",
        font=("Segoe UI", 11),
        text_color="#B3E5FC"
    )
    task_count_label.pack(side="right", padx=15, pady=8)

    # قائمة المهام
    list_frame = ctk.CTkFrame(queue_section, fg_color=COLORS["list_bg"], corner_radius=10)
    list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # Scrollbar
    scrollbar = ctk.CTkScrollbar(list_frame)
    scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
    
    queue_listbox = tk.Listbox(
        list_frame, 
        width=105, 
        height=7, 
        font=("Consolas", 11),
        bg=COLORS["list_bg"],
        fg=COLORS["list_text"],
        selectbackground=COLORS["secondary"],
        selectforeground="white",
        borderwidth=0,
        highlightthickness=0,
        activestyle="none",
        yscrollcommand=scrollbar.set
    )
    queue_listbox.pack(fill="both", expand=True, padx=8, pady=8)
    scrollbar.configure(command=queue_listbox.yview)

    # ============ أزرار التحكم ============
    btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    btn_frame.pack(pady=10)

    remove_btn = ctk.CTkButton(
        btn_frame, 
        text="Remove Selected",
        width=180,
        height=45,
        fg_color=COLORS["danger"],
        hover_color=COLORS["danger_hover"],
        font=("Segoe UI", 13, "bold"),
        corner_radius=10
    )
    remove_btn.grid(row=0, column=0, padx=15)

    deploy_btn = ctk.CTkButton(
        btn_frame, 
        text="DEPLOY TO NETWORK",
        width=280,
        height=50,
        fg_color=COLORS["warning"],
        hover_color=COLORS["warning_hover"],
        font=("Segoe UI", 16, "bold"),
        corner_radius=10
    )
    deploy_btn.grid(row=0, column=1, padx=15)

    # زر العودة
    back_btn = ctk.CTkButton(
        btn_frame,
        text="Back to Dashboard",
        width=180,
        height=45,
        fg_color="transparent",
        hover_color=COLORS["border"],
        text_color=COLORS["text_secondary"],
        border_width=2,
        border_color=COLORS["border"],
        font=("Segoe UI", 12,"bold"),
        corner_radius=8,
        command=lambda: [window.destroy(), parent_root.deiconify()] if parent_root else window.destroy()
    )
    back_btn.grid(row=0, column=2, padx=15)

    # ============ الدوال البرمجية ============
    def update_listbox():
        queue_listbox.delete(0, 'end')
        for i, t in enumerate(task_queue):
            if t['type'] == "VLAN":
                info = f"  [VLAN]  Switch: {t['ip']}  |  ID: {t['vlan_id']}  |  Mode: {t['mode']}  |  Port: {t['port']}"
            else:
                info = f"  [OSPF]  Router: {t['ip']}  |  Network: {t['net_ip']}  |  Area: {t['area']}  |  RID: {t['rid']}"
            queue_listbox.insert('end', f" {i+1}. {info}")
            if i % 2 == 0:
                queue_listbox.itemconfig(i, bg="#F8FAFC")
        task_count_label.configure(text=f"{len(task_queue)} task{'s' if len(task_queue) != 1 else ''}")

    def add_vlan():
        if not ip_v.get() or not vid_v.get():
            messagebox.showwarning("Input Required", "Please enter Switch IP and VLAN ID")
            return
        task_queue.append({
            "type": "VLAN", 
            "ip": ip_v.get(), 
            "vlan_id": vid_v.get(),
            "vlan_name": vname_v.get() or "Unnamed", 
            "port": port_v.get(),
            "mode": mode_v.get() 
        })
        ip_v.delete(0, 'end')
        vid_v.delete(0, 'end')
        vname_v.delete(0, 'end')
        update_listbox()
        messagebox.showinfo("Success", "VLAN task added successfully!")
        
    def add_ospf():
        if not ip_o.get() or not net_o.get() or not pid_o.get():
            messagebox.showwarning("Input Required", "Please enter Router IP, Process ID, and Network IP")
            return
        
        task_queue.append({
            "type": "OSPF", 
            "ip": ip_o.get(), 
            "pid": pid_o.get(), 
            "rid": rid_o.get() or "N/A",
            "net_ip": net_o.get(), 
            "wildcard": wild_o.get() or "0.0.0.255", 
            "area": area_o.get()
        })
        ip_o.delete(0, 'end')
        pid_o.delete(0, 'end')
        rid_o.delete(0, 'end')
        net_o.delete(0, 'end')
        wild_o.delete(0, 'end')
        update_listbox()
        messagebox.showinfo("Success", "OSPF task added successfully!")

    def remove_task():
        try:
            idx = queue_listbox.curselection()[0]
            removed = task_queue.pop(idx)
            update_listbox()
            messagebox.showinfo("Removed", f"Task for {removed['ip']} has been removed")
        except IndexError:
            messagebox.showwarning("Selection Required", "Please select a task to remove")


    def run_all():
        if not task_queue:
            messagebox.showinfo("Empty Queue", "No tasks to deploy. Please add tasks first.")
            return

        if not messagebox.askyesno("Confirm Deployment", f"Deploy {len(task_queue)} task(s) to the network?"):
            return

        def worker():
            results_local = []
            for t in list(task_queue):
                try:
                    if t['type'] == "VLAN":
                        res = backendFinalVersion.run_vlan_logic(
                            t['ip'], config.SSH_USER, config.SSH_PASS, config.SSH_SECRET,
                            t['vlan_id'], t['vlan_name'], t['port'], t['mode']
                        )
                        results_local.append(f"VLAN {t['vlan_id']} on {t['ip']}: {res[0] if isinstance(res, list) else res}")
                    else:
                        res = backendFinalVersion.run_ospf_logic(
                            t['ip'], config.SSH_USER, config.SSH_PASS, config.SSH_SECRET,
                            t['pid'], t['rid'], t['net_ip'], t['wildcard'], t['area']
                        )
                        results_local.append(f"OSPF on {t['ip']}: {res}")
                except Exception as e:
                    results_local.append(f"✗ {t['type']} - {t.get('ip','unknown')}: Error - {str(e)}")

            # show results and clear queue on main thread
            window.after(0, lambda: messagebox.showinfo("Deployment Complete", "\n".join(results_local) if results_local else "No results"))
            task_queue.clear()
            window.after(0, update_listbox)

        threading.Thread(target=worker, daemon=True).start()

    # ربط الأزرار بالدوال
    add_vlan_btn.configure(command=add_vlan)
    add_ospf_btn.configure(command=add_ospf)
    remove_btn.configure(command=remove_task)
    deploy_btn.configure(command=run_all)

    update_listbox()
    
    return window

if __name__ == "__main__":
    app = open_automation_window()
    app.mainloop()