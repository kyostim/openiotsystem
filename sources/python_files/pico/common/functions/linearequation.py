from time import sleep
from pico.common.ccontenttag import CContentTag

class LinearEquation:
    def __init__(self, linearEquationHierarchy, contentTags):
        self.linearEquationHierarchy = linearEquationHierarchy
        self.contentTags = contentTags
        print("LinearEquation: %s" % self.linearEquationHierarchy.Name)
        
        #y=coefficient*x + constant
        self.coefficient = None
        self.constant = None
        self.xContentTag = None
        self.resultTag = None
        
        coefficient = self.linearEquationHierarchy.GetFeature("Coefficient")
        constant = self.linearEquationHierarchy.GetFeature("Constant")
        if(coefficient != None and constant != None):
            self.coefficient = float(coefficient.Value)
            self.constant = float(constant.Value)
            
            sourceHierarchies = self.linearEquationHierarchy.GetChildrenByFeature("ThingType", "Source")
            if(len(sourceHierarchies) == 1):
                sourceContentTagHierarchies = sourceHierarchies[0].GetChildrenByFeature("ThingType", "ContentTag")
                if(len(sourceContentTagHierarchies) == 1):
                    xThing = sourceContentTagHierarchies[0].Thing
                    if(xThing != None):
                        if(xThing.ThingUUID in self.contentTags):
                            self.xContentTag = self.contentTags[xThing.ThingUUID]
                            print("    %f %f %s" % (self.coefficient, self.constant, self.xContentTag.Name))                            
                else:
                    print("Linear equation accepts only one source ContentTag")
            else:
                print("Linear equation accepts only one source folder")
                
            
            sinkHierarchies = self.linearEquationHierarchy.GetChildrenByFeature("ThingType", "Sink")
            if(len(sinkHierarchies) == 1):
                sinkContentTagHierarchies = sinkHierarchies[0].GetChildrenByFeature("ThingType", "ContentTag")
                if(len(sinkContentTagHierarchies) == 1):
                    if(sinkContentTagHierarchies[0].Thing != None):
                        if(sinkContentTagHierarchies[0].Thing.ThingUUID in self.contentTags):
                            self.resultTag = self.contentTags[sinkContentTagHierarchies[0].Thing.ThingUUID]
                            print("    LinearEquation ResultTag: %s" % self.resultTag.Name)
                
        else:
            print("LinearEquation function has not Coefficient or Constant feature")
            
            
    def calculate(self):
        if(self.resultTag != None and self.coefficient != None and self.constant != None and self.xContentTag != None and self.xContentTag.value != None):
            self.resultTag.value = float((self.coefficient * float(self.xContentTag.value)) + self.constant)  #y=coefficient*x + constant
        