class Device:
    def __init__(self,host,username,password,device_type):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type




def configure_device_task(**kwargs):
    device = kwargs.get('device')
    ip_helper = kwargs.get('ip_helper')
    interface = kwargs.get('interface')


    print(f"starting config on {device.host}")
    print(f"interface :{interface}")
    print(f"ip_helper_address{ip_helper}")


    return {"status" : "success","output":"configured"}