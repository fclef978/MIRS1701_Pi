class DataBox:
    """
    受信したデータを格納するクラスです。
    """

    def __init__(self):
        self.uss = {}
        self.ard = {}
        self.is_left = True
        self.state = "init"
        self.expected = "straight"
        self.prev = ""

    def set_value(self, uss, ard, is_left):
        self.is_left = is_left
        self.deside_uss_dir(uss)
        self.ard = ard

    def deside_uss_dir(self, uss):
        self.uss["f"] = uss[0]
        self.uss["b"] = uss[4]
        if self.is_left:
            self.uss["sf"] = uss[7]
            self.uss["s"] = uss[6]
            self.uss["sb"] = uss[5]
            self.uss["os"] = uss[2]
        else:
            self.uss["sf"] = uss[1]
            self.uss["s"] = uss[2]
            self.uss["sb"] = uss[3]
            self.uss["os"] = uss[6]
