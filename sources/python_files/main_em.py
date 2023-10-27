import os
import sys
import uasyncio
import _thread
from time import sleep

from pico.common.cfile import CFile
from pico.common.cconnection import CConnection
from imot.cimotparser import CIMoTParser
from pico.common.cdevice import CDevice
from cinterfacethread import CInterfaceThread
from cprocessthread import CProcessThread

from pico.common.chttpapi import CHTTPAPI
from pico.common.ciniparser import CIniParser

interfaceThread = None
processThread = None
defaultPage = ""
devices = []
device = None

def Core0Process():
    global device, interfaceThread, devices, rootFolder
    interfaceThread = CInterfaceThread(rootFolder, devices, device)       
    interfaceThread.start()

def Core1Process():
    global device, processThread
    processThread = CProcessThread(device)
    processThread.start() 

rootFolder = os.getcwd() #for pico
#rootFolder = os.path.abspath(__file__+"/../../..")
sys.path.append(rootFolder)
print("Root folder:%s" % rootFolder)
sys.path.append(rootFolder)

connectionini = CFile.GetFileContent(rootFolder + "/connection.ini")
configxml = CFile.GetFileContent(rootFolder + "/config.xml")
deviceini = CFile.GetFileContent(rootFolder + "/device.ini")



ssid = ""
ssidpw = ""
uuid = ""
apconnection = True
ipaddress = ""

if(len(connectionini) == 0):
    print("connection.ini not found")
    connection.start_ap_connection("pico_openiot_device","password")
    defaultPage = "connection"
else:
    print("connection.ini found")
    connectionArgs = CIniParser.GetIni(rootFolder + "/connection.ini")
    if(len(connectionArgs) == 2):
        if("ssid" in connectionArgs):
            ssid = connectionArgs["ssid"]
        if("ssidpw" in connectionArgs):
            ssidpw = connectionArgs["ssidpw"]
        
            
if(len(configxml) == 0):
    print("config.xml not found")
    defaultPage = "config"   
else:
    if(len(deviceini) > 0):
        connectionArgs = CIniParser.GetIni(rootFolder + "/device.ini")
        if(len(connectionArgs) == 1):
            if("uuid" in connectionArgs):
                uuid = connectionArgs["uuid"]
                print("uuid: %s" % uuid)
                
    imotParser = CIMoTParser(configxml)
    iotdevices = imotParser.GetHierarchiesByFeature("ThingType","OpenIoTDevice")
    if(len(iotdevices) > 0):
        print("Open IoT device(s) found")
        devices = []
        for iotdevice in iotdevices:
            cdevice = CDevice(iotdevice, rootFolder, ssid, ssidpw)
            devices.append(cdevice)
            if(cdevice.uuid == uuid):
                device = cdevice
                ipaddress = device.ipaddress
                print('Open IoT Device(%s:%s) %s' % (device.name, device.uuid, device.ipaddress))
                
    defaultPage = "device"
    
#open connection
connection = CConnection()    
if(len(ssid) == 0 or len(ssidpw) == 0):
    connection.start_ap_connection("pico_openiot_device","password")
else:
    ok = False
    if(len(ipaddress) == 0):
        ok = connection.start_wifi_dhcp_connection(ssid, ssidpw)
    else:
        ok = connection.start_wifi_static_connection(ssid, ssidpw, ipaddress)
        
    if(ok == False):
        connection.start_ap_connection("pico_openiot_device","password")
        
if(device != None and connection.connectiontype=="static"):
    print("Device(%s) settings ready... start device operations" % device.name)
    
    #start new thread in an other core
    _thread.start_new_thread(Core1Process, ())
    while processThread == None or processThread.running == False:
        print("wait until processThread is started...")
        sleep(1)
         
    try:
        Core0Process()
    except KeyboardInterrupt:        
        print("Core 0 KeyboardInterrupt")
    finally:
        processThread.stop()
        while processThread.ended == False:
             sleep(0.001)

        interfaceThread.stop()
        print("program ended")
        #machine.reset()
 
    
else:
    loop = uasyncio.get_event_loop()
    CHTTPAPI(loop, rootFolder, defaultPage, devices, device)
    loop.run_forever()
    


 
        
#open interface
    
        
        
# if(len(ssid) > 0 and len(ssidpw) > 0):
#     ok = False
#     if(len(ipaddress) > 0):
#         ok = connection.start_wifi_static_connection(ssid, ssidpw, ipaddress)
#     else:
#         ok = connection.start_wifi_dhcp_connection(ssid, ssidpw)
#         
#     if(ok == False):
#         connection.start_ap_connection("pico_openiot_device","password")
#         defaultPage = "connection"
# else:
#     connection.start_ap_connection("pico_openiot_device","password")
#     defaultPage = "connection"  
# 
# httpConnectionAPI = CHTTPAPI(loop, rootFolder, defaultPage, devices, device)
# if(device != None):
#     print("Device(%s) settings ready... start device operations" % device.name)
#     
# loop.run_forever() 


 

# if(len(deviceini) == 0 and len(configxml) == 0):
#     connection = CConnection()
#     print("config.xml and device.ini not found")
#     connection = CConnection()
#     connection.start_ap_connection("pico_openiot_device","password")
#     httpConfigAPI = CHTTPConfigAPI(loop, rootFolder)
#     loop.run_forever()
#         
# elif(len(deviceini) == 0 and len(configxml) > 10):
#     print("config.xml found but device.ini not")
#     connection = CConnection()
#     connection.start_ap_connection("pico_openiot_device","password")
#     imotParser = CIMoTParser(configxml)
#     iotdevices = imotParser.GetHierarchiesByFeature("ThingType","OpenIoTDevice")
#     if(len(iotdevices) > 0):
#         print("Open IoT device(s) found")
#         devices = []
#         for iotdevice in iotdevices:
#             devices.append(CDevice(iotdevice, rootFolder))
#                            
#         httpDeviceAPI = CHTTPDeviceAPI(loop,rootFolder, devices)
#     else:
#         print("No open IoT devices defined in config.xml")
#         connection.start_ap_connection("pico_openiot_device","password")
#     
#     loop.run_forever()
#     
# else:
#     print("hah")





# if(len(configxml) == 0):
#     connection = CConnection()
# else:
#     imotParser = CIMoTParser(configxml)
# 
#     #device.ini 
#     deviceini = CFile.GetFileContent(rootFolder + "/device.ini")
#     #if(len(deviceini) > 0):
#     #    self.ParseDeviceIni()
# 
#     #get open IoT devices
#     device = None
#     iotdevices = imotParser.GetHierarchiesByFeature("ThingType","OpenIoTDevice")
#     for iotdevice in iotdevices:
#         picoWDevice = iotdevice.GetFeature("DeviceType", "PicoW")
#         if(picoWDevice != None):
#             device = CDevice(iotdevice)


    
    
    

# #device.ini 
# self.deviceini = CFile.GetFileContent(self.root_folder + "/device.ini")
# if(len(self.deviceini) > 0):
#     self.ParseDeviceIni()
# 
# self.contentTags = {} 
# self.deviceHierarchy = self.imotParser.GetHierarchyByHierarchyUUID(self.uuid) 

# import os
# import sys
# import machine
# import _thread
# from time import sleep
# 
# from pico.common.cdevice import CDevice
# from pico.common.cfile import CFile
# from pico.energymeter.cinterfacethread import CInterfaceThread
# from pico.energymeter.cprocessthread import CProcessThread
# from pico.common.ccontenttag import CContentTag
# 
# 
# root_folder = os.getcwd() #for pico
# #root_folder = os.path.abspath(__file__+"/../../..")
# sys.path.append(root_folder)
# print("Root folder:%s" % root_folder)
# sys.path.append(root_folder)
# 
# device = CDevice(root_folder)
# 
# #Start process cycles
# interfaceThread = None
# processThread = None
# 
# def Core0Process():
#     global interfaceThread, contentTags
#     interfaceThread = CInterfaceThread(device)       
#     interfaceThread.start()        
#         
# # def Core1Process():
# #     global processThread, contentTags
# #     processThread = CProcessThread(energymeterHierarchy, contentTags)
# #     processThread.start()  
# 
# Core0Process()
# #reservedarray = bytearray(3000)
# 
# 
# # from imot.cimotparser import CIMoTParser
# # 
# # #config.xml
# # configxml = CFile.GetFileContent(root_folder + "/pico/energymeter/config.xml")  
# # imotParser = CIMoTParser(configxml)
# # 
# # contentTags = {} 
# # energymeterHierarchy = imotParser.GetHierarchyByHierarchyUUID("a78d3210-4cb7-43a5-883c-8b29d5bb9d42") 
# # if(energymeterHierarchy != None):
# #     
# #     contentTagHierarchies = energymeterHierarchy.GetChildrenByFeature("ThingType", "ContentTag")
# #     for contentTagHierarchy in contentTagHierarchies:
# #         if(contentTagHierarchy.Thing != None and contentTagHierarchy.Thing.ThingUUID not in contentTags):
# #             contentTags[contentTagHierarchy.Thing.ThingUUID] = CContentTag(contentTagHierarchy)
# #         else:
# #             print("%s is exists in different hierarchy" % contentTagHierarchy.Name)
# # 
# #     print("Total number of ContentTag Things: %i" % len(contentTags))
# #     #Start prcess cycles
# #     interfaceThread = None
# #     processThread = None
# #     
# #     def Core0Process():
# #         global interfaceThread, contentTags
# #         interfaceThread = CInterfaceThread(energymeterHierarchy, contentTags, root_folder)       
# #         interfaceThread.start()        
# #             
# #     def Core1Process():
# #         global processThread, contentTags
# #         processThread = CProcessThread(energymeterHierarchy, contentTags)
# #         processThread.start()            
# # 
# # 
# #     #start new thread in an other core
# #     _thread.start_new_thread(Core1Process, ())
# #     while processThread == None or processThread.running == False:
# #         print("wait until processThread is started...")
# #         sleep(1)
# #         
# #     Core0Process()
# # 
# # #     #start main thread process    
# # #     try:
# # #         Core0Process()
# # #     except KeyboardInterrupt:        
# # #         print("Core 0 KeyboardInterrupt")
# # #     finally:
# # #         processThread.stop()
# # #         interfaceThread.stop()
# # #         print("program ended")
# 
# 