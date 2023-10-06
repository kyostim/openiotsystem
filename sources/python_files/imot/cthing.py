class CThing:
    def __init__(self,thingName, thingUUID):
        self.Name = thingName
        self.ThingUUID = thingUUID
        self.Features = []

    def GetFeature(self, name, value = None):
        if(value == None):
            for feature in self.Features:
                if feature.Name == name:
                    return feature
        else:
            for feature in self.Features:
                if feature.Name == name and feature.Value == value:
                    return feature
        return None