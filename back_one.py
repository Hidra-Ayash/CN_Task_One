from netmiko import ConnectHandler

class Device:
    def __init__(self, host, username, password, device_type, secret=""):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        # If secret is not provided, fallback to password, but it's better to provide it
        self.secret = secret

def _connect_and_send_config(device, config_commands):
    """Helper function to handle Netmiko connection and command execution."""
    
    netmiko_params = {
        'device_type': device.device_type,
        'host': device.host,
        'username': device.username,
        'password': device.password,
        'secret': device.secret, # يستخدم secret
        'session_log': 'netmiko_session.log', 
        # التعديل: زيادة عامل التأخير لتعويض بطء GNS3
        'global_delay_factor': 3.0, 
        # التعديل: إضافة مهلة الاتصال المفقودة لتجنب الـ Timeout
        'timeout': 20 
    }
    
    try:
        net_connect = ConnectHandler(**netmiko_params)
        
        # Always try to enable if a secret exists
        if device.secret:
            net_connect.enable()
            
        output = net_connect.send_config_set(config_commands)
        # Ensure we save config
        net_connect.send_command("write memory")
        
        net_connect.disconnect()
        return {"status": "Success", "output": output}
        
    except Exception as e:
        # طباعة الخطأ في الكونسول للمساعدة في تتبع سبب الفشل (Timeout, Auth, etc.)
        print(f"Netmiko failed for {device.host}. Error: {e}")
        return {"status": "Failure", "output": f"Netmiko Error on {device.host}: {e}"}


def configure_device_task(**kwargs):
    """Configures IP Helper address on a specified interface or IP/Mask on a specified interface."""
    device = kwargs.get('device')
    ip_helper = kwargs.get('ip_helper')
    interface = kwargs.get('interface', 'Vlan1')
    ip_address = kwargs.get('ip_address')
    subnet_mask = kwargs.get('subnet_mask')

    if ip_address and subnet_mask:
        # تكوين IP Mask على الواجهة
        print(f"Attempting to configure IP Address {ip_address} on {device.host} interface {interface}...")
        config_commands = [
            f'interface {interface}',
            f'ip address {ip_address} {subnet_mask}',
            'no shutdown', # تأكد من أن الواجهة مرفوعة
            'exit'
        ]
    elif ip_helper:
        # تكوين IP Helper
        print(f"Attempting to configure IP Helper {ip_helper} on {device.host} interface {interface}...")
        config_commands = [
            f'interface {interface}',
            f'ip helper-address {ip_helper}',
            'exit'
        ]
    else:
        return {"status": "Failure", "output": "Missing parameters for configuration task."}
    
    return _connect_and_send_config(device, config_commands)


def configure_dhcp_pool_task(**kwargs):
    """Configures a basic DHCP pool on a router."""
    device = kwargs.get('device')
    pool_name = kwargs.get('pool_name')
    network_addr = kwargs.get('network_addr')
    default_router = kwargs.get('default_router') 
    dns_server = kwargs.get('dns_server', '8.8.8.8')
    
    print(f"Attempting to configure DHCP pool '{pool_name}' on {device.host}...")
    
    config_commands = [
        f'ip dhcp pool {pool_name}',
        f'network {network_addr}',
        f'default-router {default_router}',
        f'dns-server {dns_server}',
        'exit'
    ]
    
    return _connect_and_send_config(device, config_commands)

def configure_dhcp_exclude_task(**kwargs):
    """Excludes a range of IP addresses from DHCP assignment."""
    device = kwargs.get('device')
    start_ip = kwargs.get('start_ip')
    end_ip = kwargs.get('end_ip', start_ip)
    
    config_command = f'ip dhcp excluded-address {start_ip} {end_ip}'
    
    return _connect_and_send_config(device, [config_command])