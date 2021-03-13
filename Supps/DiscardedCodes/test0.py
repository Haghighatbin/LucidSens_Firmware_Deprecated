class drv8825:
    def __init__(self, m0, m1, m2):
        self.m0 = m0
        self.m1 = m1
        self.m2 = m2
    def printer(self):
        return(self.m0)

d = drv8825(14, 15, 18)
dd = d.printer()
print(dd)