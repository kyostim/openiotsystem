import machine
import struct
from machine import Pin

class CContentTag:
    def __init__(self, hierarchy):
        self.thing = hierarchy.Thing
        self.Name = ""
        self.length = 0
        self.gppin = -1
        self.value = None
        self.endianess = '<'
        self.tagType = ""
        self.Pin = None
        
        if(self.thing != None):
            self.Name = self.thing.Name
            valueType = self.thing.GetFeature("Value")
            print(self.thing.Name)
            
            if(valueType != None):
                self.valuetype = valueType.Type.lower()
                print("    Value(%s): %s" % (valueType.Type, valueType.Value))
            else:
                print("ContentTag has not Value Feature")
                
            endianess = self.thing.GetFeature("Endianness")
            if(endianess != None):
                print("    Endianness(%s): %s" % (endianess.Type, endianess.Value))
                if(endianess.Value.lower()=="big"):
                    self.endianess = '>'
            else:
                print("ContentTag has not Endianness Feature")
                
            length = self.thing.GetFeature("Length") 
            if(length != None):
                self.length = int(length.Value)
                print("    Endianness(%s): %s" % (length.Type, length.Value))
            else:
                print("ContentTag has not Length Feature")
               
            #optional features
            gppin = self.thing.GetFeature("PicoGPPin")
            if(gppin != None):
                self.gppin = int(gppin.Value)
                print("    PicoGPPin(%s): %s" % (gppin.Type, gppin.Value))
                
            tagtype = self.thing.GetFeature("TagType")
            if(tagtype != None):
                self.tagType = tagtype.Value
                print("    TagType(%s): %s" % (tagtype.Type, tagtype.Value))
        else:
            print('ContentTag Hierarchy has not connection between Thing')
            
        if(self.tagType == "Analog" and self.gppin >= 0):
            self.Pin = machine.ADC(self.gppin)
    
    def valuebytearray(self):
        valuebytearray=bytearray(self.length)
        if(self.value != None):
            if(self.valuetype == 'uint16'):
                valuebytearray = bytearray(struct.pack('%sH' % self.endianess, self.value))
            elif(self.valuetype == 'float32'):
                valuebytearray = bytearray(struct.pack('%sf'% self.endianess, self.value))
        
        return valuebytearray
    
    
    def read(self):
        if(self.Pin != None and self.tagType == "Analog"):
            self.value = self.Pin.read_u16()
        
 
