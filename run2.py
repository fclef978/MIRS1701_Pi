import math
from pid import PID


class Run():
    RADIUS = 40  # MIRSのタイヤ間の距離[cm]
    USS_RADIUS = 19
    USS_DIST = 30  # MIRSの中心から超音波センサまでの距離[cm]
    USS_DIFF = 6
    Kp = 0.4
    Ki = 0.01
    Kd = 0
    TARGET_DIST = 50  # 目標となる壁との距離[m]
    INTERVAL = 0.01  # 制御周期[s]
    USS_DICT_LIST = ["f", "sf", "s", "sb", "b"]

    def __init__(self):
        self.isLeft = True
        self.vel_left_sum = 0
        self.vel_right_sum = 0
        self.uss = {}
        self.speed = 20
        self.cmd_prev = []
        self.pid = PID((Run.Kp, Run.Ki, Run.Kd), 0.1, Run.TARGET_DIST)
        self.pid_th = PID((0.3, 0, 0), 0.1, 0)

    def set_val(self, is_left, uss):
        self.isLeft = is_left
        self.uss["f"] = uss[0]
        self.uss["b"] = uss[4]
        if self.isLeft:
            self.uss["sf"] = uss[7]
            self.uss["s"] = uss[6]
            self.uss["sb"] = uss[5]
        else:
            self.uss["sf"] = uss[1]
            self.uss["s"] = uss[2]
            self.uss["sb"] = uss[3]

    def straight(self):
        speed_mod = self.pid.calc(self.calc_dist())  # 近いと正、遠いと負
        agl = self.calc_angle()
        speed_mod -= self.pid_th.calc(agl)
        if (agl >= 10 and speed_mod < 0) or (agl <= -10 and speed_mod > 0):
            speed_mod = 0
        speed_mod = int(speed_mod)
        speed_l, speed_r = self.speed + speed_mod, self.speed - speed_mod
        return [["velocity", speed_l, speed_r]]

    def is_duplicate_cmd(self, cmd):
        if self.cmd_prev == cmd:
            return cmd
        else:
            return []
        
    def calc_ratio(self):
        front = self.uss["sf"]
        back = self.uss["sb"]
        tmp = ((back - front) / Run.USS_DIST) ** 2.0
        return (tmp + 1) ** -0.5
        
    def calc_angle(self):
        front = self.uss["sf"]
        back = self.uss["sb"]
        tmp = math.acos(self.calc_ratio())
        if (self.isLeft and front > back) or (not self.isLeft and back > front):
            tmp *= -1
        return math.degrees(tmp)
        
    def calc_dist(self):
        tmp = self.calc_ratio()
        return tmp * (self.uss["s"] + Run.USS_RADIUS)
    
