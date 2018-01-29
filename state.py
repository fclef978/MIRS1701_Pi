class State:

    def __init__(self):
        self.state = "init"
        self.uss = {}
        self.sns = {}
        self.isLeft = True

    def judge(self):
        self.__getattribute__(self.state)()

    def init(self):
        self.state = "straight"

    def straight(self):
        if self.uss["sf"] > 100:
            self.state = "turn"
        if self.isLeft and self.sns["jsX"] < 100: #左壁右入力
            self.state = "change"
        if not self.isLeft and self.sns["jsX"] > 900: #右壁左入力
            self.state = "change"
        
    def avoid(self):
        self.state = "straight"

    def change(self):
        self.state = "straight"

    def turn(self):
        self.state = "straight"

if __name__ == "__main__":
    s = State()
    for i in range(10):
        s.uss["a"] = i
        s.judge()
        print(i, s.state)
