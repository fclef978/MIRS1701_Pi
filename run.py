import math
from pid import PID
from sound import Sound
from state import State

sound = Sound()


class Run():
    """
    走行を制御するクラスです。
    """
    #: タイヤ間の距離[cm]を表す属性です。
    RADIUS = 40
    #: 超音波センサ間、sfとsbの間の距離[cm]を表す属性です。
    USS_RADIUS = 19
    #: MIRSの中心から超音波センサまでの距離[cm]を表す属性です。
    USS_DIST = 30
    #: 超音波センサのsf,sbとsとの飛び出ている距離の差[cm]を表す属性です。
    USS_DIFF = 6
    #: 目標となる壁との距離[m]を表す属性です。
    TARGET_DIST = 60
    #: 制御周期[s]を表す属性です。
    INTERVAL = 0.01
    #: ussのキーを表す属性です。
    USS_DICT_LIST = ["f", "sf", "s", "sb"]
    
    def __init__(self, data):
        """
        コンストラクタです。
        
        :param Databox data: Databoxのオブジェクト
        """
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
        """
        コマンドを生成します。
        
        :return list cmds: Arduinoに送るコマンド
        """
        self.data.state = self.state.state
        self.data.prev = self.state.prev
        self.data.expected = self.state.expected
        cmds = []
        cmds += self.run()
        return cmds

    def run(self):
        """
        走行値を生成します。今の状態により、各種生成用メソッドを呼び出します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
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
        """
        
        """
        if self.cmd_prev == cmd:
            return cmd
        else:
            return []

    @staticmethod
    def calc_pos(sf, s, sb, is_left):
        """
        自己位置を計算します。
        
        :param int sf: MIRSの横の前の超音波センサの値
        :param int s: MIRSの真横の超音波センサの値
        :param int sb: MIRSの横の後ろの超音波センサの値
        :param boolean is_left: 左壁かどうか
        :return tuple: 距離x、角度th
        """
        ratio = (((sb - sf) / Run.USS_DIST) ** 2.0 + 1) ** -0.5
        th = math.acos(ratio)
        if (is_left and sf > sb) or (not is_left and sb > sf):
            th *= -1
        x = ratio * (s + Run.USS_RADIUS)
        return x, th

    @staticmethod
    def limit(tgt, u, l):
        """
        値が許容範囲に収めます。
        
        :param int tgt: 許容範囲に収めたい値
        :param int u: 上限値
        :param int l: 下限値
        :rtype: int
        :return: 許容範囲に収めた値
        """
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
        """
        コンストラクタです。
        
        :param Databox data: Databoxのオブジェクト
        """
        self.data = data
        self.is_terminate = False
        self.count = 0

    def generate_command(self):
        """
        コマンドを生成します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        self.count += 1
        return []

    def is_arduino_stop(self):
        """
        走行が停止しているかをArduinoからの値を元に判断します。
        
        :rtype: bool
        :return: 停止しているか
        """
        if self.data.ard["mode"] == 0:
            return True
        else:
            return False

    def reset(self):
        """
        カウントと終了フラグをリセットします。
        """
        self.is_terminate = False
        self.count = 0


class Init(Travel):
    """
    初期状態のクラスです。
    """

    def __init__(self, data):
        """
        コンストラクタです。スピーカーをオフにします。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        self.is_terminate = True
        sound.sperker_off()

    def generate_command(self):
        """
        コマンドを生成します。一度だけ左右の壁を判定してself.data.is_leftに格納します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        if self.count == 0:
            self.count += 1
            self.data.is_left = self.data.uss["os"] > self.data.uss["s"]
        return []


class Straight(Travel):
    """
    壁追従(直進)走行制御を行うクラスです。
    """
    #: Pゲインをを表す属性です。
    Kp = -1
    #: Iゲインをを表す属性です。
    Ki = 0.0
    #: Dゲインをを表す属性です。
    Kd = 0.0

    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        self.pid_angle = PID((Straight.Kp, Straight.Ki, Straight.Kd), 0.1, Run.TARGET_DIST)
        self.pid_speed = PID((-0.4, 0, 0), 0.1, 0)
        self.speed = 40
        self.is_terminate = True
        self.dist_count = 0
        self.dist_prev = 0
        self.correction_val = 1
        self.dist = 0

    def generate_command(self):
        """
        コマンドを生成し、5メートルごとに音声通知をします。
        既定走行値に補正値を加えます。
        
        :rtype: list
        :return: Arduinoへのコマンド。左右のタイヤの速度。
        """
        self.dist = (self.data.ard["distL"] + self.data.ard["distR"]) / 2
        if self.count == 0:
            self.count += 1
            if self.data.is_left:  # 壁による制御値の補正
                self.correction_val = 1
            else:
                self.correction_val = -1
            if not self.data.prev == "turn" or not self.data.prev == "cross":
                sound.say_straight()  # 直進音声
        if (self.dist % 500 < 10 or self.dist % 500 > 490) and self.dist > 10:
            if self.dist_prev + 20 < self.dist:
                self.dist_count += 1
                sound.say_dist(self.dist_count)  # 5メートルごとの音声
            self.dist_prev = self.dist
        x, th = Run.calc_pos(self.data.uss["sf"], self.data.uss["s"], self.data.uss["sb"], self.data.is_left)
        x = Run.limit(x, Run.TARGET_DIST + 10, Run.TARGET_DIST - 10)
        th *= self.correction_val
        tgt_angle = self.pid_angle.calc(x)  # 近いと正、遠いと負
        self.pid_speed.target = tgt_angle
        speed_mod = self.pid_speed.calc(math.degrees(th))
        if (math.degrees(th) >= 10 and speed_mod < 0) or (math.degrees(th) <= -10 and speed_mod > 0):
            speed_mod = 0
        speed_mod = int(speed_mod)
        speed_mod = Run.limit(speed_mod, 5, -5)
        speed_mod *= self.correction_val
        speed_l, speed_r = self.speed + speed_mod, self.speed - speed_mod
        self.is_terminate = True
        return [["velocity", speed_l, speed_r]]

    def reset(self):
        """
        各種値をリセットします。
        """
        Travel.reset(self)
        self.dist_prev = 0
        self.correction_val = 1
        self.dist = 0
        self.dist_count = 0


class Wait(Travel):
    """
    待機を行うクラスです。
    """

    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        """
        コマンドを生成し、待機音声を通知します。
        停止コマンドを生成します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
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
        """
        各種値をリセットします。
        """
        Travel.reset(self)
        self.is_terminate = True


class Help(Travel):
    """
    救援要請を行うクラスです。
    """
    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        """
        停止コマンドを生成し、一定時間ごと救援音声を流します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        if self.count % 30 == 0:
            self.count += 1
            sound.sperker_on()
            sound.say_help()
            return [["stop"]]
        else:
            self.count += 1
        return []

    def reset(self):
        """
        各種値をリセットします。
        """
        Travel.reset(self)
        self.is_terminate = True


class Touch(Travel):
    """
    ハーネスを離した時のクラスです。
    """
    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        """
        停止コマンドを生成し、一定時間ごとハーネスを握るように促す音声を流します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        if self.count % 30 == 0:
            self.count += 1
            sound.sperker_on()
            sound.say_touch()
            return [["stop"]]
        else:
            self.count += 1
        return []

    def reset(self):
        """
        各種値をリセットします。
        """
        Travel.reset(self)
        self.is_terminate = True


class Turn(Travel):
    """
    曲がり角曲がるクラスです。
    """

    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)

    def generate_command(self):
        """
        コマンドを生成し、曲がり角を曲がる音声通知をします。
        壁との距離を旋回半径に回転した後、直進をします。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        print("isast {0}".format(self.is_arduino_stop()))
        if self.count == 0:
            self.count += 1
            sound.say_turn()
            return [["turn", 30, 90, Run.TARGET_DIST - 40, int(self.data.is_left)]]
        elif self.count == 10 and self.is_arduino_stop():
            self.count += 1
            sound.say_straight()
            return []
        elif self.count == 11:
            self.is_terminate = True
            return [["velocity", 30, 30]]
        elif self.is_arduino_stop():
            self.count += 1
            return []
        else:
            return []


class Cross(Travel):
    """
    曲がり角を直進するクラスです。
    """

    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        self.is_terminate = True

    def generate_command(self):
        """
        直進コマンドを生成し、直進音声を流します。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        if self.count == 0:
            self.count += 1
            sound.say_straight()
        return [["velocity", 30, 30]]


    def reset(self):
        """
        各種値をリセットします。
        """
        Travel.reset(self)
        self.is_terminate = True


class Avoid(Travel):
    """
    障害物回避を行うクラスです。
    現在、回避動作は実装されていません。
    """

    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        Travel.__init__(self, data)
        # self.is_terminate = True


    def generate_command(self):
        """
        障害物回避コマンドを生成し、障害物回避音声を通知します。
        現在、障害物回避動作は実装されていません。
        
        :rtype: list
        :return: Arduinoに送る走行コマンド
        """
        self.is_terminate = True
        if self.count == 0:
            self.count += 1
            sound.say_straight()
            return [["stop"]]
        else:
            return []
