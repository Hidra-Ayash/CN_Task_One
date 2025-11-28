import threading
from scapy.all import ARP, Ether, srp
from netmiko import ConnectHandler
import time 

# تأكد من أن ملف back_one.py موجود في نفس المجلد
try:
    from back_one import (configure_device_task, configure_dhcp_pool_task, 
                          configure_dhcp_exclude_task, configure_dhcp_reservation_task, Device)
except ImportError:
    # Mock classes if back_one is missing
    class Device:
        def __init__(self, host, username, password, device_type, secret=""): pass
    def configure_dhcp_reservation_task(**kwargs): return {"status": "Mock", "output": "Reservation Done"}
    def configure_device_task(**kwargs): return {"status": "Mock", "output": "Config Done"}
    def configure_dhcp_pool_task(**kwargs): return {"status": "Mock", "output": "Pool Done"}
    def configure_dhcp_exclude_task(**kwargs): return {"status": "Mock", "output": "Exclude Done"}


# ==========================================================
# HELPER: GUESS DEVICE TYPE FROM MAC (OUI)
# ==========================================================
def _guess_device_type(mac_addr):
    """
    تخمين نوع الجهاز أو البائع من MAC OUI 
    (تم تبسيط القائمة للتركيز على بيئات GNS3/الافتراضية).
    """
    if not mac_addr:
        return "Unknown Host"
    
    # تحويل MAC إلى صيغة موحدة
    mac_prefix = mac_addr.replace(':', '').replace('-', '').upper()[:6]

    # قائمة مبسطة للـ OUI
    if mac_prefix in ["000C29", "005056"]:
        return "VMware Virtual Machine"
    elif mac_prefix in ["00059A", "525400", "000000"]:
        # 52:54:00 هو QEMU/KVM الشائع في GNS3
        return "QEMU/GNS3 Virtual Device"
    elif mac_prefix.startswith(("A4", "B8", "E0", "00")):
        return "Generic PC/Mobile Device"
    else:
        return "Unknown Host"

# ==========================================================
# SCAN CLASS
# ==========================================================
class Scan:
    def __init__(self, snmp_community='public', ssh_user=None, ssh_pass=None, ssh_secret=None):
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_secret = ssh_secret
        self.discovered_devices = {"Routers": [], "Switches": [], "Servers": [], "PCs": [], "Others": []}
        self.counters = {"Routers": 1, "Switches": 1, "Servers": 1, "PCs": 1, "Others": 1}
        self.lock = threading.Lock()

    def _check_cisco_ios(self, ip, mac, device_type='cisco_ios'):
        device_params = {
            'device_type': device_type, 
            'host': ip, 
            'username': self.ssh_user, 
            'password': self.ssh_pass, 
            'secret': self.ssh_secret or self.ssh_pass, 
            'timeout': 20, 'global_delay_factor': 3.0
        }
        try:
            if not self.ssh_user: raise Exception("SSH user not configured")
            net_connect = ConnectHandler(**device_params)
            net_connect.enable() 
            output = net_connect.send_command('show version', cmd_verify=False)
            net_connect.disconnect()
            
            output_lower = output.lower()
            if 'router' in output_lower or 'cisco ios software' in output_lower: return "Router (Cisco IOS)"
            elif 'switch' in output_lower or 'vios-l2' in output_lower: return "Switch (Cisco IOS)"
            return "IOS Device (Generic)" 
        except Exception as e: 
            # فشل SSH، نعود إلى التخمين لتحديد الوصف الجديد
            print(f"SSH failed for {ip}: {e}. Attempting MAC guess.")
            return _guess_device_type(mac) 

    # ==========================================================
    # MODIFIED: _process_ip (منطق التصنيف المحدث)
    # ==========================================================
    def _process_ip(self, ip, mac):
        # 1. تحقق من IOS/Non-IOS والحصول على وصف
        sys_descr = self._check_cisco_ios(ip, mac)
        
        with self.lock:
            category = "Others" # التصنيف الافتراضي
            
            # 2. تعيين الفئة بناءً على نتيجة SSH/Netmiko (أجهزة IOS)
            if sys_descr and "Router" in sys_descr: 
                category = "Routers"
            elif sys_descr and "Switch" in sys_descr: 
                category = "Switches"
            
            # 3. المنطق الجديد: التحقق من الأجهزة الافتراضية
            elif sys_descr and ("Virtual Machine" in sys_descr or "Virtual Device" in sys_descr ):
                # *** التعديل المطلوب: فحص نطاق IP لضمان أنه جهاز حصل على IP من DHCP (192.168.20.X) ***
                if ip.startswith("192.168.20."):
                    try:
                        ip_octets = ip.split('.')
                        # نعتبر الأجهزة التي IPها يبدأ من 2 فما فوق (لتجنب 192.168.20.1 البوابة)
                        if len(ip_octets) == 4 and int(ip_octets[3]) >= 2 and int(ip_octets[3]) <= 254:
                            category = "PCs" # تصنيف الأجهزة الافتراضية كحواسيب عميلة ضمن نطاق DHCP
                    except ValueError:
                        # في حال فشل التحويل إلى رقم يبقى Others
                        pass
                # else: إذا كان جهاز افتراضي لكن ليس في نطاق 192.168.20.x، يبقى "Others" (التصنيف الافتراضي)
            
            # 4. تجاوز العناوين الثابتة للمختبرات المعروفة (GNS3)
            # هذه العناوين الثابتة تتجاوز منطق DHCP أعلاه
            if ip == "192.168.31.2": 
                category = "Servers"
                sys_descr = sys_descr if "Virtual" in sys_descr else "Dedicated Server"
            if ip == "192.168.20.30": category = "Switches"; sys_descr = "Switch"
            if ip == "192.168.32.10": category = "Routers"; sys_descr = "Router"


            device_name = f"{category}{self.counters.get(category, 1)}"
            if category in self.counters: self.counters[category] += 1
            
            # الوصف النهائي: استخدم الوصف المكتشف (IOS أو MAC Guess)
            final_descr = sys_descr 

            device_obj = {'ip': ip, 'mac': mac, 'name': device_name, 'descr': final_descr or 'Unknown'}
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

# ==========================================================
# CONFIGURATION AND HELPER LOGIC (DEPENDS ON back_one.py)
# ==========================================================

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