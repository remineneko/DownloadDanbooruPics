import json

class DumpToJSON:
    def __init__(self,filePath,data = None):
        self.data = data
        self.path = filePath

    def DumpToJSON(self):
        with open(self.path, 'w') as file:
            json.dump(self.data, file, default=str)

    def loadJSON(self):
        with open(self.path,'r') as file:
            return json.load(file)


