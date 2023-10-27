class CHierarchy:
    def __init__(self, hierarchyName, hierarchyUUID, parentUUID, thingUUID, order, things):
        self.Name = hierarchyName
        self.HierarchyUUID = hierarchyUUID
        self.Thing = None
        self.Children = []
        self.Parent = None
        self.Order = order
        
        for thing in things:
            if(thing.ThingUUID == thingUUID):
                self.Thing = thing
                break
                
    def GetChildrenByFeature(self, featureName, featureValue):
        children = []

        for child in self.Children:
            if(child.Thing != None):
                featureExists = child.Thing.GetFeature(featureName, featureValue)
                if( featureExists != None):
                    children.append(child)

            childChildren = child.GetChildrenByFeature(featureName, featureValue)
            for childChild in childChildren:
                children.append(childChild)            

        return children;

    def GetParentByFeature(self, featureName, featureValue):
        parent = None

        if(self.Parent != None and self.Parent.Thing != None):
            featureExists = self.Parent.Thing.GetFeature(featureName, featureValue)
            if( featureExists != None):
                parent = self.Parent
            else:
                parent = self.Parent.GetParentByFeature(featureName, featureValue)

        return parent
    
    def GetFeature(self, name, value = None):
        feature = None
        if(self.Thing != None):
            feature = self.Thing.GetFeature(name, value)
            
        return feature
      

      



