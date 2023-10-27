import time
from time import sleep
from pico.common.cinputreader import CInputReader

#supported function imports
from pico.common.functions.linearequation import LinearEquation
from pico.common.functions.blinkcounter import BlinkCounter

class CProcessThread:
    def __init__(self, device):
        self.device = device
        #self.contentTags = contentTags
        self.running = False
        self.ended = True
        self.inputReader = None
        self.readFrequency = 0
        
        #supported function lists
        self.linearEquations = []
        self.blinkCounters  = []
        
        inputReaderHierachies = device.deviceHierarchy.GetChildrenByFeature("ThingType", "InputReader")
        if(inputReaderHierachies != None and len(inputReaderHierachies) == 1):
            self.inputReader = CInputReader(inputReaderHierachies[0], device.contentTags)
            if(self.inputReader.readFrequency > 0 and (self.readFrequency == 0 or self.inputReader.readFrequency < self.readFrequency)):
                self.readFrequency = self.inputReader.readFrequency
                
        functionHierarchies = device.deviceHierarchy.GetChildrenByFeature("ThingType", "Function")
        for functionHierarchy in functionHierarchies:
            functionType = functionHierarchy.GetFeature("FunctionType")
            if(functionType != None):
                moduleName = functionType.Value.lower()
                if(moduleName == "linearequation"): 
                    linearEquation = LinearEquation(functionHierarchy, device.contentTags)
                    self.linearEquations.append(linearEquation)
                elif(moduleName == "blinkcounter"):
                    blinkCounter = BlinkCounter(functionHierarchy, device.contentTags)
                    self.blinkCounters.append(blinkCounter)
                    
        
        print("CProcessThread %s" % self.device.name)
        
    def start(self):
        print("CProcessThread start")
        
        if(self.inputReader != None):  
            self.running = True
            print("CProcessThread cycle time: %i" % self.readFrequency)
            self.ended = False
            
            while self.running:
                if(self.readFrequency > 0): 

                    startTimestamp = time.ticks_ms() #int(time.time() * 1000) #
                    self.inputReader.read()
                    
                    for linearEquation in self.linearEquations:
                        linearEquation.calculate()
                    
                    for blinkCounter in self.blinkCounters:
                        blinkCounter.calculate()
                        
                        
                    
                    endTimestamp = time.ticks_ms() #int(time.time() * 1000) #
                    difference = (endTimestamp - startTimestamp)
                    sleeptime = self.readFrequency - difference
                    if(sleeptime>0):
                        sleep(sleeptime / 1000)            
            
        else:
            print("CInputReader ReadFrequency is zero or less")
            
        print("CProcessThread %s process loop ended" % self.device.name)
        self.ended = True
        
        
        
    def stop(self):
        print("CProcessThread stop")
        self.running = False
        
#         while self.ended == False:
#             print("wait until process loop is ended...")
#             sleep(1)
