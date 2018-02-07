# バッテリー管理クラス


class BatteryVoltageDiffError(Exception):

    def __init__(self, diff, a, b):
        self.diff = diff
        self.a = a
        self.b = b

    def __str__(self):
        return """
        Battery Voltage Difference is {0}V. A = {1}V, B = {2}V.
        It is Dangerous because it is more than 1.0V!!
        This robot cannot start...
        """.format(self.diff, self.a, self.b)


class Battery:
    """
    バッテリー管理モジュールです。
    電源電圧を監視し、常に適切な方のバッテリーに切り替えます。
    """

    ACCEPTABLE_DIFF = 0.3

    def __init__(self, a, b):
        self.set_values(a, b)
        # if self.diff > 1.0:
        #     raise BatteryVoltageDiffError(self.diff, a, b)
        self.isAOn = False
        self.isBOn = False
        self.isInit = True
        print("A{0}V, B{1}V".format(a, b))

    def generate_command(self, a, b):
        self.set_values(a, b)
        cmd = []
        tmp = self.judge()
        if tmp is not None:
            (a, b) = tmp
            if a:
                cmd.append(["Battery", 1, 0])
            elif b:
                cmd.append(["Battery", 0, 1])
        return cmd

    def judge(self):
        if self.isInit:
            self.isInit = False
            if self.is_a_high():
                self.isAOn = True
                return (True, False)
            else:
                self.isBOn = True
                return (False, True)

        if self.isAOn:
            if self.is_a_high():
                return None
            elif self.diff > Battery.ACCEPTABLE_DIFF:
                self.isBOn = True
                return (False, True)
        elif self.isBOn:
            if not self.is_a_high():
                return None
            elif self.diff > Battery.ACCEPTABLE_DIFF:
                self.isAOn = True
                return (True, False)
        return None

    def set_values(self, a, b):
        self.a = a
        self.b = b
        self.diff = self.calc_volt_diff()

    def is_a_high(self):
        return self.a > self.b

    def calc_volt_diff(self):
        return abs(self.a - self.b)

if __name__ == "__main__":
    b = Battery(8.0, 8.2)
    print(b.generate_command(8.0, 8.2))
    print(b.generate_command(8.0, 7.8))
    print(b.generate_command(8.0, 7.6))
    print(b.generate_command(7.2, 7.6))
    print(b.diff)
