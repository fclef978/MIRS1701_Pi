"""
ラズパイのGPIOをラップするモジュールです。

:author: 鈴木宏和
"""

from RPi import GPIO
import time


class IO:
    """
    ラズパイのGPIOをラップするクラスです。
    """
    #: マイクロスイッチのピン番号を並べた属性です。
    PIN = [11, 13, 15, 19, 21, 23, 29, 31]
    #: リセットピンの番号を表す属性です。
    RESET = 32
    #: パワーアンプのスタンバイスイッチのピン番号を表す属性です。
    SP_SSW = 7
    #: 入出力の方向を表す属性です。コンストラクタに渡して使います。
    IN = GPIO.IN
    #: 入出力の方向を表す属性です。コンストラクタに渡して使います。
    OUT = GPIO.OUT

    def __init__(self, port, dir, is_pull_up=False):
        """
        コンストラクタです。ここで通信開始から通信確立まで行います。

        :param int port: ポート番号(物理ピン番号)です。
        :param dir: 入出力方向です。このクラスの属性を入れてください。
        :param bool is_pull_up: プルアップするか否かを指定します。デフォルトはFalseです。
        """
        self.port = port
        self.dir = dir
        self.is_pull_up = is_pull_up
        GPIO.setmode(GPIO.BOARD)
        if self.dir == IO.IN:
            if self.is_pull_up:
                GPIO.setup(self.port, self.dir, pull_up_down=GPIO.PUD_UP)
            else:
                GPIO.setup(self.port, self.dir)
        elif self.dir == IO.OUT:
            GPIO.setup(self.port, self.dir)

    def __del__(self):
        """
        デストラクタです。

        :return: なし
        """
        GPIO.cleanup(self.port)

    def read(self):
        """
        ピンから読み取るメソッドです。

        :rtype: bool
        :return: ピンの状態です。
        """
        return GPIO.input(self.port)

    def write(self, state):
        """
        ピンのON/OFFを変えるメソッドです。

        :param bool state: ON/OFFです。
        :rtype: bool
        :return: 成功したらTrue、OUTでないピンに書き込んだらFalseを返します。
        """
        if self.dir == IO.OUT:
            GPIO.output(self.port, state)
            return True
        else:
            print("Port {0} is not OUTPUT".format(self.port))
            return False

    def on(self):
        """
        ピンをONにするメソッドです。

        :return: なし
        """
        self.write(True)

    def off(self):
        """
        ピンをOFFにするメソッドです。

        :return: なし
        """
        self.write(False)

    def inv(self):
        """
        ピンを反転させるメソッドです。

        :return: なし
        """
        self.write(not self.read())
