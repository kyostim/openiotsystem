from time import sleep
from pico.common.ccontenttag import CContentTag

class BlinkCounter:
    def __init__(self, blinkCounterHierarchy, contentTags):
        self.blinkCounterHierarchy = blinkCounterHierarchy
        self.contentTags = contentTags
        print("BlinkCounter: %s" % self.blinkCounterHierarchy.Name)
        
        self.adcContentTag = None
        self.delta = 0
        self.n = 0
        self.resultTag = None
        self.values = []
        self.valuesSum = 0
        self.reducers = []
        self.reducersSum = 0
        self.blink = False
        self.counter = 0
        self.maxDelta = 0
        self.minDelta = 0
        
        delta = self.blinkCounterHierarchy.GetFeature("Delta")
        if(delta != None):
            self.delta = int(delta.Value)
        else:
            print("   Cannot find Delta feature")
            
        n = self.blinkCounterHierarchy.GetFeature("N")
        if(n != None):
            self.n = int(n.Value)
        else:
            print("   Cannot find N feature")
            
        if(self.delta > 0 and self.n > 0):
            sourceHierarchies = self.blinkCounterHierarchy.GetChildrenByFeature("ThingType", "Source")
            if(len(sourceHierarchies) == 1):
                sourceContentTagHierarchies = sourceHierarchies[0].GetChildrenByFeature("ThingType", "ContentTag")
                if(len(sourceContentTagHierarchies) == 1):
                    xThing = sourceContentTagHierarchies[0].Thing
                    if(xThing != None):
                        if(xThing.ThingUUID in self.contentTags):
                            self.adcContentTag = self.contentTags[xThing.ThingUUID]
                            print("    %i %i %s" % (self.delta, self.n, self.adcContentTag.Name))                            
                else:
                    print("Blink counter accepts only one source ContentTag")
            else:
                print("Blink counter accepts only one source folder")
                
            
            sinkHierarchies = self.blinkCounterHierarchy.GetChildrenByFeature("ThingType", "Sink")
            if(len(sinkHierarchies) == 1):
                sinkContentTagHierarchies = sinkHierarchies[0].GetChildrenByFeature("ThingType", "ContentTag")
                if(len(sinkContentTagHierarchies) == 1):
                    if(sinkContentTagHierarchies[0].Thing != None):
                        if(sinkContentTagHierarchies[0].Thing.ThingUUID in self.contentTags):
                            self.resultTag = self.contentTags[sinkContentTagHierarchies[0].Thing.ThingUUID]
                            print("    BlinkCounter ResultTag: %s" % self.resultTag.Name)
            
        
        
    def calculate(self):
        if(self.resultTag != None and self.delta != None and self.n != None and self.adcContentTag != None and self.adcContentTag.value != None):
            if(self.n > 0):
                value = int(self.adcContentTag.value)
                self.values.append(value)
                self.valuesSum = self.valuesSum + value
                if(len(self.values) > self.n):
                    self.reducers.append(self.values[0])
                    self.reducersSum = self.reducersSum + self.values[0]
                    self.valuesSum = self.valuesSum - self.values[0]
                    self.values.pop(0)
                    
                if(len(self.reducers) > self.n):
                    self.reducersSum = self.reducersSum - self.reducers[0]
                    self.reducers.pop(0)
                    
                    valueAverage = self.valuesSum / len(self.values)
                    reducersAverage = self.reducersSum / len(self.reducers)
                    
                    calculatedDelta = int(valueAverage - reducersAverage)
                    if(calculatedDelta > self.maxDelta):
                        self.maxDelta = calculatedDelta
                    if(calculatedDelta < self.minDelta):
                        self.minDelta = calculatedDelta
                    
                    if(self.blink == False and calculatedDelta > self.delta):
                        self.blink = True
                    elif(self.blink == True and calculatedDelta < -self.delta):
                        self.blink = False
                        self.counter = self.counter + 1
                        self.resultTag.value = self.counter
                        
                