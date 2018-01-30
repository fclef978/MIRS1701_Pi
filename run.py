import math
from pid import PID
from state import State
from sound import Sound


class Run():
    RADIUS = 40  # MIRSのタイヤ間の距離[cm]
    USS_RADIUS = 19
    USS_DIST = 30  # MIRSの中心から超音波センサまでの距離[cm]
    USS_DIFF = 6
    TARGET_DIST = 50  # 目標となる壁との距離[m]
    INTERVAL = 0.01  # 制御周期[s]
    USS_DICT_LIST = ["f", "sf", "s", "sb"]

    def __init__(self, data):
        self.data = data
        self.cmd_prev = []
        self.state = State(data)
        self.straight = Straight(data)
        self.turn = Turn(data)
        self.sound = Sound()

    def execute(self):
        cmds = []
        cmds += self.run()
        return cmds

    def run(self):
        tmp = self.__getattribute__(self.state.state)
        cmd = tmp.generate_command()
        if tmp.is_terminate:
            self.state.judge()
        return cmd

    def is_duplicate_cmd(self, cmd):
        if self.cmd_prev == cmd:
            return cmd
        else:
            return []

    @staticmethod
    def calc_pos(sf, s, sb, is_left):
        ratio = (((sb - sf) / Run.USS_DIST) ** 2.0 + 1) ** -0.5
        th = math.acos(ratio)
        if (is_left and sf > sb) or (not is_left and sb > sf):
            th *= -1
        x = ratio * (s + Run.USS_RADIUS)
        return x, th


class Travel:
    """
    走行系の親クラス
    """
    def __init__(self, data):
        self.data = data
        self.is_left = True
        self.is_terminate = False
        self.count = 0

    def generate_command(self):
        self.count += 1

    def is_arduino_stop(self):
        if self.data.ard["mode"] == 0:
            return True
        else:
            return False


class Straight(Travel):
    """
    壁追従制御
    """
    Kp = 0.3
    Ki = 0
    Kd = 0

    def __init__(self, data):
        Travel.__init__(self, data)
        self.pid = PID((Straight.Kp, Straight.Ki, Straight.Kd), 0.1, Run.TARGET_DIST)
        self.pid_th = PID((0.3, 0, 0), 0.1, 0)
        self.speed = 20
        self.is_terminate = True

    def generate_command(self):
        x, th = Run.calc_pos(self.data.uss["sf"], self.data.uss["s"], self.data.uss["sb"], self.is_left)
        speed_mod = self.pid.calc(x)  # 近いと正、遠いと負
        speed_mod -= self.pid_th.calc(th)
        if (th >= 10 and speed_mod < 0) or (th <= -10 and speed_mod > 0):
            speed_mod = 0
        speed_mod = int(speed_mod)
        speed_l, speed_r = self.speed + speed_mod, self.speed - speed_mod
        return [["velocity", speed_l, speed_r]]


class Turn(Travel):
    """
    曲がり角曲がる
    """
    def __init__(self, data):
        Travel.__init__(self, data)

    def generate_command(self):
        if self.count == 0:
            self.count += 1
            return [["turn", 30, 90, Run.TARGET_DIST, int(self.data.is_left)]]
        elif self.is_arduino_stop():
            self.is_terminate = True
            return []
        else:
            return []
