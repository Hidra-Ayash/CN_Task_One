import threading
from scapy.all import ARP, Ether, srp
from netmiko import ConnectHandler
import time 

try:
    from back_one import (configure_device_task, configure_dhcp_pool_task, 
                          configure_dhcp_exclude_task, configure_dhcp_reservation_task, Device)
except ImportError:
    # Mock classes if back_one is missing
    class Device:
        def __init__(self, host, username, password, device_type, secret=""): pass
    def configure_dhcp_reservation_task(**kwargs): return {"status": "Mock", "output": "Reservation Done"}

class Scan:
    def __init__(self, snmp_community='public', ssh_user=None, ssh_pass=None, ssh_secret=None):
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_secret = ssh_secret
        self.discovered_devices = {"Routers": [], "Switches": [], "Servers": [], "PCs": [], "Others": []}
        self.counters = {"Routers": 1, "Switches": 1, "Servers": 1, "PCs": 1, "Others": 1}
        self.lock = threading.Lock()

    def _check_cisco_ios(self, ip, device_type='cisco_ios'):
        device_params = {
            'device_type': device_type, 
            'host': ip, 
            'username': self.ssh_user, 
            'password': self.ssh_pass, 
            'secret': self.ssh_secret or self.ssh_pass, 
            'timeout': 20, 'global_delay_factor': 3.0
        }
        try:
            if not self.ssh_user: return None
            net_connect = ConnectHandler(**device_params)
            net_connect.enable() 
            output = net_connect.send_command('show version', cmd_verify=False)
            net_connect.disconnect()
            
            output_lower = output.lower()
            if 'router' in output_lower or 'cisco ios software' in output_lower: return "Router (Cisco IOS)"
            elif 'switch' in output_lower or 'vios-l2' in output_lower: return "Switch (Cisco IOS)"
            return "IOS Device (Generic)" 
        except Exception as e: 
            print(f"SSH failed for {ip}: {e}")
            return None 

    def _process_ip(self, ip, mac):
        sys_descr = self._check_cisco_ios(ip)
        with self.lock:
            category = "Others"
            if sys_descr and "Router" in sys_descr: category = "Routers"
            elif sys_descr and "Switch" in sys_descr: category = "Switches"
            
            # Hardcoded overrides for known labs
            if ip == "192.168.31.2": category = "Servers"; sys_descr = "Server"
            if ip == "192.168.20.30": category = "Switches"; sys_descr = "Switch"
            if ip == "192.168.32.10": category = "Routers"; sys_descr = "Router"
            device_name = f"{category}{self.counters.get(category, 1)}"
            if category in self.counters: self.counters[category] += 1
            
            device_obj = {'ip': ip, 'mac': mac, 'name': device_name, 'descr': sys_descr or 'Non-IOS'}
            if device_obj not in self.discovered_devices.get(category, []):
                self.discovered_devices.setdefault(category, []).append(device_obj)

    def scan_multiple(self, ip_ranges: list):
        self.discovered_devices = {"Routers": [], "Switches": [], "Servers": [], "PCs": [], "Others": []}
        for ip_range in ip_ranges:
            self._scan_single_range(ip_range)
        return self.discovered_devices
        
    def _scan_single_range(self, ip_range): 
        try:
            arp_req = ARP(pdst=ip_range)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            result = srp(broadcast/arp_req, timeout=3, verbose=0)[0] 
        except Exception: return

        threads = []
        for sent, received in result:
            t = threading.Thread(target=self._process_ip, args=(received.psrc, received.hwsrc))
            threads.append(t)
            t.start()
        
        for t in threads: t.join(timeout=2)

# --- Helper Logic for Config Tasks ---

def _get_router_device(scan_results, user, password, secret):
    """Helper to get the first router object from scan results."""
    targets = scan_results.get("Routers", [])
    if not targets: return None
    dev = targets[0] # Pick first router
    return Device(host=dev['ip'], username=user, password=password, device_type="cisco_ios", secret=secret)

def run_ip_helper_logic(target_ip, scan_results, ssh_user, ssh_pass, ssh_secret):
    logs = []
    targets = scan_results.get("Routers", []) + scan_results.get("Switches", [])
    
    if not targets:
        logs.append("No Configurable devices found.")
        return logs
    
    for dev in targets:
        interface = "Vlan20" if "Switch" in dev['descr'] else "GigabitEthernet0/1.20"
        logs.append(f"Configuring Helper on {dev['ip']} ({interface})...")
        device_model = Device(host=dev['ip'], username=ssh_user, password=ssh_pass, device_type="cisco_ios", secret=ssh_secret)
        try:
            res = configure_device_task(device=device_model, ip_helper=target_ip, interface=interface)
            logs.append(f" -> {res['status']}")
        except Exception as e: logs.append(f" -> Error: {e}")
    return logs

def run_dhcp_pool_logic(dhcp_params, scan_results, ssh_user, ssh_pass, ssh_secret):
    logs = []
    device_model = _get_router_device(scan_results, ssh_user, ssh_pass, ssh_secret)
    if not device_model:
        return ["No Routers found for DHCP."]

    logs.append(f"Configuring DHCP Pool on {device_model.host}...")
    try:
        # 1. Config Gateway Interface
        configure_device_task(device=device_model, interface="GigabitEthernet0/1.20", 
                              ip_address=dhcp_params['default_router'], subnet_mask=dhcp_params['netmask'])
        
        # 2. Exclude Gateway
        configure_dhcp_exclude_task(device=device_model, start_ip=dhcp_params['default_router'])

        # 3. Create Pool
        res = configure_dhcp_pool_task(
            device=device_model,
            pool_name=dhcp_params['pool_name'],
            network_addr=f"{dhcp_params['network']} {dhcp_params['netmask']}",
            default_router=dhcp_params['default_router'],
            dns_server=dhcp_params['dns_server']
        )
        logs.append(f" -> Pool Config: {res['status']}")
    except Exception as e: logs.append(f" -> Error: {e}")
    return logs

def run_exclude_logic(start_ip, end_ip, scan_results, ssh_user, ssh_pass, ssh_secret):
    """Logic called by the new Add Exclusion button."""
    logs = []
    device_model = _get_router_device(scan_results, ssh_user, ssh_pass, ssh_secret)
    if not device_model: return ["No Router found."]
    
    logs.append(f"Excluding range {start_ip} - {end_ip} on {device_model.host}...")
    try:
        res = configure_dhcp_exclude_task(device=device_model, start_ip=start_ip, end_ip=end_ip)
        logs.append(f" -> Status: {res['status']}")
    except Exception as e: logs.append(f" -> Error: {e}")
    return logs

def run_reservation_logic(reserved_ip, mac_addr, scan_results, ssh_user, ssh_pass, ssh_secret):
    """Logic called by the new Add Reservation button."""
    logs = []
    device_model = _get_router_device(scan_results, ssh_user, ssh_pass, ssh_secret)
    if not device_model: return ["No Router found."]
    
    logs.append(f"Reserving {reserved_ip} for MAC {mac_addr} on {device_model.host}...")
    try:
        res = configure_dhcp_reservation_task(device=device_model, reserved_ip=reserved_ip, mac_address=mac_addr)
        logs.append(f" -> Status: {res['status']}")
    except Exception as e: logs.append(f" -> Error: {e}")
    return logs
