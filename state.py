class State:

    def __init__(self, data):
        self.state = "straight"
        self.data = data

    def judge(self):
        self.__getattribute__(self.state)()

    def init(self):
        self.state = "straight"

    def straight(self):
        if self.data.uss["sf"] > 100:
            self.state = "turn"
        if self.data.is_left and self.data.ard["jsX"] < 100:  # 左壁右入力
            self.state = "change"
        if not self.data.is_left and self.data.ard["jsX"] > 900:  # 右壁左入力
            self.state = "change"
        if self.data.uss["f"] < 100:
            self.state = "avoid"

    def avoid(self):
        if self.data.uss["f"] > 100:
            self.state = "straight"

    def change(self):
        self.state = "straight"

    def turn(self):
        self.state = "straight"
