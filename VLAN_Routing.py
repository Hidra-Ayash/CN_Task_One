import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import backendFinalVersion

# قائمة تخزين المهام
task_queue = []

def open_automation_window(parent_root):
    parent_root.withdraw()
    window = ctk.CTkToplevel()
    window.title("Network Automation Queue Manager")
    window.geometry("1050x800")

    # --- العنوان الرئيسي ---
    ctk.CTkLabel(window, text="Global Network Task Manager", font=("Arial", 24, "bold")).pack(pady=15)

    # --- تبويبات الإدخال (VLAN vs OSPF) ---
    tabview = ctk.CTkTabview(window, width=950, height=300)
    tabview.pack(pady=10)
    tab_vlan = tabview.add("VLAN Config (Switches)")
    tab_ospf = tabview.add("OSPF Config (Routers)")

    # ---------------------------------------------------------
    # إعدادات تبويب VLAN (تعديل القائمة المنسدلة للواجهات)
    # ---------------------------------------------------------
    # إنشاء قائمة بالواجهات من g0/0 إلى g0/10
    interfaces_list = [f"Gi0/{i}" for i in range(11)]
    
    ctk.CTkLabel(tab_vlan, text="Switch IP:").grid(row=0, column=0, padx=5, pady=5)
    ip_v = ctk.CTkEntry(tab_vlan, placeholder_text="e.g. 192.168.20.1", width=150)
    ip_v.grid(row=1, column=0, padx=10, pady=10)

    ctk.CTkLabel(tab_vlan, text="VLAN ID:").grid(row=0, column=1, padx=5, pady=5)
    vid_v = ctk.CTkEntry(tab_vlan, placeholder_text="e.g. 10", width=80)
    vid_v.grid(row=1, column=1, padx=10)

    ctk.CTkLabel(tab_vlan, text="VLAN Name:").grid(row=0, column=2, padx=5, pady=5)
    vname_v = ctk.CTkEntry(tab_vlan, placeholder_text="e.g. Sales", width=120)
    vname_v.grid(row=1, column=2, padx=10)

    ctk.CTkLabel(tab_vlan, text="Interface:").grid(row=0, column=3, padx=5, pady=5)
    port_v = ctk.CTkOptionMenu(tab_vlan, values=interfaces_list, width=120)
    port_v.set("Gi0/0") # القيمة الافتراضية
    port_v.grid(row=1, column=3, padx=10)

    # ---------------------------------------------------------
    # إعدادات تبويب OSPF (تعديل القائمة المنسدلة للـ Area)
    # ---------------------------------------------------------
    ctk.CTkLabel(tab_ospf, text="Router IP:").grid(row=0, column=0, padx=5, pady=5)
    ip_o = ctk.CTkEntry(tab_ospf, placeholder_text="e.g. 192.168.32.10", width=150)
    ip_o.grid(row=1, column=0, padx=10, pady=10)

    ctk.CTkLabel(tab_ospf, text="Router ID:").grid(row=0, column=1, padx=5, pady=5)
    rid_o = ctk.CTkEntry(tab_ospf, placeholder_text="e.g. 1.1.1.1", width=120)
    rid_o.grid(row=1, column=1, padx=10)

    ctk.CTkLabel(tab_ospf, text="Network IP:").grid(row=0, column=2, padx=5, pady=5)
    net_o = ctk.CTkEntry(tab_ospf, placeholder_text="e.g. 192.168.20.0", width=150)
    net_o.grid(row=1, column=2, padx=10)

    ctk.CTkLabel(tab_ospf, text="OSPF Area:").grid(row=0, column=3, padx=5, pady=5)
    area_o = ctk.CTkOptionMenu(tab_ospf, values=["0", "1", "10", "100"], width=100)
    area_o.set("0")
    area_o.grid(row=1, column=3, padx=10)

    # --- صندوق عرض المهام ---
    ctk.CTkLabel(window, text="Pending Tasks Queue:", font=("Arial", 16)).pack()
    queue_listbox = tk.Listbox(window, width=110, height=12, font=("Courier New", 11), bg="#1a1a1a", fg="#00ff00")
    queue_listbox.pack(pady=10, padx=20)

    # --- الدوال البرمجية ---
    def update_listbox():
        queue_listbox.delete(0, 'end')
        for i, t in enumerate(task_queue):
            if t['type'] == "VLAN":
                info = f"[VLAN] Switch: {t['ip']} | ID: {t['vlan_id']} | Port: {t['port']}"
            else:
                info = f"[OSPF] Router: {t['ip']} | Net: {t['net_ip']} | Area: {t['area']}"
            queue_listbox.insert('end', f"{i}. {info}")

    def add_vlan():
        if not ip_v.get() or not vid_v.get():
            messagebox.showwarning("Input Error", "Please enter IP and VLAN ID")
            return
        task_queue.append({
            "type": "VLAN", "ip": ip_v.get(), "vlan_id": vid_v.get(),
            "vlan_name": vname_v.get(), "port": port_v.get()
        })
        # مسح الحقول النصية فقط وترك القائمة المنسدلة
        ip_v.delete(0, 'end')
        vid_v.delete(0, 'end')
        vname_v.delete(0, 'end')
        update_listbox()

    def add_ospf():
        if not ip_o.get() or not net_o.get():
            messagebox.showwarning("Input Error", "Please enter IP and Network")
            return
        task_queue.append({
            "type": "OSPF", "ip": ip_o.get(), "rid": rid_o.get(),
            "net_ip": net_o.get(), "area": area_o.get()
        })
        ip_o.delete(0, 'end')
        rid_o.delete(0, 'end')
        net_o.delete(0, 'end')
        update_listbox()

    def remove_task():
        try:
            idx = queue_listbox.curselection()[0]
            task_queue.pop(idx)
            update_listbox()
        except: messagebox.showwarning("Selection", "Please select a task to remove")

    def run_all():
        if not task_queue: 
            messagebox.showinfo("Empty", "No tasks to deploy")
            return
        
        results = []
        for t in task_queue:
            try:
                if t['type'] == "VLAN":
                    status = backendFinalVersion.run_vlan_logic(
                        t['ip'], "admin", "cisco123", "cisco", 
                        t['vlan_id'], t['vlan_name'], t['port'], "access"
                    )
                else:
                    status = backendFinalVersion.run_ospf_logic(
                        t['ip'], "admin", "cisco123", "cisco", 
                        "1", t['rid'], t['net_ip'], "0.0.0.255", t['area']
                    )
                results.append(f"✅ Device {t['ip']}: {status}")
            except Exception as e:
                results.append(f"❌ Device {t['ip']}: Error ({str(e)})")
        
        messagebox.showinfo("Deployment Results", "\n".join(results))
        task_queue.clear()
        update_listbox()

    # --- الأزرار ---
    btn_frame = ctk.CTkFrame(window, fg_color="transparent")
    btn_frame.pack(pady=20)

    ctk.CTkButton(tab_vlan, text="Add VLAN Task", command=add_vlan, fg_color="green", width=200).grid(row=2, column=0, columnspan=4, pady=20)
    ctk.CTkButton(tab_ospf, text="Add OSPF Task", command=add_ospf, fg_color="green", width=200).grid(row=2, column=0, columnspan=4, pady=20)
    
    ctk.CTkButton(btn_frame, text="Remove Selected", command=remove_task, fg_color="#c0392b", width=180).grid(row=0, column=0, padx=20)
    ctk.CTkButton(btn_frame, text="DEPLOY TO NETWORK", command=run_all, fg_color="#d35400", width=250, height=45, font=("Arial", 14, "bold")).grid(row=0, column=1, padx=20)
    
    ctk.CTkButton(window, text="Back to Dashboard", command=lambda: [window.destroy(), parent_root.deiconify()], fg_color="gray").pack(pady=10)

    update_listbox()