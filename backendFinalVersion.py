import threading
import re
# تأكد من تثبيت المكتبات: pip install scapy pysnmp netmiko
from scapy.all import ARP, Ether, srp
from pysnmp.hlapi import *
from netmiko import ConnectHandler
# محاولة استيراد الكلاس من الملف الأول، أو إنشاء بديل وهمي في حال عدم وجوده
try:
    from back_one import configure_device_task, Device
except ImportError:
    class Device:
        def __init__(self, host, username, password, device_type):
            self.host = host; self.username = username; self.password = password; self.device_type = device_type
    def configure_device_task(**kwargs): return {"status": "Mock Success", "output": "Configured (Mock)"}

class Scan:
    def __init__(self, snmp_community='public', ssh_user=None, ssh_pass=None, ssh_secret=None):
        self.snmp_community = snmp_community
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_secret = ssh_secret
        self.discovered_devices = {"Routers": [], "Switches": [], "Servers": [], "PCs": [], "Others": []}
        self.counters = {"Routers": 1, "Switches": 1, "Servers": 1, "PCs": 1, "Others": 1}
        self.lock = threading.Lock()

    def enable_snmp_via_ssh(self, ip, device_type='cisco_ios'):
        device_params = {
            'device_type': device_type, 
            'ip': ip, 
            'username': self.ssh_user, 
            'password': self.ssh_pass, 
            'secret': self.ssh_secret
        }
        try:
            net_connect = ConnectHandler(**device_params)
            if self.ssh_secret: 
                net_connect.enable()
            # إرسال أمر تفعيل SNMP
            net_connect.send_config_set(['snmp-server community public ro'])
            net_connect.disconnect()
            return True, "Success"
        except Exception as e: 
            return False, str(e)

    def _get_oid(self, ip, oid):
        try:
            iterator = getCmd(
                SnmpEngine(), 
                CommunityData(self.snmp_community, mpModel=1), 
                UdpTransportTarget((ip, 161), timeout=1, retries=1), 
                ContextData(), 
                ObjectType(ObjectIdentity(oid))
            )
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            if errorIndication or errorStatus: 
                return None
            return str(varBinds[0][1])
        except: 
            return None

    def _parse_device_type(self, sys_descr, sys_services):
        # تصحيح المسافة البادئة هنا (Indentation Fix)
        descr = str(sys_descr).lower()
        if re.search(r'cisco.*(isr|1841|2800|2900|4000|asr|router)', descr): return "Routers"
        if "switch" in descr or "catalyst" in descr: return "Switches"
        if "windows" in descr: return "PCs"
        return "Others"

    def _process_ip(self, ip, mac, auto_fix_ssh):
        sys_descr = self._get_oid(ip, '1.3.6.1.2.1.1.1.0')
        
        # محاولة الإصلاح التلقائي عبر SSH إذا لم يتم العثور على وصف SNMP
        if sys_descr is None and auto_fix_ssh and self.ssh_user:
            self.enable_snmp_via_ssh(ip)
            sys_descr = self._get_oid(ip, '1.3.6.1.2.1.1.1.0')

        with self.lock:
            category = self._parse_device_type(sys_descr, "") if sys_descr else "Others"
            
            device_name = f"{category}{self.counters.get(category, 1)}"
            if category in self.counters: 
                self.counters[category] += 1
            
            device_obj = {'ip': ip, 'mac': mac, 'name': device_name, 'descr': str(sys_descr)[:30]}
            if category in self.discovered_devices:
                self.discovered_devices[category].append(device_obj)

    def scan(self, ip_range="192.168.1.0/24", auto_fix_ssh=False):
        try:
            # إرسال ARP Request
            arp_req = ARP(pdst=ip_range)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            # verbose=0 لمنع طباعة التفاصيل الكثيرة في الكونسول
            result = srp(broadcast/arp_req, timeout=2, verbose=0)[0]
        except Exception as e:
            print(f"Scapy Error (Run as Admin/Root?): {e}")
            return {}

        threads = []
        for sent, received in result:
            t = threading.Thread(target=self._process_ip, args=(received.psrc, received.hwsrc, auto_fix_ssh))
            threads.append(t)
            t.start()
        
        for t in threads: 
            t.join()
            
        return self.discovered_devices

def run_ip_helper_logic(target_ip, scan_results):
    logs = []
    logs.append(f"Starting configuration for Relay Agent: {target_ip}")
    
    # استخراج الراوترات والسويتشات فقط من نتائج الفحص
    targets = scan_results.get("Routers", []) + scan_results.get("Switches", [])
    
    if not targets:
        logs.append("No Routers or Switches found in last scan.")
        return logs

    for dev in targets:
        logs.append(f"Configuring device: {dev['ip']}...")
        
        # ملاحظة: هنا يتم استخدام اسم مستخدم وكلمة مرور ثابتة
        # يمكنك تغييرها لتستقبل البيانات من الواجهة الرسومية إذا أردت
        device_model = Device(
            host=dev['ip'],
            username="admin", 
            password="cisco", 
            device_type="cisco_ios"
        )
        
        try:
            result = configure_device_task(
                device=device_model,
                ip_helper=target_ip,
                interface="Vlan1" 
            )
            logs.append(f" -> Status: {result['status']}, Output: {result['output']}")
        except Exception as e:
            logs.append(f" -> Error configuring {dev['ip']}: {e}")
            
    return logs