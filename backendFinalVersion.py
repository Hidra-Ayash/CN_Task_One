import threading                                                                                                                       #مكتبة كي لا تتجمد الواجهة اثناء التنفيذ
import socket
import re
import time
from scapy.all import ARP, Ether, srp
from pysnmp.hlapi import *
from netmiko import ConnectHandler

try:
    from back_one import configure_device_task, Device
except ImportError:
    class Device:
        def __init__(self, host, username, password, device_type):
            self.host = host
            self.username = username
            self.password = password
            self.device_type = device_type
            self.port = 22

    def configure_device_task(**kwargs):
        return {"status": "Mock Success", "output": "Configured"}

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
            'secret': self.ssh_secret,
            'fast_cli': True,
        }
        commands = ['snmp-server community public ro']
        net_connect = None
        try:
            net_connect = ConnectHandler(**device_params)
            if self.ssh_secret:
                net_connect.enable()
            net_connect.send_config_set(commands)
            return True, "Success"
        except Exception as e:
            return False, str(e)
        finally:
            if net_connect:
                net_connect.disconnect()

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
        descr = str(sys_descr).lower()
        if re.search(r'cisco.*(isr|1841|2800|2900|4000|asr|router)', descr):
            return "Routers"
        
        try:
            if sys_services and (int(sys_services) & 4):
                return "Routers"
        except: pass

        if "switch" in descr or "catalyst" in descr:
            return "Switches"
            
        try:
            if sys_services and (int(sys_services) & 2):
                return "Switches"
        except: pass

        if "windows server" in descr or "linux" in descr:
            return "Servers"
        elif "windows" in descr:
            return "PCs"
            
        return "Others"

    def _process_ip(self, ip, mac, auto_fix_ssh):
        sys_descr = self._get_oid(ip, '1.3.6.1.2.1.1.1.0')
        sys_services = self._get_oid(ip, '1.3.6.1.2.1.1.7.0')

        if sys_descr is None and auto_fix_ssh and self.ssh_user:
            success, msg = self.enable_snmp_via_ssh(ip)
            if success:
                sys_descr = self._get_oid(ip, '1.3.6.1.2.1.1.1.0')
                sys_services = self._get_oid(ip, '1.3.6.1.2.1.1.7.0')

        with self.lock:
            if sys_descr:
                category = self._parse_device_type(sys_descr, sys_services)
                single_name = category[:-1] if category.endswith('s') else category
                device_name = f"{single_name}{self.counters[category]}"
                self.counters[category] += 1
                
                device_obj = {'ip': ip, 'mac': mac, 'name': device_name, 'descr': sys_descr[:30]}
                self.discovered_devices[category].append(device_obj)
            else:
                device_name = f"Unknown{self.counters['Others']}"
                self.counters["Others"] += 1
                self.discovered_devices["Others"].append({'ip': ip, 'mac': mac, 'name': device_name})

    def scan(self, ip_range="192.168.1.0/24", auto_fix_ssh=False):
        arp_req = ARP(pdst=ip_range)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        result = srp(broadcast/arp_req, timeout=2, verbose=0)[0]
        
        threads = []
        
        for sent, received in result:
            ip = received.psrc
            mac = received.hwsrc
            
            t = threading.Thread(target=self._process_ip, args=(ip, mac, auto_fix_ssh))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        return self.discovered_devices

def Run_Ip_Helper_Automation(target_ip_helper):
    scanner = Scan(ssh_user="admin", ssh_pass="cisco123", ssh_secret="cisco")
    devices_map = scanner.scan("192.168.1.0/24", auto_fix_ssh=True)
    
    target_devices = devices_map["Routers"] + devices_map["Switches"]
    
    if not target_devices:
        return

    for dev in target_devices:
        device_model = Device(
            host=dev['ip'],
            username="admin",
            password="cisco",
            device_type="cisco_ios"
        )
        
        result = configure_device_task(
            device=device_model,
            ip_helper=target_ip_helper,
            interface="Vlan1"
        )
        print(f"Result for {dev['ip']}: {result}")

if __name__ == "__main__":
    Run_Ip_Helper_Automation("10.10.10.50")