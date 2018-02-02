import math
from pid import PID
from sound import Sound
from state import State

sound = Sound()


class Run():
    RADIUS = 40  # MIRSのタイヤ間の距離[cm]
    USS_RADIUS = 19
    USS_DIST = 30  # MIRSの中心から超音波センサまでの距離[cm]
    USS_DIFF = 6
    TARGET_DIST = 60  # 目標となる壁との距離[m]
    INTERVAL = 0.01  # 制御周期[s]
    USS_DICT_LIST = ["f", "sf", "s", "sb"]
    
    def __init__(self, data):
        self.data = data
        self.cmd_prev = []
        self.state = State(data)
        self.straight = Straight(data)
        self.turn = Turn(data)
        self.cross = Cross(data)
        self.avoid = Avoid(data)
        self.init = Init(data)
        self.wait = Wait(data)
        self.help = Help(data)
        self.un_touch = Touch(data)
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
        sound.sperker_off()

    def generate_command(self):
        if self.count == 0:
            self.count += 1
            self.data.is_left = self.data.uss["os"] > self.data.uss["s"]
        return []


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
        self.dist_count = 0
        self.dist_prev = 0

    def generate_command(self):
        dist = (self.data.ard["distL"] + self.data.ard["distR"]) / 2
        if self.count == 0:
            self.count += 1
            sound.say_straight()
        if (dist % 500 < 10 or dist % 500 > 490) and dist > 10:
            if self.dist_prev + 20 < dist:
                self.dist_count += 1
                sound.say_dist(self.dist_count)
            self.dist_prev = dist
        x, th = Run.calc_pos(self.data.uss["sf"], self.data.uss["s"], self.data.uss["sb"], self.data.is_left)
        x = Run.limit(x, Run.TARGET_DIST + 10, Run.TARGET_DIST - 10)
        tgt_angle = self.pid_angle.calc(x)  # 近いと正、遠いと負
        self.pid_speed.target = tgt_angle
        speed_mod = self.pid_speed.calc(math.degrees(th))
        if (math.degrees(th) >= 10 and speed_mod < 0) or (math.degrees(th) <= -10 and speed_mod > 0):
            speed_mod = 0
        speed_mod = int(speed_mod)
        speed_mod = Run.limit(speed_mod, 5, -5)
        speed_l, speed_r = self.speed + speed_mod, self.speed - speed_mod
        self.is_terminate = True
        return [["velocity", speed_l, speed_r]]


class Wait(Travel):
    """
    待機
    走行を停止させ、入力を待ちます。
    """

    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        if self.count == 0:
            self.count += 1
            sound.sperker_off()
            if not (self.data.prev == "help" or self.data.prev == "un_touch"):
                sound.say_stop()
            return [["stop"]]
        elif self.count == 10:
            self.count += 1
            sound.say_wait(self.data.expected)
        else:
            self.count += 1
        return []

    def reset(self):
        Travel.reset(self)
        self.is_terminate = True


class Help(Travel):
    """
    救援要請
    走行を停止させ、救援要請を行います。
    """
    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        if self.count % 30 == 0:
            self.count += 1
            sound.sperker_on()
            sound.say_help()
            return [["stop"]]
        else:
            self.count += 1
        return []

    def reset(self):
        Travel.reset(self)
        self.is_terminate = True


class Touch(Travel):
    """
    ハーネスを話した時の動作
    走行を停止させ、ユーザーに通知します。
    """
    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        if self.count % 30 == 0:
            self.count += 1
            sound.sperker_on()
            sound.say_touch()
            return [["stop"]]
        else:
            self.count += 1
        return []

    def reset(self):
        Travel.reset(self)
        self.is_terminate = True


class Turn(Travel):
    """
    曲がり角曲がる
    90度旋回し、その後に壁との距離分直進します。
    """

    def __init__(self, data):
        Travel.__init__(self, data)

    def generate_command(self):
        print("isast {0}".format(self.is_arduino_stop()))
        if self.count == 0:
            self.count += 1
            sound.say_turn()
            return [["turn", 30, 90, Run.TARGET_DIST - 40, int(self.data.is_left)]]
        elif self.count == 10 and self.is_arduino_stop():
            self.count += 1
            sound.say_straight()
            return [["straight", 30, 40]]
        elif self.is_arduino_stop() and self.count == 20:
            self.is_terminate = True
            return []
        elif self.is_arduino_stop():
            self.count += 1
            return []
        else:
            return []


class Cross(Travel):
    """
    待機
    走行を停止させ、入力を待ちます。
    """

    def __init__(self, data):
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        if self.count == 0:
            self.count += 1
            sound.say_straight()
        return [["velocity", 30, 30]]


    def reset(self):
        Travel.reset(self)
        self.is_terminate = True


class Avoid(Travel):
    """
    障害物回避
    よけれない
    """

    def __init__(self, data):
        Travel.__init__(self, data)
        # self.is_terminate = True


    def generate_command(self):
        self.is_terminate = True
        if self.count == 0:
            self.count += 1
            sound.say_straight()
            return [["stop"]]
        else:
            return []
    """

    def generate_command(self):
        if self.count == 0:
            self.count += 1
            sound.say_turn()
            return [["rotation", 30, 90, int(not self.data.is_left)]]  # 回転
        elif self.count == 10:
            self.count += 1
            self.is_terminate = True
            sound.say_straight()
            return [["straight", 30, 200]]  # 横が障害物を外れるまで直進
        elif self.count == 11 and self.data.step == 1:
            self.count += 1
            self.is_terminate = False
            sound.say_turn()
            return [["rotation", 30, 90, int(self.data.is_left)]]  # 横が障害物をはずれたら回転
        elif self.count == 20:
            self.count += 1
            self.is_terminate = True
            sound.say_straight()
            return [["straight", 30, 200]]  # 障害物を感知するまで直進
        elif self.count == 21 and self.data.step == 2:
            self.count += 1
            self.is_terminate = True
            sound.say_straight()
            return [["straight", 30, 200]]  # 横が障害物を外れるまで直進
        elif self.count == 22 and self.data.step == 3:
            self.count += 1
            self.is_terminate = False
            sound.say_turn()
            return [["rotation", 30, 90, int(self.data.is_left)]]  # 横が障害物をはずれたら回転
        elif self.count == 30:
            self.count += 1
            self.is_terminate = True
            sound.say_straight()
            return [["straight", 30, 200]]  # 正面に壁が現れるれるまで直進
        elif self.count == 31 and self.data.step == 4:
            self.count += 1
            self.is_terminate = False
            sound.say_turn()
            return [["rotation", 30, 90, int(not self.data.is_left)]]  # 回転して直進に戻る
        elif self.is_arduino_stop():
            self.count += 1
            return []
        else:
            return []
        """
