import tkinter as tk
from tkinter import messagebox

# =========================================================
# === GLOBAL DICTIONARIES (THE HANDOFF POINT FOR BACKEND) ===
# =========================================================

EXCLUSION_ENTRIES = {}
RESERVATION_ENTRIES = {}

# Hold references to the Listbox widgets for display/deletion
EXCLUSION_LISTBOX = None
RESERVATION_LISTBOX = None

# =========================================================
# === MOCK BACKEND FUNCTIONS (FOR TESTING ONLY) ===
# =========================================================

def retrieve_data_and_mock(action_type, entry_dict, listbox=None):
    """Retrieves data, calls the mock backend, and updates the GUI."""
    data = {k: v.get() for k, v in entry_dict.items()}
    success, msg = mock_backend_action(action_type, data)
    
    if success:
        if action_type in ["Add Exclusion", "Add Reservation"]:
            item_key = data.get('start_ip', data.get('Reserved IP'))
            listbox.insert(tk.END, item_key) 
            messagebox.showinfo("MOCK SUCCESS", f"SUCCESS: Item added to list. {action_type} logic executed.")
        elif action_type in ["Delete Exclusion", "Delete Reservation"]:
            try:
                listbox.delete(listbox.curselection())
                messagebox.showinfo("MOCK SUCCESS", f"SUCCESS: Item deleted visually.")
            except:
                messagebox.showerror("MOCK FAIL", "Please select an item to delete first.")
    else:
        messagebox.showerror("MOCK FAIL", f"ERROR: {msg}")

def mock_backend_action(action_type, data):
    return True, "Mock Successful."

# =========================================================
# === GUI BUILD FUNCTIONS ===
# =========================================================

def build_exclusion_section(parent_frame): 
    """Builds the Exclusions list management section."""
    global EXCLUSION_LISTBOX
    excl_frame = tk.LabelFrame(parent_frame, text="1. Exclude IPs (IPs to reserve)", padx=10, pady=10)
    
    tk.Label(excl_frame, text="Start Address:").grid(row=0, column=0, sticky='w', padx=5)
    entry_start = tk.Entry(excl_frame, width=15)
    entry_start.grid(row=0, column=1, padx=5, pady=2)
    EXCLUSION_ENTRIES['start_ip'] = entry_start
    
    tk.Label(excl_frame, text="End Address:").grid(row=1, column=0, sticky='w', padx=5)
    entry_end = tk.Entry(excl_frame, width=15)
    entry_end.grid(row=1, column=1, padx=5, pady=2)
    EXCLUSION_ENTRIES['end_ip'] = entry_end
    
    tk.Button(excl_frame, text="زر إضافة استثناء (Add)", 
              command=lambda: retrieve_data_and_mock("Add Exclusion", EXCLUSION_ENTRIES, EXCLUSION_LISTBOX)).grid(row=2, column=0, pady=5, sticky='ew')
    tk.Button(excl_frame, text="زر حذف استثناء (Delete)", 
              command=lambda: retrieve_data_and_mock("Delete Exclusion", EXCLUSION_ENTRIES, EXCLUSION_LISTBOX)).grid(row=2, column=1, pady=5, sticky='ew')
    
    EXCLUSION_LISTBOX = tk.Listbox(excl_frame, height=5, width=35)
    EXCLUSION_LISTBOX.grid(row=3, column=0, columnspan=2, pady=5)
    
    return excl_frame

def build_reservation_section(parent_frame): 
    """Builds the Reservations list management section."""
    global RESERVATION_LISTBOX
    res_frame = tk.LabelFrame(parent_frame, text="2. Static Reservations", padx=10, pady=10)

    RES_LABELS = ["Reserved IP:", "MAC Address:", "Description:"]
    for i, label_text in enumerate(RES_LABELS):
        tk.Label(res_frame, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=2)
        entry = tk.Entry(res_frame, width=25)
        entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
        RESERVATION_ENTRIES[label_text.replace(':', '').strip()] = entry
    
    tk.Button(res_frame, text="زر إضافة حجز (Add)", 
              command=lambda: retrieve_data_and_mock("Add Reservation", RESERVATION_ENTRIES, RESERVATION_LISTBOX)).grid(row=3, column=0, pady=5, sticky='ew')
    tk.Button(res_frame, text="زر حذف حجز (Delete)", 
              command=lambda: retrieve_data_and_mock("Delete Reservation", RESERVATION_ENTRIES, RESERVATION_LISTBOX)).grid(row=3, column=1, pady=5, sticky='ew')
    
    RESERVATION_LISTBOX = tk.Listbox(res_frame, height=5, width=40)
    RESERVATION_LISTBOX.grid(row=4, column=0, columnspan=2, pady=5)
    
    return res_frame

# =========================================================

def create_dhcp_gui(root):
    """Initializes the main Tkinter window and frames."""
    global EXCLUSION_LISTBOX, RESERVATION_LISTBOX
    
    root.title("DHCP Configuration - FRONTEND")
    main_frame = tk.Frame(root, padx=15, pady=15)
    main_frame.pack(fill='both', expand=True)

    excl_frame = build_exclusion_section(main_frame)
    excl_frame.grid(row=0, column=0, sticky='nswe', padx=5, pady=10)

    res_frame = build_reservation_section(main_frame)
    res_frame.grid(row=0, column=1, sticky='nswe', padx=5, pady=10)

# =========================================================
# === MAIN EXECUTION BLOCK ===
# =========================================================
if __name__ == "__main__":
    root = tk.Tk()
    create_dhcp_gui(root)
    root.mainloop()
