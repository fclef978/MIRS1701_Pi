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
        self.prev = ""

    def judge(self):
        prev = self.state
        self.__getattribute__(self.state)()
        if not prev == self.state:
            self.prev = prev
            self.is_changed = True
        else:
            self.is_changed = False

    def init(self):
        if self.data.ard["jsY"] < 100:
            self.state = "straight"

    def straight(self):
        if self.data.uss["sf"] > 150:
            self.state = "wait"
            self.expected = "turn"
        elif self.data.is_left and self.data.ard["jsX"] < 100:  # 左壁右入力
            self.state = "change"
        elif not self.data.is_left and self.data.ard["jsX"] > 900:  # 右壁左入力
            self.state = "change"
        elif self.data.uss["f"] < 40:
            self.state = "wait"
            self.expected = "avoid"
        elif self.data.ard["jsY"] > 800:
            self.state = "wait"
            self.expected = "straight"

    def wait(self):
        if self.expected == "turn":
            if self.data.is_left and self.data.ard["jsX"] > 800:
                self.state = "turn"
        elif self.expected == "straight":
            if self.data.ard["jsY"] < 200:
                self.state = "straight"
        elif self.expected == "avoid":
            if self.data.ard["jsY"] < 200:
                self.state = "straight"
        else:
            self.state = self.expected

    def avoid(self):
        if self.data.uss["f"] > 40:
            self.state = "straight"

    def change(self):
        self.state = "straight"

    def turn(self):
        self.state = "straight"
