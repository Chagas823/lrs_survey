class Signature:
    def __init__(self, y0, s_values, c_values):
        self.y0 = y0
        self.s_values = s_values
        self.c_values = c_values
    def get(self):
        return self.y0,self.s_values,self.c_values