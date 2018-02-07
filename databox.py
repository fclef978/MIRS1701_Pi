"""
Arduinoや超音波センサなどの値を格納し、共有するためのモジュールです。。
:author: 鈴木宏和
"""


class DataBox:
    """
    受信したデータを格納するクラスです。
    """
    def __init__(self):
        """
        コンストラクタです。
        """
        self.uss = {}
        self.ard = {}
        self.is_left = True
        self.state = "init"
        self.expected = "straight"
        self.prev = ""

    def set_value(self, uss, ard):
        """
        値をセットするメソッドです。
        :param list uss:
        :param dict ard:
        :return: なし
        """
        self.__deside_uss_dir(uss)
        self.ard = ard

    def __deside_uss_dir(self, uss):
        """
        壁が左か右かによって連想配列のキーを変えて代入するメソッドです。
        :param list uss:
        :return: なし
        """
        self.uss["f"] = uss[0]
        self.uss["b"] = uss[4]
        if self.is_left:
            self.uss["sf"] = uss[7]
            self.uss["s"] = uss[6]
            self.uss["sb"] = uss[5]
            self.uss["os"] = uss[2]
        else:
            self.uss["sf"] = uss[1]
            self.uss["s"] = uss[2]
            self.uss["sb"] = uss[3]
            self.uss["os"] = uss[6]
