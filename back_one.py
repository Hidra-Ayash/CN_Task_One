class Device:
    def __init__(self, host, username, password, device_type):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type

def configure_device_task(**kwargs):
    device = kwargs.get('device')
    ip_helper = kwargs.get('ip_helper')
    interface = kwargs.get('interface')

    # طباعة توضيحية لعملية التكوين
    print(f"starting config on {device.host}")
    
    # محاكاة النتيجة الناجحة
    return {
        "status": "success", 
        "output": f"Configured IP Helper {ip_helper} on {interface}"
    }