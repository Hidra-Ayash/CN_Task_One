import tkinter as tk
from tkinter import messagebox

# =========================================================
# === GLOBAL DICTIONARIES (THE HANDOFF POINT FOR BACKEND) ===
# =========================================================

# Hold references to all Entry widgets for data retrieval (e.g., POOL_ENTRIES['Pool Name'].get())
POOL_ENTRIES = {}
EXCLUSION_ENTRIES = {}
RESERVATION_ENTRIES = {}

# Hold references to the Listbox widgets for display/deletion
EXCLUSION_LISTBOX = None
RESERVATION_LISTBOX = None

# =========================================================
# === MOCK BACKEND FUNCTIONS (FOR TESTING ONLY) ===
# =========================================================

# This function is the gateway for all button actions
def retrieve_data_and_mock(action_type, entry_dict, listbox=None):
    """Retrieves data, calls the mock backend, and updates the GUI."""
    
    # 1. Gather data from the dictionary references
    data = {k: v.get() for k, v in entry_dict.items()}
    
    # 2. Call the mock backend (replace this with the actual Netmiko call later)
    success, msg = mock_backend_action(action_type, data)
    
    if success:
        # Update listboxes on successful ADD/DELETE
        if action_type in ["Add Exclusion", "Add Reservation"]:
            # Format item for display in the Listbox
            item_key = data.get('start_ip', data.get('Reserved IP'))
            listbox.insert(tk.END, item_key) 
            messagebox.showinfo("MOCK SUCCESS", f"SUCCESS: Item added to list. {action_type} logic executed.")
        elif action_type in ["Delete Exclusion", "Delete Reservation"]:
            try:
                listbox.delete(listbox.curselection())
                messagebox.showinfo("MOCK SUCCESS", f"SUCCESS: Item deleted visually.")
            except:
                messagebox.showerror("MOCK FAIL", "Please select an item to delete first.")
        
        else: # For Pool Apply
            messagebox.showinfo("MOCK SUCCESS", f"SUCCESS: Pool data gathered and sent. {action_type} logic executed.")

    else:
        messagebox.showerror("MOCK FAIL", f"ERROR: {msg}")

# The actual mock logic (for testing data validation)
def mock_backend_action(action_type, data):
    # Example validation: Check if the essential Pool Name is present
    if action_type == "Pool Apply" and not data.get("Pool Name"):
        return False, "Pool Name cannot be blank (Validation Error)."
    
    # All other mocks pass
    return True, "Mock Successful."

# =========================================================
# === PHASE 2, 3, 4: GUI BUILD FUNCTIONS (All functions are now globally accessible) ===
# =========================================================

def build_pool_section(parent_frame):
    """Builds the 5 input fields for Pool Configuration."""
    pool_frame = tk.LabelFrame(parent_frame, text="1. Pool Configuration", padx=10, pady=10)
    
    POOL_LABELS = [
        "Pool Name:", 
        "Network Address:", 
        "Subnet Mask:", 
        "Default Getway:", 
        "Dns server:"
    ]
    
    for i, label_text in enumerate(POOL_LABELS):
        tk.Label(pool_frame, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=2)
        entry = tk.Entry(pool_frame, width=35)
        entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
        
        # CRITICAL HANDOFF: Store the widget reference using a clean key
        key = label_text.replace(':', '').strip()
        POOL_ENTRIES[key] = entry
        
    # Main action button (placeholder command)
    tk.Button(pool_frame, text="APPLY ALL POOL CONFIG", width=45, bg='blue', fg='white', 
              command=lambda: retrieve_data_and_mock("Pool Apply", POOL_ENTRIES)).grid(row=5, column=0, columnspan=2, pady=10)
    
    return pool_frame

def build_exclusion_section(parent_frame): 
    """Builds the Exclusions list management section."""
    global EXCLUSION_LISTBOX
    excl_frame = tk.LabelFrame(parent_frame, text="2. Exclude IPs (IPs to reserve)", padx=10, pady=10)
    
    # --- Input Fields ---
    tk.Label(excl_frame, text="Start Address:").grid(row=0, column=0, sticky='w', padx=5)
    entry_start = tk.Entry(excl_frame, width=15)
    entry_start.grid(row=0, column=1, padx=5, pady=2)
    EXCLUSION_ENTRIES['start_ip'] = entry_start # Store reference
    
    tk.Label(excl_frame, text="End Address:").grid(row=1, column=0, sticky='w', padx=5)
    entry_end = tk.Entry(excl_frame, width=15)
    entry_end.grid(row=1, column=1, padx=5, pady=2)
    EXCLUSION_ENTRIES['end_ip'] = entry_end # Store reference
    
    # --- Action Buttons (Placeholder Commands) ---
    tk.Button(excl_frame, text="زر إضافة استثناء (Add)", 
              command=lambda: retrieve_data_and_mock("Add Exclusion", EXCLUSION_ENTRIES, EXCLUSION_LISTBOX)).grid(row=2, column=0, pady=5, sticky='ew')
              
    tk.Button(excl_frame, text="زر حذف استثناء (Delete)", 
              command=lambda: retrieve_data_and_mock("Delete Exclusion", EXCLUSION_ENTRIES, EXCLUSION_LISTBOX)).grid(row=2, column=1, pady=5, sticky='ew')
              
    # --- Listbox (قائمة استثناءات حالية) ---
    EXCLUSION_LISTBOX = tk.Listbox(excl_frame, height=5, width=35)
    EXCLUSION_LISTBOX.grid(row=3, column=0, columnspan=2, pady=5)
    
    return excl_frame

def build_reservation_section(parent_frame): 
    """Builds the Reservations list management section."""
    global RESERVATION_LISTBOX
    res_frame = tk.LabelFrame(parent_frame, text="3. Static Reservations", padx=10, pady=10)

    RES_LABELS = ["Reserved IP:", "MAC Address:", "Description:"]
    for i, label_text in enumerate(RES_LABELS):
        tk.Label(res_frame, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=2)
        entry = tk.Entry(res_frame, width=25)
        entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
        
        # CRITICAL HANDOFF: Store the widget reference
        RESERVATION_ENTRIES[label_text.replace(':', '').strip()] = entry
    
    # --- Action Buttons (Placeholder Commands) ---
    tk.Button(res_frame, text="زر إضافة حجز (Add)", 
              command=lambda: retrieve_data_and_mock("Add Reservation", RESERVATION_ENTRIES, RESERVATION_LISTBOX)).grid(row=3, column=0, pady=5, sticky='ew')
              
    tk.Button(res_frame, text="زر حذف حجز (Delete)", 
              command=lambda: retrieve_data_and_mock("Delete Reservation", RESERVATION_ENTRIES, RESERVATION_LISTBOX)).grid(row=3, column=1, pady=5, sticky='ew')
    
    # --- Listbox ---
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

    # --- Start building sections here ---
    
    # ------------------ 1. POOL CONFIGURATION FRAME ------------------
    pool_frame = build_pool_section(main_frame)
    pool_frame.grid(row=0, column=0, sticky='ew', columnspan=2, pady=(0, 10))
    
    # ------------------ 2. EXCLUSIONS FRAME ------------------
    excl_frame = build_exclusion_section(main_frame)
    excl_frame.grid(row=1, column=0, sticky='nswe', padx=5, pady=10)

    # ------------------ 3. RESERVATIONS FRAME ------------------
    res_frame = build_reservation_section(main_frame)
    res_frame.grid(row=1, column=1, sticky='nswe', padx=5, pady=10)


# =========================================================
# === MAIN EXECUTION BLOCK ===
# =========================================================
if __name__ == "__main__":
    root = tk.Tk()
    # Replace the placeholder command with the real mock function call for testing
    # root.protocol("WM_DELETE_WINDOW", lambda: root.destroy()) 
    create_dhcp_gui(root)
    root.mainloop()
