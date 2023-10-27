from imot.chierarchy import CHierarchy
from imot.cthing import CThing
from imot.cfeature import CFeature

import os

class CIMoTParser:
    def __init__(self, xmlcontent):
        self.Hierarchies = [] 
        self.things = []
       
        thingsStart = xmlcontent.find("<things>") + 8
        thingsEnd = xmlcontent.find("</things>")
       
        if(thingsEnd > thingsStart):
            self.xmlThings = xmlcontent[thingsStart:thingsEnd]
            self.ParseThings()
            
        hierarchiesStart = xmlcontent.find("<hierarchies>") + 13;
        hierarchiesEnd = xmlcontent.find("</hierarchies>");

        if(hierarchiesEnd > hierarchiesStart):
            self.xmlHierarchies = xmlcontent[hierarchiesStart:hierarchiesEnd].strip();
            self.ParseHierarchies();
            
        print("CIMoTParser parsed %i hierarchies and %i things" % (len(self.Hierarchies), len(self.things)))
        
    def ParseHierarchies(self):
        hierarchyEnd = 0
        hierarchyStart = self.xmlHierarchies.find("<hierarchy ", hierarchyEnd) + 11
        
        while(hierarchyStart > 10):
            hierarchyEnd = self.xmlHierarchies.find("/>", hierarchyStart)
            if(hierarchyEnd > hierarchyStart):
                hierarchyContent = self.xmlHierarchies[hierarchyStart:hierarchyEnd].strip()
                hierarchyArguments = self.ParseArguments(hierarchyContent)
            
                hierarchyName = ""
                hierarchyUUID  = ""
                parentUUID = ""
                thingUUID = ""
                order = 0
                hidden = 0
                
                for i in range(len(hierarchyArguments)):
                    argumentParts = hierarchyArguments[i].split("=")
                    if(len(argumentParts) == 2):
                        if(argumentParts[0].strip() == "name"):
                            hierarchyName = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "hierarchyuuid"):
                            hierarchyUUID = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "parentuuid"):
                            parentUUID = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "thinguuid"):
                            thingUUID = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "order"):
                            order = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "hidden"):
                            if(argumentParts[1].strip() == 'true'):
                                hidden=1
                if(hidden==0):
                    hierarchy = CHierarchy(hierarchyName, hierarchyUUID, parentUUID, thingUUID, order, self.things)
                    self.Hierarchies.append(hierarchy)

                    for cHierarchy in self.Hierarchies:
                        if(cHierarchy.HierarchyUUID == parentUUID):
                            cHierarchy.Children.append(hierarchy)
                            hierarchy.Parent = cHierarchy

                hierarchyStart = self.xmlHierarchies.find("<hierarchy ", hierarchyEnd) + 11
            else:
               hierarchyStart = -1 
            
    def ParseThings(self):
        thingEnd = 0
        thingStart = self.xmlThings.find("<thing ", thingEnd) + 7
        
        while thingStart > 6:
            thingEnd = self.xmlThings.find(">", thingStart)
            if(thingEnd > thingStart):
                thingContent = self.xmlThings[thingStart:thingEnd]
                thingArguments = self.ParseArguments(thingContent)
                
                thingName = ""
                thingUUID = ""
                
                for i in range(len(thingArguments)):
                    argumentParts = thingArguments[i].split("=")
                    if(len(argumentParts) == 2):
                        if(argumentParts[0].strip() == "name"):
                            thingName = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "thinguuid"):
                            thingUUID = argumentParts[1].strip()
                            
                thing = CThing(thingName, thingUUID)
                
                thingTagEnd = self.xmlThings.find("</thing>", thingEnd)
                if(thingTagEnd > thingEnd):
                    xmlFeatures = (self.xmlThings[(thingEnd + 1):thingTagEnd]).strip();
                    thing.Features = self.ParseFeatures(xmlFeatures);
                    self.things.append(thing);

                    thingStart = self.xmlThings.find("<thing ", thingEnd) + 7;
                else:
                    thingStart = -1;
                               
    def ParseFeatures(self, xmlFeatures):
        features = []
        featureEnd = 0
        featureStart = xmlFeatures.find("<feature ", featureEnd) + 9
        while(featureStart > 8):
            featureEnd = xmlFeatures.find("/>", featureStart)
            if(featureEnd > featureStart):
                featureContent = xmlFeatures[featureStart:featureEnd].strip();
                featureArguments = self.ParseArguments(featureContent)
                
                featureName = ""
                featureType = ""
                featureValue = ""
                
                for i in range(len(featureArguments)):
                    argumentParts = featureArguments[i].split("=")
                    if(len(argumentParts) == 2):
                        if(argumentParts[0].strip() == "name"):
                            featureName = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "type"):
                            featureType = argumentParts[1].strip()
                        elif(argumentParts[0].strip() == "value"):
                            featureValue = argumentParts[1].strip()
                
                features.append(CFeature(featureName, featureType, featureValue))
                featureStart = xmlFeatures.find("<feature ", featureEnd) + 9
            else:
                featureStart = -1
        return features                   
                             
    def ParseArguments(self, argumentsText):
        arguments = []
        quatationMarkOpen = False
        start = 0
        for i in range(len(argumentsText)):
            if(argumentsText[i] == "\""):
                if(quatationMarkOpen):
                    arguments.append(argumentsText[start:i].replace("\"",""))
                    quatationMarkOpen = False
                    start = i + 1
                else:
                    quatationMarkOpen = True
        return arguments
    
    def GetHierarchyByHierarchyUUID(self, hierarchyUUID):
        hierarchy = None
        
        for cHierarchy in self.Hierarchies:
            if(cHierarchy.HierarchyUUID == hierarchyUUID):
                hierarchy = cHierarchy
                break
        
        return hierarchy
    
    def GetHierarchiesByFeature(self, featureName, featureValue):
        hierarchies = []

        for hierarchy in self.Hierarchies:
            if(hierarchy.Thing != None):
                featureExists = hierarchy.Thing.GetFeature(featureName, featureValue)
                if( featureExists != None):
                    hierarchies.append(hierarchy)
          

        return hierarchies;
          


