from time import time


class State:
    """
    走行状態を判定するクラスです。
    判定結果はself.stateへ格納されます。
    """
    def __init__(self, data):
        """
        コンストラクタです。各種初期状態を代入します。
        
        :param Databox data: Databoxのオブジェクト
        """
        self.state = "init"
        self.data = data
        self.is_changed = False
        self.expected = "straight"
        self.prev = ""
        self.timer = 0

    def judge(self):
        """
        走行状態を判定します。今の状態により各種判定用メソッドを呼び出します。
        
        :return: なし
        """
        prev = self.state
        self.__getattribute__(self.state)()
        if self.sns_check("help"):
            self.state = "help"
        if not self.state == "help":
            if self.sns_check("un_touch"):
                if self.timer == 0:
                    self.timer = time()
                self.state = "un_touch"
        if not prev == self.state:
            self.prev = prev
            self.is_changed = True
        else:
            self.is_changed = False

    def init(self):
        """
        初期状態での判定です。ジョイスティック前入力で直進状態に移行します。
        
        :return: なし
        """
        if self.sns_check("jsU"):
            self.state = "straight"

    def straight(self):
        """
        直進走行状態での判定です。
        何かを検知したら停止状態に移行し、次になる状態をexpectedに代入します。
        
        :return: なし
        """
        if self.sns_check("corner"):  # 曲がり角
            self.state = "wait"
            self.expected = "turn"
        elif self.data.is_left and self.sns_check("jsR"):  # 左壁右入力
            self.state = "change"
        elif not self.data.is_left and self.sns_check("jsL"):  # 右壁左入力
            self.state = "change"
        elif self.sns_check("obstacle"):  # 障害物
            self.state = "wait"
            self.expected = "avoid"
        elif self.sns_check("jsD"):  # 一時停止
            self.state = "wait"
            self.expected = "straight"

    def wait(self):
        """
        待機状態での判定です。
        入力が行われるとexpectedの状態へ移行します。
        
        :return: なし
        """
        if self.expected == "turn":  # 交差点の動作
            if (self.data.is_left and self.sns_check("jsL")) or (not self.data.is_left and self.sns_check("jsR")):  # 曲がる
                self.state = "turn"
            if self.sns_check("jsU") and self.sns_check("cross_straight"):
                self.state = "cross"
        elif self.expected == "straight":
            if self.sns_check("jsU"):
                self.state = "straight"
        elif self.expected == "avoid":
            if self.sns_check("jsU"):
                if not self.sns_check("obstacle"):
                    self.state = "straight"
                else:
                    self.state = "avoid"
                    self.data.step = 0
        else:
            self.state = self.expected

    def avoid(self):
        """
        障害物回避状態での判定です。障害物がなくなれば直進状態へ移行します。
        
        :return: なし
        """
        if not self.sns_check("obstacle"):
            self.state = "straight"

    def change(self):
        """
        左右の壁変更状態での判定です。直進状態へ移行します。
        
        :return: なし
        """
        self.state = "straight"

    def turn(self):
        """
        曲がり角回転状態での判定です。壁を検出したら直進状態へ移行します。
        
        :return: なし
        """
        if self.sns_check("catch_wall"):
            self.state = "straight"
            self.expected = "straight"

    def cross(self):
        """
        曲がり角直進状態での判定です。壁を検出したら直進状態へ移行します。
        
        :return: なし
        """
        if self.sns_check("catch_wall"):
            self.state = "straight"
            self.expected = "straight"

    def help(self):
        """
        救援要請状態での判定です。救援がいらなくなったら待機状態へ移行します。
        
        :return: なし
        """
        if self.prev == "un_touch":
            if not self.sns_check("un_touch"):  # un_touchから時間経過で来た場合、握ったらwaitに戻る
                self.state = "wait"
        elif not self.sns_check("help"):  # 救援がいらなくなったら、waitに戻る
            self.state = "wait"

    def un_touch(self):
        """
        ハーネスから手が離れている状態での判定です。時間経過で救援要請状態へ移行します。
        
        :return: なし
        """
        if not self.sns_check("un_touch"):  # ハーネスを握ったらwaitに戻る
            self.state = "wait"
            self.timer = 0
        elif time() - self.timer > 30:  # 時間経過でhelpへ移行
            self.state = "help"
            self.timer = 0

    def sns_check(self, check_name):
        """
        センサーの値から入力があるかどうかを判定します。
        
        :param String check_name: 判定ほしい入力
        :return boolean: 入力判定結果
        """
        if check_name == "jsL":  # ジョイスティック左入力
            return self.data.ard["jsX"] > 900
        elif check_name == "jsR":  # ジョイスティック右入力
            return self.data.ard["jsX"] < 100
        elif check_name == "jsD":  # ジョイスティック前入力
            return self.data.ard["jsY"] > 800
        elif check_name == "jsU":  # ジョイスティック後ろ入力
            return self.data.ard["jsY"] < 200
        elif check_name == "obstacle":  # 障害物
            return self.data.uss["f"] < 40
        elif check_name == "corner":  # 曲がり角
            return self.data.uss["sf"] > 150
        elif check_name == "catch_wall":  # 壁があるか判定
            return self.data.uss["sb"] < 150  # 壁があったらTrue
        elif check_name == "cross_straight":
            return self.data.uss["f"] < 150  # 曲がり角に直進の道はあるか
        elif check_name == "help":  # 救援要請ボタン
            return self.data.ard["tglR"]  # 救援が必要ならTrue、いらないならFalse
        elif check_name == "un_touch":  # 静電容量式タッチセンサ
            return self.data.ard["cap"] == 1  # 離れていたらTrueを返す(capが0)、デバッグのため現在反転

