from pico.common.cfile import CFile
#from imot.cimotparser import CIMoTParser
from pico.common.ccontenttag import CContentTag

class CDevice:
    def __init__(self, deviceHierarchy, rootFolder, ssid, ssidpw):
        self.deviceHierarchy = deviceHierarchy
        self.rootFolder = rootFolder
        self.deviceini = ""
        self.name = ""
        self.uuid = ""
        self.ssid = ssid
        self.ssidpw = ssidpw
        self.ipaddress = ""
        self.contentTags = {}
        
        
        if(self.deviceHierarchy != None):
            self.name = self.deviceHierarchy.Name
            self.uuid = self.deviceHierarchy.HierarchyUUID
            
            
            ipaddress = self.deviceHierarchy.GetFeature("IPAddress")
            if(ipaddress != None):
                print("haha")
                self.ipaddress = ipaddress.Value
                
            print("CDevice: %s(%s) ip:%s" % (self.name,self.uuid, self.ipaddress))
            
            contentTagHierarchies = self.deviceHierarchy.GetChildrenByFeature("ThingType", "ContentTag")
            for contentTagHierarchy in contentTagHierarchies:
                if(contentTagHierarchy.Thing != None and contentTagHierarchy.Thing.ThingUUID not in self.contentTags):
                    self.contentTags[contentTagHierarchy.Thing.ThingUUID] = CContentTag(contentTagHierarchy)
                else:
                    print("%s is exists in different hierarchy" % contentTagHierarchy.Name)

            print("Total number of ContentTag Things: %i" % len(self.contentTags))
        
        
        
        
#         #device.ini 
#         self.deviceini = CFile.GetFileContent(self.rootFolder + "/device.ini")
#         if(len(self.deviceini) > 0):
#             self.ParseDeviceIni()
#         
#         #config.xml
#         self.configxml = CFile.GetFileContent(root_folder + "/pico/energymeter/config.xml")  
#         self.imotParser = CIMoTParser(self.configxml)
#         
#         self.contentTags = {} 
#         self.deviceHierarchy = self.imotParser.GetHierarchyByHierarchyUUID(self.uuid) 
#         if(self.deviceHierarchy != None):
#             self.name = self.deviceHierarchy.Name
#             self.uuid = self.deviceHierarchy.HierarchyUUID
#             
#             contentTagHierarchies = self.deviceHierarchy.GetChildrenByFeature("ThingType", "ContentTag")
#             for contentTagHierarchy in contentTagHierarchies:
#                 if(contentTagHierarchy.Thing != None and contentTagHierarchy.Thing.ThingUUID not in self.contentTags):
#                     self.contentTags[contentTagHierarchy.Thing.ThingUUID] = CContentTag(contentTagHierarchy)
#                 else:
#                     print("%s is exists in different hierarchy" % contentTagHierarchy.Name)
# 
#             print("Total number of ContentTag Things: %i" % len(self.contentTags))
            
            
#     def ParseDeviceIni(self):
#         print("CDevice::ParseDeviceIni(%s)" % self.name)
#         argumentLines = deviceini.split("\n") 
#         for argumentLine in argumentLines:
#             argumentParts = argumentLine.split("=")
#             if(len(argumentParts) == 2):
#                 arguments[argumentParts[0].strip()] = argumentParts[1].strip()
#                 
#         if("HierarchyUUID" in arguments):            
#             self.uuid = arguments["HierarchyUUID"]
#             print("    HierarchyUUID:%s" % self.uuid)
#         else:
#             print("    HierarchyUUID not found")
#             
#         if("SSID" in arguments):
#             self.ssid = arguments["SSID"]
#             print("    HierarchyUUID:%s" % self.ssid)
#         else:
#             print("    SSID not found")
#             
#         if("SSIDPW" in arguments):
#             self.ssidpw=arguments["SSIDPW"]
#             print("    SSIDPW:%s" % self.ssidpw)
#         else:
#             print("    SSIDPW not found")
            



    