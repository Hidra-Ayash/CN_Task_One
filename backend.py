import threading 
import socket
import time
from scapy.all import ARP,Ether,srp
from pysnmp.hlapi import* 
from netmiko import ConnectHandler 


class CN :
    def __init__(self,snmp_community='public',ssh_user= None,ssh_pass= None,ssh_secret= None):
          self. snmp_community = snmp_community
          self.ssh_user = ssh_user
          self.ssh_pass = ssh_pass
          self.ssh_secret = ssh_secret 
          self.discovered_Devices ={"Routers":[],"Switches":[],"Servers":[],"pcs":[]}


    def enable_snmp_via_ssh(self,ip,device_type='cisco_ios'):
         device_params = {
          'device_type':device_type,
          'ip':ip,
          'username':self.ssh_user,
          'password':self.ssh_pass,
          'secret':self.ssh_secret,
          'fast_cli': True,  
           }


         commands = ['snmp-server community public ro']
         net_connect=None
         try:
           net_connect = ConnectHandler(**device_params)
           if self.ssh_secret:
             net_connect.enable()
             output=net_connect.send_config_set(commands)
             return output
         except Exception as e:
             print(f"error config")
             return None
         finally:
             if net_connect:
                 net_disconnect()
               
    def _get_oid (self,ip,oid):
          iterator = getCmd( 
            SnmpEngine(),
            CommunityData(self.snmp_community,mpModel=1),
            UdpTransportTarget((ip,161),timeout=1,retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
         )
          errorIndication,errorStatus,errorIndex,varBinds=next(iterator)