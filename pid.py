from time import sleep


class PID:
    """
    PID制御をする際の数値計算をするクラスです。
    """

    def __init__(self, gain, dt, target):
        self.prev = 0
        self.curr = 0
        self.sum = 0
        self.kp, self.ki, self.kd = gain
        self.dt = dt
        self.target = target
        self.is_first = True

    def calc(self, val):
        self.calc_curr(val)
        return self.calc_prop() + self.calc_intg() + self.calc_diff()

    def calc_curr(self, curr):
        self.curr = self.target - curr

    def calc_prop(self):
        return self.curr * self.kp

    def calc_intg(self):
        self.sum += self.curr
        return self.sum * self.ki * self.dt

    def calc_diff(self):
        if self.is_first:
            self.is_first = False
            return 0
        diff = self.curr - self.prev
        self.prev = self.curr
        return diff * self.kd / self.dt


if __name__ == "__main__":
    import math
    dt = .1
    pid = PID((.5, 0, .1), 1, 0)
    val = 1
    amp = 1
    for i in range(63):
        ctrl = pid.calc(val)
        val = math.sin()
        print("target->{0}, ctrl->{1}, val->{2}".format(pid.target, ctrl, val))
        sleep(dt)
