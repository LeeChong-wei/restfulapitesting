class node:
    def __init__(self,id,name,label):
        self.name =name
        self.label =label
        self.id = id
    def __repr__(self):
        return repr((self.name, self.label,self.id))