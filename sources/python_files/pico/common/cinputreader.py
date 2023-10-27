from time import sleep
from pico.common.ccontenttag import CContentTag

class CInputReader:
    def __init__(self, inputreaderHierarchy, contentTags):
        self.inputreaderHierarchy = inputreaderHierarchy
        self.contentTags = contentTags
        self.inputTags = []
        self.readFrequency = 0
        print("Input reader: %s" % self.inputreaderHierarchy.Name)
        
        readFrequency = self.inputreaderHierarchy.GetFeature("ReadFrequency")
        if(readFrequency != None):
            self.readFrequency = int(readFrequency.Value)
            print("    ReadFrequency: %i" % self.readFrequency)
        else:
            print("    InputReader has not ReadFrequency Feature")
        
        self.contentTagHierarchies = self.inputreaderHierarchy.GetChildrenByFeature("ThingType", "ContentTag")
        for contentTagHierarchy in self.contentTagHierarchies:
            if(contentTagHierarchy.Thing != None and contentTagHierarchy.Thing.ThingUUID in self.contentTags):
                inputTag = self.contentTags[contentTagHierarchy.Thing.ThingUUID]
                if(inputTag.gppin >= 0 and inputTag.tagType == "Analog" or inputTag.tagType == "Digital"):
                    self.inputTags.append(inputTag) 
            
        
        
    def read(self):
        #print("CInputReader run")   
        for inputTag in self.inputTags:
            inputTag.read()
        #print("CInputReader ended")
        