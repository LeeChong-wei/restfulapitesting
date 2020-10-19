class field_info:
    def __init__(self,field_name,require,default,fuzz,location):
        self.field_name = field_name
        self.require = require
        self.default = default
        self.fuzz = fuzz
        self.location = location