from netmiko import ConnectHandler

class Device:
    def __init__(self, host, username, password, device_type, secret=""):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.secret = secret

def _connect_and_send_config(device, config_commands):
    """Helper function to handle Netmiko connection and command execution."""
    netmiko_params = {
        'device_type': device.device_type,
        'host': device.host,
        'username': device.username,
        'password': device.password,
        'secret': device.secret,
        'session_log': 'netmiko_session.log',
        'global_delay_factor': 3.0,
        'timeout': 20
    }
    
    try:
        net_connect = ConnectHandler(**netmiko_params)
        if device.secret:
            net_connect.enable()
            
        output = net_connect.send_config_set(config_commands)
        net_connect.send_command("write memory")
        net_connect.disconnect()
        return {"status": "Success", "output": output}
        
    except Exception as e:
        print(f"Netmiko failed for {device.host}. Error: {e}")
        return {"status": "Failure", "output": f"Netmiko Error on {device.host}: {e}"}

def configure_device_task(**kwargs):
    """Configures IP Helper or IP Address."""
    device = kwargs.get('device')
    ip_helper = kwargs.get('ip_helper')
    interface = kwargs.get('interface', 'Vlan1')
    ip_address = kwargs.get('ip_address')
    subnet_mask = kwargs.get('subnet_mask')

    config_commands = []
    if ip_address and subnet_mask:
        config_commands = [
            f'interface {interface}',
            f'ip address {ip_address} {subnet_mask}',
            'no shutdown',
            'exit'
        ]
    elif ip_helper:
        config_commands = [
            f'interface {interface}',
            f'ip helper-address {ip_helper}',
            'exit'
        ]
    else:
        return {"status": "Failure", "output": "Missing parameters."}
    
    return _connect_and_send_config(device, config_commands)

def configure_dhcp_pool_task(**kwargs):
    """Configures a basic DHCP pool."""
    device = kwargs.get('device')
    pool_name = kwargs.get('pool_name')
    network_addr = kwargs.get('network_addr')
    default_router = kwargs.get('default_router') 
    dns_server = kwargs.get('dns_server', '8.8.8.8')
    
    config_commands = [
        f'ip dhcp pool {pool_name}',
        f'network {network_addr}',
        f'default-router {default_router}',
        f'dns-server {dns_server}',
        'exit'
    ]
    return _connect_and_send_config(device, config_commands)
#==================Add DNS Server Option==================#
def configure_dns_send_config(**kwargs):
    """Configure DNS Server"""
    device=kwargs.get('device')
    dns_server_ip = kwargs.get('dns_server') 
    
    if not dns_server_ip:
        return {"status": "Failure", "output": "No DNS IP provided"}
    config_commands=[
         f'ip domain-lookup',
        f'ip dns server',
        f'ip name-server {dns_server_ip}',
        'exit'
    ]
    return _connect_and_send_config(device,config_commands)

#=========================================================#
def configure_dhcp_exclude_task(**kwargs):
    """Excludes a range of IPs."""
    device = kwargs.get('device')
    start_ip = kwargs.get('start_ip')
    end_ip = kwargs.get('end_ip')
    
    cmd = f'ip dhcp excluded-address {start_ip}'
    if end_ip and end_ip != start_ip:
        cmd += f' {end_ip}'
    
    return _connect_and_send_config(device, [cmd])

def configure_dhcp_reservation_task(**kwargs):
    """
    Configures a Static Binding (Reservation).
    In Cisco IOS, this usually requires a separate pool for the host.
    """
    device = kwargs.get('device')
    reserved_ip = kwargs.get('reserved_ip')
    mac_address = kwargs.get('mac_address')
    
    host_pool_name = f"STATIC_{reserved_ip.replace('.', '_')}"
    
    
    config_commands = [
        f'ip dhcp pool {host_pool_name}',
        f'host {reserved_ip} 255.255.255.0', 
        f'hardware-address {mac_address} ethernet',
        'exit'
    ]
    
    return _connect_and_send_config(device, config_commands)