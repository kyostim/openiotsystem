import socket
import os
import sys
import time
import datetime
import struct
from time import sleep

#rootFolder = os.getcwd() #for pico
rootFolder = os.path.abspath(__file__+"/../..")
sys.path.append(rootFolder)
print("Root folder:%s" % rootFolder)
sys.path.append(rootFolder)

from imot.cimotparser import CIMoTParser
from common.cfile import CFile
from common.ccontenttag import CContentTag

def reverseBytes(byteArray):
    reversedByteArray = bytearray()
    for i in range(len(byteArray)-1,-1,-1):
        reversedByteArray.append(byteArray[i])
    return reversedByteArray

hierarchyUUID = ""
if(len(sys.argv) > 1):
    hierarchyUUID = sys.argv[1]
    
    configxml = CFile.GetFileContent(rootFolder + "/config.xml")
    imotParser = CIMoTParser(configxml)
    connectionnodeHierarchy = imotParser.GetHierarchyByHierarchyUUID(hierarchyUUID)
    
    connectionNodeThingUUID = ""
    host = ""
    port = 0
    contentTags = {}
        
    if(connectionnodeHierarchy != None and connectionnodeHierarchy.Thing != None):
        connectionNodeThingUUID = connectionnodeHierarchy.Thing.ThingUUID
        print(connectionnodeHierarchy.Name)
        
        
        deviceHierarchy = connectionnodeHierarchy.GetParentByFeature("ThingType", "OpenIoTDevice")
        if(deviceHierarchy != None):
            ipaddress = deviceHierarchy.GetFeature("IPAddress")
            if(ipaddress != None):
                host = ipaddress.Value
                print("    IPAddress: %s" % host)
        
        outputport = connectionnodeHierarchy.GetFeature("OutputPort")
        if(outputport != None):
            port = int(outputport.Value)
            print("    OutputPort: %d" % port)
                
        
        contentblockHierarchies = connectionnodeHierarchy.GetChildrenByFeature("ThingType", "ContentBlock")
        if(len(contentblockHierarchies) == 1):
            contentTagHierarchies = contentblockHierarchies[0].GetChildrenByFeature("ThingType", "ContentTag")
            if(len(contentTagHierarchies) > 0):
                for contentTagHierarchy in contentTagHierarchies:
                    contentTag = CContentTag(contentTagHierarchy)
                    contentTags[contentTag.thing.ThingUUID] = contentTag


        
if(len(connectionNodeThingUUID) == 36 and len(host) > 6 and port > 0 and len(contentTags) > 0):
    millisecondstoepoch = 0
    timestamp = 0
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        while True:
            openiotmessage = client_socket.recv(65535)
            if(len(openiotmessage) >= 0x12):
                messagetype = int.from_bytes(openiotmessage[0x0:0x2], "little")
                #print(messagetype)
                if(messagetype == 3 and len(openiotmessage) >= 0x1e ): #0x0003 = monitoring message contains sender uuid + floating timestamp + length + content
                    uuidarray1 = openiotmessage[0x2:0x6]
                    uuidarray2 = openiotmessage[0x6:0x8]
                    uuidarray3 = openiotmessage[0x8:0xa]
                    uuidarray4 = openiotmessage[0xa:0xc]
                    uuidarray5 = openiotmessage[0xc:0x12]
                    uuid1 = reverseBytes(uuidarray1).hex()
                    uuid2 = reverseBytes(uuidarray2).hex()
                    uuid3 = reverseBytes(uuidarray3).hex()
                    uuid4 = uuidarray4.hex()
                    uuid5 = uuidarray5.hex()
                    uuid = uuid1 + "-" + uuid2 + "-" + uuid3 + "-" + uuid4 + "-" + uuid5 
                    #print(uuid)
                    if(uuid == connectionNodeThingUUID):                    
                        timestamparray = openiotmessage[0x12:0x1a]
                        floatigtimestamp = int.from_bytes(timestamparray, "little")
                        testi = struct.unpack("<q", timestamparray)[0]
                        
                        if(millisecondstoepoch == 0):
                            millisecondstoepoch =  round(time.time() * 1000)
                        else:
                            timestamp = millisecondstoepoch + floatigtimestamp
                        
                        lengtharray = openiotmessage[0x1a:0x1e]
                        length = int.from_bytes(lengtharray, "little")
                        
                        if((len(openiotmessage) - 0x1e - length) == 0):
                            contentarray = openiotmessage[0x1e:(0x1e + length)]
                            startbyte = 0x1e
                            for contentTag in contentTags.values():
                                value = contentTag.setvaluebytearray(openiotmessage[startbyte:startbyte+contentTag.length])
                                startbyte = startbyte + contentTag.length
                                print("%s %s: %s" % (datetime.datetime.fromtimestamp(timestamp/1000.0), contentTag.Name, contentTag.value))
                                
            
            sleep(0.01)
                
    except KeyboardInterrupt:        
        print("KeyboardInterrupt")
    finally:
        client_socket.close()
        print("socket closed")

