import uasyncio

from time import sleep
from pico.common.cconnection import CConnection
from pico.common.cconnectionnode import CConnectionNode
from pico.common.chttpapi import CHTTPAPI
from pico.common.cfile import CFile

class CInterfaceThread:
    def __init__(self, rootFolder, devices, device):
        self.rootFolder = rootFolder
        self.defaultPage = "process"
        self.devices = devices
        self.device = device        
        self.running = False
        self.ended = True
        self.loop = None
        self.connectionnode = None
        
        if(self.device != None and self.device.deviceHierarchy != None):
            print("CInterfaceThread %s" % self.device.deviceHierarchy.Name)
            print("    rootFolder: %s" % self.rootFolder)
            print("    defaultPage: %s" % self.defaultPage)
            print("    device count: %i" % len(self.devices))
            self.loop = uasyncio.get_event_loop()
        else:
            print("device.ini is not found")
               
        
        #self.connection = CConnection()
#         self.httpAPI = None
#         
#         if(len(self.device.deviceini) == 0):
#             self.connection.start_ap_connection("pico_openiot_device","password")
#              
#         if(self.connection.status == 3):
#             self.httpAPI = CHTTPAPI(self.loop, self.device)
                     
        
    
    def start(self):
        print("CInterfaceThread start")
        if(self.loop != None):
            self.running = True
            self.ended = False
            
            connectionnodeHierachies = self.device.deviceHierarchy.GetChildrenByFeature("ThingType", "ConnectionNode")
            if(connectionnodeHierachies != None and len(connectionnodeHierachies) == 1):
                self.connectionnode = CConnectionNode(self.loop, connectionnodeHierachies[0], self.device)
            
            httpAPI = CHTTPAPI(self.loop, self.rootFolder, self.defaultPage, self.devices, self.device)
            self.loop.create_task(self.calculations())

            self.loop.run_forever()
            print("CInterfaceThread %s" % self.device.deviceHierarchy.Name)
            print("    loop program ended")            
            
        else:
            print("Cannot start interface, because device is not defined")
            
        print("CInterfaceThread %s loop ended" % self.device.name)
        self.ended = True
        
    def stop(self):
        print("CInterfaceThread stop")
        self.running = False
        self.loop.stop()
        self.loop.close()
        
#         while self.ended == False:
#             print("wait until loop is ended...")
#             sleep(1)
        
    async def calculations(self):
        while self.running:                            
#             for contentTag in self.device.contentTags.values():
#                 if(contentTag.value != None):
#                     print("%s: %s" % (contentTag.Name, str(contentTag.value)))
    
            await uasyncio.sleep_ms(1000)
        
