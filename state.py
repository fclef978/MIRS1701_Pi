class State:
    FRONT_INPUT_VALUE = 100
    BACK_INPUT_VALUE = 900
    LEFT_INPUT_VALUE = 900
    RIGHT_INPUT_VALUE = 100


    def __init__(self, data):
        self.state = "init"
        self.data = data
        self.is_changed = False
        self.expected = "straight"

    def judge(self):
        prev = self.state
        self.__getattribute__(self.state)()
        if not prev == self.state:
            self.prev = prev
            self.is_changed = True

    def init(self):
        if self.data.ard["jsY"] < 100:
            self.state = "straight"

    def straight(self):
        if self.data.uss["sf"] > 150:
            self.state = "wait"
            self.expected = "turn"
        if self.data.is_left and self.data.ard["jsX"] < 100:  # 左壁右入力
            self.state = "change"
        if not self.data.is_left and self.data.ard["jsX"] > 900:  # 右壁左入力
            self.state = "change"
        if self.data.uss["f"] < 40:
            self.state = "wait"
            self.expected = "avoid"
        if self.data.ard["jsY"] < 900:
            self.state = "wait"
            self.expected = "straight"

    def wait(self):
        if self.expected == "turn":
            if self.data.is_left and self.data.ard["jsX"] > 900:
                self.state = "turn"
        else:
            self.state = self.expected


    def avoid(self):
        if self.data.uss["f"] > 40:
            self.state = "straight"

    def change(self):
        self.state = "straight"

    def turn(self):
        self.state = "straight"
