import threading
import re
from scapy.all import ARP, Ether, srp
from netmiko import ConnectHandler
import time 

try:
    from back_one import configure_device_task, configure_dhcp_pool_task,configure_dhcp_exclude_task, Device
except ImportError:
    # الكلاس الوهمي ليعمل في بيئة بدون back_one.py
    class Device:
        def __init__(self, host, username, password, device_type, secret=""):
            self.host = host; self.username = username; self.password = password; self.device_type = device_type; self.secret = secret
    def configure_device_task(**kwargs): return {"status": "Mock Success", "output": "Configured"}
    def configure_dhcp_pool_task(**kwargs): return {"status": "Mock Success", "output": "DHCP Pool Configured"}
    def configure_dhcp_exclude_task(**kwargs): return {"status": "Mock Success", "output": "DHCP Exclude Configured"}


# تم حذف GATEWAY_INTERFACE واستبدالها بواجهات محددة حسب الوظيفة (G0/1 للـ LAN)

class Scan:
    def __init__(self, snmp_community='public', ssh_user=None, ssh_pass=None, ssh_secret=None):
        self.snmp_community = snmp_community
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_secret = ssh_secret
        self.discovered_devices = {"Routers": [], "Switches": [], "Servers": [], "PCs": [], "Others": []}
        self.counters = {"Routers": 1, "Switches": 1, "Servers": 1, "PCs": 1, "Others": 1}
        self.lock = threading.Lock()

    def _check_cisco_ios(self, ip, device_type='cisco_ios'):
        """
        يحاول الاتصال بـ SSH/Netmiko لتحديد ما إذا كان الجهاز هو راوتر/سويتش
        قادر على استقبال تكوينات Cisco IOS.
        **تم تعديل منطق التصنيف هنا**
        """
        device_params = {
            'device_type': device_type, 
            'host': ip, 
            'username': self.ssh_user, 
            'password': self.ssh_pass, 
            'secret': self.ssh_secret or self.ssh_pass, 
            'timeout': 20,  
            'global_delay_factor': 3.0, 
            'fast_cli': False
        }
        try:
            if not self.ssh_user or not self.ssh_pass:
                print(f"Skipping SSH check for {ip}: SSH credentials are not set.")
                return None
                
            net_connect = ConnectHandler(**device_params)
            net_connect.enable() 

            # **التعديل:** استخدام أمر 'show version' الكامل للحصول على أفضل دقة في التصنيف
            output = net_connect.send_command('show version', cmd_verify=False)
            net_connect.disconnect()
            
            # --- منطق تصنيف الأجهزة المُعدّل ---
            output_lower = output.lower()
            
            # 1. البحث عن نموذج الراوتر (عادةً ما يحتوي على كلمة Router أو Processor Board ID)
            if 'router' in output_lower or 'cisco ios software, c' in output_lower or 'processor board id' in output_lower:
                return "Router (Cisco IOS)"
            
            # 2. البحث عن نموذج السويتش (عادةً ما يحتوي على كلمة Switch أو VIOs-L2)
            elif 'switch' in output_lower or 'vios-l2' in output_lower or 'ethernet switching' in output_lower:
                return "Switch (Cisco IOS)"
            
            # 3. إذا لم يتعرف عليه، لكن الاتصال نجح
            return "IOS Device (Generic)" 
        
        except Exception as e: 
            error_message = f"SSH/Netmiko connection failed for {ip}: {type(e).__name__} - {e}"
            print(error_message) 
            return None 

    def _process_ip(self, ip, mac):
        """تتم معالجة IP وتصنيفه بناءً على محاولة اتصال SSH/Netmiko."""
        sys_descr = self._check_cisco_ios(ip)

        with self.lock:
            category = "Others"
            
            # منطق التصنيف بناءً على نتيجة SSH/Netmiko
            if sys_descr and "Router" in sys_descr:
                category = "Routers"
            elif sys_descr and "Switch" in sys_descr:
                category = "Switches"

            # منطق خاص للأجهزة المعروفة مسبقاً بناءً على عنوان IP
            if ip == "192.168.31.100": 
                 category = "Servers"
                 sys_descr = "Server"
            if ip=="192.168.20.3":
                category="Switches"
                sys_descr="Switch"

            device_name = f"{category}{self.counters.get(category, 1)}"
            if category in self.counters: self.counters[category] += 1
            
            device_descr = sys_descr or 'Non-IOS Device (SSH Failed)'
            device_obj = {'ip': ip, 'mac': mac, 'name': device_name, 'descr': device_descr[:30]}
            
            # نضمن عدم تكرار الجهاز إذا تم اكتشافه بالفعل في نطاق سابق
            if device_obj not in self.discovered_devices.get(category, []):
                self.discovered_devices.setdefault(category, []).append(device_obj)

    # **الدالة الجديدة للمسح المتعدد**
    def scan_multiple(self, ip_ranges: list):
        """تكرار عملية المسح على نطاقات IP متعددة."""
        
        # إعادة تهيئة النتائج والعدادات مرة واحدة في البداية
        self.discovered_devices = {"Routers": [], "Switches": [], "Servers": [], "PCs": [], "Others": []}
        self.counters = {"Routers": 1, "Switches": 1, "Servers": 1, "PCs": 1, "Others": 1}
        
        for ip_range in ip_ranges:
            print(f"Scanning range: {ip_range}")
            self._scan_single_range(ip_range)
            
        return self.discovered_devices
        
    # **الدالة المساعدة للمسح على نطاق واحد (بدلاً من دالة 'scan' القديمة)**
    def _scan_single_range(self, ip_range): 
        """تنفيذ مسح ARP لنطاق واحد."""
        try:
            arp_req = ARP(pdst=ip_range)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            result = srp(broadcast/arp_req, timeout=3, verbose=0)[0] 
        except Exception as e:
            print(f"Scapy Error on {ip_range}: {e}")
            return

        threads = []
        for sent, received in result:
            t = threading.Thread(target=self._process_ip, args=(received.psrc, received.hwsrc))
            threads.append(t)
            t.start()
        
        scan_timeout = 30 
        start_time = time.time()
        for t in threads: 
            t.join(timeout=3) 
            if time.time() - start_time > scan_timeout:
                print(f"Scanning timeout reached for {ip_range}, exiting thread join.")
                break


def run_ip_helper_logic(target_ip, scan_results, ssh_user, ssh_pass, ssh_secret=None):
    """منطق تكوين IP Helper على الموجهات/المبدلات المكتشفة."""
    logs = []
    logs.append(f"Starting configuration for Relay Agent: {target_ip}")
    
    targets = scan_results.get("Routers", []) + scan_results.get("Switches", [])
    
    if not targets:
        logs.append("No Configurable Routers/Switches found in last scan.")
        return logs
    
    # الواجهة الافتراضية للـ IP Helper هي G0/1 أو G0/3 حيث يتصل السويتش، أو Vlan1 للسويتش نفسه
    
    for dev in targets:
        # تحديد الواجهة للتكوين (G0/1 لشبكة الـ LAN، Vlan1 للسويتش)
        interface_to_config = "GigabitEthernet0/1" # افتراضياً G0/1 كواجهة الـ LAN
        if "Switch" in dev['descr']:
             interface_to_config = "Vlan1" 
        elif "Router" in dev['descr'] and dev['ip'] == "192.168.32.10":
            # الراوتر المتصل بالـ Cloud
            interface_to_config = "GigabitEthernet0/0"
        
        logs.append(f"Configuring device: {dev['ip']} on interface {interface_to_config}...")
        
        device_model = Device(
            host=dev['ip'],
            username=ssh_user, 
            password=ssh_pass, 
            device_type="cisco_ios",
            secret=ssh_secret 
        )
        
        try:
            result = configure_device_task(
                device=device_model,
                ip_helper=target_ip,
                interface=interface_to_config 
            )
            output_snippet = result['output'].strip()[-50:] if result['output'] else ""
            logs.append(f" -> Status: {result['status']}, Output: {output_snippet}...")
        except Exception as e:
            logs.append(f" -> Error configuring {dev['ip']}: {e}")
            
    return logs


def run_dhcp_pool_logic(dhcp_params, scan_results, ssh_user, ssh_pass, ssh_secret=None):
    """
    منطق تكوين DHCP Pool على الموجه المكتشف.
    """
    logs = []
    
    targets = scan_results.get("Routers", []) 
    
    if not targets:
        logs.append("No Routers found to host the DHCP pool.")
        return logs

    dev = targets[0] # نأخذ أول راوتر مكتشف فقط
    
    logs.append(f"Starting DHCP Pool configuration on Router: {dev['ip']}")
    
    device_model = Device(
        host=dev['ip'],
        username=ssh_user,
        password=ssh_pass, 
        device_type="cisco_ios",
        secret=ssh_secret 
    )
    
    try:
        netmask = dhcp_params.get('netmask', '255.255.255.0') 
        # **التعديل:** استخدام G0/1 كواجهة البوابة لشبكة 192.168.20.0
        gateway_interface_for_dhcp = "GigabitEthernet0/1" 

        # --- 1. تكوين واجهة الراوتر كبوابة (Gateway Interface) ---
        logs.append(f" -> Configuring interface {gateway_interface_for_dhcp} with Gateway IP ({dhcp_params['default_router']})...")

        result_intf = configure_device_task(
            device=device_model,
            interface=gateway_interface_for_dhcp,
            ip_address=dhcp_params['default_router'],
            subnet_mask=netmask
        )

        if result_intf.get('status') != "Success":
            logs.append(f" -> FAILED to configure Gateway Interface: {result_intf.get('output', 'Unknown Error')}")
            return logs
        
        logs.append(" -> Gateway Interface configured successfully.")


        # --- 2. استبعاد IP البوابة (DHCP Exclusion) ---
        logs.append(" -> Excluding default router IP...")
        exclude_result = configure_dhcp_exclude_task(
             device=device_model,
             start_ip=dhcp_params['default_router'],
             end_ip=dhcp_params['default_router']
        )
        logs.append(f" -> Exclude Status: {exclude_result['status']}")

        # --- 3. تكوين بركة الـ DHCP (DHCP Pool) ---
        logs.append(" -> Creating Pool...")
        result = configure_dhcp_pool_task(
            device=device_model,
            pool_name=dhcp_params['pool_name'],
            network_addr=f"{dhcp_params['network']} {netmask}",
            default_router=dhcp_params['default_router'],
            dns_server=dhcp_params['dns_server']
        )
        
        output_snippet = result['output'].strip()[-50:] if result['output'] else ""
        logs.append(f" -> Pool Status: {result['status']}, Output: {output_snippet}...")
        
        if result['status'] == "Success":
            logs.append("DHCP Pool Configured Successfully.")
        else:
            logs.append("DHCP Pool Configuration Failed.")

    except Exception as e:
        logs.append(f" -> Error configuring DHCP on {dev['ip']}: {e}")
            
    return logs