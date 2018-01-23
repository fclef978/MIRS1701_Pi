class State:

    def __init__(self):
        self.state = "init"
        self.uss = {}
        self.sns = {}

    def judge(self):
        self.__getattribute__(self.state)()

    def init(self):
        self.state = "normal"

    def normal(self):
        if self.uss["a"] < 2:
            self.state = "avoid"
        elif self.uss["a"] < 4:
            self.state = "change"
        elif self.uss["a"] < 8:
            self.state = "turn"

    def avoid(self):
        self.state = "normal"

    def change(self):
        self.state = "normal"

    def turn(self):
        self.state = "normal"

if __name__ == "__main__":
    s = State()
    for i in range(10):
        s.uss["a"] = i
        s.judge()
        print(i, s.state)
