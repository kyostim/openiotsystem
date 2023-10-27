import network
import ubinascii
import gc
from time import sleep

class CConnection:
    def __init__(self):
        self.ssid = None
        self.ssidpw = None
        self.ipaddress = None        
        self.status = -1
        self.connectiontype = "unknown"
        
    def start_wifi_static_connection(self, ssid, ssidpw, ipaddress):
        self.ssid = ssid
        self.ssidpw = ssidpw
        self.ipaddress = ipaddress
        
        if(self.ssid != None and self.ssidpw != None):
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            self.mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
            print(self.mac)
 
            sleep(1)
            self.status = self.wlan.status()
            
            while(self.status < 3):
                self.wlan.ifconfig((self.ipaddress, '255.255.255.0', self.ipaddress, '8.8.8.8'))
                self.wlan.connect(self.ssid, self.ssidpw)
                
                reconnectcounter = 0
                while(self.wlan.isconnected() == False and reconnectcounter < 10):
                    reconnectcounter = reconnectcounter + 1
                    print('Waiting for connection... status:', self.status)
                    sleep(1)
                    self.status = self.wlan.status()

                    sleep(1)
                if(reconnectcounter >= 10):
                    return False
            self.ipaddress = self.wlan.ifconfig()[0]
            print(f'Connected on {self.ipaddress}')
            self.connectiontype = "static"
            return True
        
        
    def start_wifi_dhcp_connection(self,ssid, ssidpw):
        self.ssid = ssid
        self.ssidpw = ssidpw
        
        if(self.ssid != None and self.ssidpw != None):
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            self.mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
            print(self.mac)
 
            sleep(1)
            self.status = self.wlan.status()
            
            while(self.status < 3):
                #self.wlan.ifconfig(('192.168.58.1', '255.255.255.0', '192.168.58.1', '8.8.8.8'))
                self.wlan.connect(ssid, ssidpw)
                
                reconnectcounter = 0
                while(self.wlan.isconnected() == False and reconnectcounter < 10):
                    reconnectcounter = reconnectcounter + 1
                    print('Waiting for connection(%i)... status: %s' % (reconnectcounter, self.status))
                    sleep(1)
                    self.status = self.wlan.status()

                    sleep(1)
                if(reconnectcounter >= 10):
                    return False
            self.ipaddress = self.wlan.ifconfig()[0]
            print(f'Connected on {self.ipaddress}')
            self.connectiontype = "dhcp"
            return True
            
    def start_ap_connection(self,ssid, ssidpw):
        self.ssid = ssid
        self.ssidpw = ssidpw
        gc.collect()

        if(self.ssid != None and self.ssidpw != None):
            self.wlan = network.WLAN(network.AP_IF)
            self.wlan.config(essid=self.ssid, password=self.ssidpw)
            self.wlan.active(True)
            self.mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
            print(self.mac)

            sleep(1)
            self.status = self.wlan.status()
            while(self.status < 3):
                while self.wlan.active() == False:
                    print('Waiting for access point started... status:', self.status)
                    sleep(1)
                    self.status = self.wlan.status()
                    sleep(1)
                
            print('Connection is successful')
            self.connectiontype = "ap"
            print(self.wlan.ifconfig())
