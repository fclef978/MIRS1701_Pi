from time import time


class State:

    def __init__(self, data):
        self.state = "init"
        self.data = data
        self.is_changed = False
        self.expected = "straight"
        self.prev = ""
        self.timer = 0

    def judge(self):
        prev = self.state
        self.__getattribute__(self.state)()
        if self.sns_check("help"):  # 救援要請ボタンが押されていたら救援要請に入る
            self.state = "help"
        if not self.state == "help":
            if self.sns_check("un_touch"):  # 救援要請中でなく、ハーネスから手が離れた場合
                if self.timer == 0:  # タイマーセット
                    self.timer = time()
                self.state = "un_touch"
        if not prev == self.state:
            self.prev = prev
            self.is_changed = True
        else:
            self.is_changed = False

    def init(self):
        if self.sns_check("jsU"):
            self.state = "straight"

    def straight(self):
        """
        直進走行状態からの状態分岐です。
        何かを検知したら一度走行を停止し、次になる状態をexpectedに代入します。
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
        待機状態からの状態分岐です。
        どの状態の前かを判断し、入力が行われると次の状態へ移行します。
        waitと言いながらstopも入ってるので分離したほうがいいかも?
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
        if not self.sns_check("obstacle"):
            self.state = "straight"

    def change(self):
        self.state = "straight"

    def turn(self):
        if self.sns_check("catch_wall"):
            self.state = "straight"
            self.expected = "straight"

    def cross(self):
        if self.sns_check("catch_wall"):
            self.state = "straight"
            self.expected = "straight"

    def help(self):
        if self.prev == "un_touch":
            if not self.sns_check("un_touch"):  # un_touchから時間経過で来た場合、握ったらwaitに戻る
                self.state = "wait"
        elif not self.sns_check("help"):  # 救援がいらなくなったら、waitに戻る
            self.state = "wait"

    def un_touch(self):
        if not self.sns_check("un_touch"):  # ハーネスを握ったらwaitに戻る
            self.state = "wait"
            self.timer = 0
        elif time() - self.timer > 30:  # 時間経過でhelpへ移行
            self.state = "help"
            self.timer = 0

    def sns_check(self, check_name):
        """
        センサーや入力から、判定してほしい項目(check_name)をチェックするメソッド
        センサーと入力のチェックは別のメソッドにした方がわかりやすいかも?
        :param check_name:
        :return:True or False
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
            return self.data.uss["f"] > 150  # 曲がり角に直進の道はあるか
        elif check_name == "help":  # 救援要請ボタン
            return self.data.ard["tglR"]  # 救援が必要ならTrue、いらないならFalse
        elif check_name == "un_touch":  # 静電容量式タッチセンサ
            return self.data.ard["cap"] == 1  # 離れていたらTrueを返す(capが0)、デバッグのため現在反転

