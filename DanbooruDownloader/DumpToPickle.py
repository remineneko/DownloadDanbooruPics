import pickle

class DumpToPickle:
    def __init__(self, filePath, data = None):
        self.path = filePath
        self.data = data

    def DumpToPickle(self):
        with open(self.path,'wb') as f:
            pickle.dump(self.data,f)

    def loadPickle(self):
        with open(self.path,'rb') as f:
            return pickle.load(f)