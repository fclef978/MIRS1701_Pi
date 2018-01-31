import math
from pid import PID
from state import State
from sound import Sound


class Run():
    RADIUS = 40  # MIRSのタイヤ間の距離[cm]
    USS_RADIUS = 19
    USS_DIST = 30  # MIRSの中心から超音波センサまでの距離[cm]
    USS_DIFF = 6
    TARGET_DIST = 60  # 目標となる壁との距離[m]
    INTERVAL = 0.01  # 制御周期[s]
    USS_DICT_LIST = ["f", "sf", "s", "sb"]
    sound = Sound()

    def __init__(self, data):
        self.data = data
        self.cmd_prev = []
        self.state = State(data)
        self.straight = Straight(data)
        self.turn = Turn(data)
        self.avoid = Avoid(data)
        self.init = Init(data)
        self.wait = Wait(data)
        self.state_prev = self.state.state

    def execute(self):
        self.data.state = self.state.state
        self.data.prev = self.state.prev
        self.data.expected = self.state.expected
        cmds = []
        cmds += self.run()
        return cmds

    def run(self):
        tmp = self.__getattribute__(self.state.state)
        cmd = tmp.generate_command()
        if tmp.is_terminate:
            self.state.judge()
        if self.state.state == "change":
            print(self.data.ard)
        print(self.state.prev, self.state.state, self.state.expected)
        if self.state.is_changed:
            self.__getattribute__(self.state_prev).reset()
            self.state.is_changed = False
        self.state_prev = self.state.state
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

    @staticmethod
    def limit(tgt, u, l):
        if tgt > u:
            tgt = u
        if tgt < l:
            tgt = l
        return tgt


class Travel:
    """
    走行系の親クラス
    """
    def __init__(self, data):
        self.data = data
        self.is_terminate = False
        self.count = 0

    def generate_command(self):
        self.count += 1
        return []

    def is_arduino_stop(self):
        if self.data.ard["mode"] == 0:
            return True
        else:
            return False

    def reset(self):
        self.is_terminate = False
        self.count = 0


class Init(Travel):
    """
    初期状態
    """
    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True


class Straight(Travel):
    """
    壁追従制御
    """
    Kp = -1
    Ki = 0.0
    Kd = 0.0

    def __init__(self, data):
        Travel.__init__(self, data)
        self.pid_angle = PID((Straight.Kp, Straight.Ki, Straight.Kd), 0.1, Run.TARGET_DIST)
        self.pid_speed = PID((-0.4, 0, 0), 0.1, 0)
        self.speed = 40
        self.is_terminate = True

    def generate_command(self):
        x, th = Run.calc_pos(self.data.uss["sf"], self.data.uss["s"], self.data.uss["sb"], self.data.is_left)
        x = Run.limit(x, Run.TARGET_DIST + 10, Run.TARGET_DIST - 10)
        tgt_angle = self.pid_angle.calc(x)  # 近いと正、遠いと負
        self.pid_speed.target = tgt_angle
        speed_mod = self.pid_speed.calc(math.degrees(th))
        if (math.degrees(th) >= 10 and speed_mod < 0) or (math.degrees(th) <= -10 and speed_mod > 0):
            speed_mod = 0
        speed_mod = int(speed_mod)
        speed_mod = Run.limit(speed_mod, 5, -5)
        print(int(tgt_angle), speed_mod, int(math.degrees(th)), int(x))
        speed_l, speed_r = self.speed + speed_mod, self.speed - speed_mod
        self.is_terminate = True
        return [["velocity", speed_l, speed_r]]


class Wait(Travel):
    """
    曲がり角曲がる
    """
    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        Run.sound.talk("とまります")
        Run.sound.talk(self.wait_sound())
        return [["stop"]]

    def reset(self):
        Travel.reset(self)
        self.is_terminate = True

    def wait_sound(self):
        if self.data.expected == "turn":
            return "まがりかどです、まがるほうこうをにゅうりょくしてください"
        if self.data.expected == "straight":
            return "まえにたおすとちょくしんをさいかいします"
        if self.data.expected == "avoid":
            return "しょうがいぶつです、しょうがいぶつをかいひします"



class Turn(Travel):
    """
    曲がり角曲がる
    """
    def __init__(self, data):
        Travel.__init__(self, data)

    def generate_command(self):
        print("isast {0}".format(self.is_arduino_stop()))
        if self.count == 0:
            self.count += 1
            Run.sound.talk("まがります")
            return [["turn", 30, 90, Run.TARGET_DIST - 40, int(self.data.is_left)]]
        elif self.count == 10 and self.is_arduino_stop():
            self.count += 1
            Run.sound.talk("ちょくしんします")
            return [["straight", 50, 40]]
        elif self.is_arduino_stop() and self.count == 20:
            self.is_terminate = True
            return []
        elif self.is_arduino_stop():
            self.count += 1
            return []
        else:
            return []


class Avoid(Travel):
    """
    障害物回避
    """

    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        self.is_terminate = True
        if self.count == 0:
            self.count += 1
            return [["stop"]]
        else:
            return []
