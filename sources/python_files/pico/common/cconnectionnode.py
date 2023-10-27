import uasyncio
import struct
import time
#from routputnode import ROutputNode
#from rcontenttag import RContentTag

class CConnectionNode:
    def __init__(self, loop, hierarchy, device):
        self.loop = loop
        self.hierarchy = hierarchy
        self.device = device
        self.outputnodes = []
        self.contenttags = []
        
        self.contentlength=0
        self.messagetypebytearray=bytearray(2)
        self.uuidbytearray=bytearray(16)
        self.lengthbytearray=bytearray(4)
        #self.messagebytearray=bytearray(22)
        
        self.updatefrequency = 1000
        self.outputport = -1
        self.maxclientcount = -1
        self.contenttype = ""
        self.heartbeatfrequency = -1
        self.protocol = ""
        
        self.floatingtimestamp=lastTimestamp = time.ticks_ms()
        
        
        if(self.device != None and self.hierarchy != None and self.hierarchy.Thing != None):
            print("CConnectionNode :%s" % self.hierarchy.Name)           
            
            updatefrequency = self.hierarchy.GetFeature("UpdateFrequency")
            if(updatefrequency != None):
                self.updatefrequency = int(updatefrequency.Value)
                print("    UpdateFrequency: %d" % self.updatefrequency)
                
            outputport = self.hierarchy.GetFeature("OutputPort")
            if(outputport != None):
                self.outputport = int(outputport.Value)
                print("    OutputPort: %d" % self.outputport)
            
            maxclientcount = self.hierarchy.GetFeature("MaxClientCount")
            if(maxclientcount != None):
                self.maxclientcount = int(maxclientcount.Value)
                print("    MaxClientCount: %d" % self.maxclientcount)
                
            contenttype = self.hierarchy.GetFeature("ContentType")
            if(contenttype != None):
                self.contenttype = contenttype.Value
                print("    ContentType: %s" % self.contenttype)
                
            heartbeatfrequency = self.hierarchy.GetFeature("HeartbeatFrequency")
            if(heartbeatfrequency != None):
                self.heartbeatfrequency = int(heartbeatfrequency.Value)
                print("    HeartbeatFrequency: %d" % self.heartbeatfrequency)
                
            protocol = self.hierarchy.GetFeature("Protocol")
            if(protocol != None):
                self.protocol = protocol.Value.lower()
                print("    Protocol: %s" % self.protocol)
                
            datagramhierarchies = self.hierarchy.GetChildrenByFeature("ThingType", "ContentBlock")
            if(datagramhierarchies != None and len(datagramhierarchies) == 1):
                contentTagHierarchies = datagramhierarchies[0].GetChildrenByFeature("ThingType", "ContentTag")
                startbyte=0
                for contentTagHierarchy in contentTagHierarchies:
                    if(contentTagHierarchy.Thing != None):
                        if(contentTagHierarchy.Thing.ThingUUID in self.device.contentTags):
                            #self.contenttaguuids.append(contentTagHierarchy.Thing.ThingUUID)
                            startbyte = startbyte + self.device.contentTags[contentTagHierarchy.Thing.ThingUUID].length
                            self.contenttags.append(self.device.contentTags[contentTagHierarchy.Thing.ThingUUID])
                            print("    ContentTag:%s" % self.device.contentTags[contentTagHierarchy.Thing.ThingUUID].Name)
                self.contentlength=startbyte                                
                            
               
            print(self.hierarchy.Thing.ThingUUID)   
            uuidParts = self.hierarchy.Thing.ThingUUID.split("-");
            if(len(uuidParts) == 5):
                self.messagetype=3
                messagetypebytearray = bytearray(2)
                messagetypebyte = struct.pack('<B', self.messagetype)
                messagetypebytearray[0:0]=messagetypebyte
                self.messagetypebytearray[:]=messagetypebytearray[0:2]
                print("messagetypebytearray len:%d" % len(self.messagetypebytearray))
                
                uuidbytearray = bytearray();
                uuidbytearray = self.reverseBytes(bytearray.fromhex(uuidParts[0]))
                uuidbytearray = uuidbytearray + self.reverseBytes(bytearray.fromhex(uuidParts[1]))
                uuidbytearray = uuidbytearray + self.reverseBytes(bytearray.fromhex(uuidParts[2]))
                uuidbytearray = uuidbytearray + bytearray.fromhex(uuidParts[3])
                uuidbytearray = uuidbytearray + bytearray.fromhex(uuidParts[4])
                self.uuidbytearray = uuidbytearray
                
                floatingTimestamp = time.ticks_ms()
                self.timestampbytearray = struct.pack('<q', floatingTimestamp)
                
                
                self.lengthbytearray = bytearray(struct.pack('<I', self.contentlength))
                self.messagelength = 30 + self.contentlength
                               
                print("messagesize:%d content size:%d" % (self.messagelength, self.contentlength))
                
                #self.loop.create_task(self.createdatagram())
                
            if(self.outputport > 0 and self.maxclientcount > 0 and self.protocol == "tcp"):
                self.loop.create_task(uasyncio.start_server(self.connection, "0.0.0.0", self.outputport, self.maxclientcount)) 
            
        else:
            print("hierarchy is None")
            
    async def connection(self, reader, writer):
        print('new connection')
       
        try:
            print("start")
            while True:
                try:
                    heartbeat = await uasyncio.wait_for(reader.readexactly(16), self.updatefrequency / 1000)
                    if(len(heartbeat) > 0):
                        print("heartbeat")
                except uasyncio.TimeoutError:
                    ok = 1
                finally:                    
                    #self.floatingtimestamp = self.floatingtimestamp + time.ticks_ms()
                    self.floatingtimestamp = time.ticks_ms()

                    messagebytearray = self.messagetypebytearray + self.uuidbytearray
                    messagebytearray = messagebytearray + struct.pack('<q', self.floatingtimestamp)
                    messagebytearray = messagebytearray + self.lengthbytearray
                    messagebytearray = messagebytearray + bytearray(self.contentlength)
                    
                    print("messagesize:%d" % (len(messagebytearray)))
                    startbyte=30
                    for contenttag in self.contenttags:
                        print("%s %s %s" % (contenttag.Name, contenttag.thing.ThingUUID, contenttag.value))
                        if(contenttag.value != None): 
                            
                            for i in range(contenttag.length):                            
                                valuearray=contenttag.valuebytearray()
                                index=startbyte+i
                                #print("%s index:%d i:%d" % (contenttag.thing.Name,index, i), valuearray)
                                
                                messagebytearray[index] = valuearray[i]
                            startbyte=startbyte+contenttag.length
                        
                    writer.write(messagebytearray)
                    print("sent: %d" % len(messagebytearray))
                    await writer.drain()           
                    
                        
        except Exception as e:            
            print("CConnectionNode exception: %s" % e)
        finally:
            writer.close()
            await writer.wait_closed()
            
    
        
                    
            
    def reverseBytes(self, byteArray):
        reversedByteArray = bytearray()
        for i in range(len(byteArray)-1,-1,-1):
            reversedByteArray.append(byteArray[i])
        return reversedByteArray