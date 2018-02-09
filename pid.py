"""
PID制御をする際の数値計算をラップするモジュールです。

:author: 鈴木宏和
"""

from time import sleep


class PID:
    """
    PID制御をする際の数値計算をするクラスです。
    """
    def __init__(self, gain, dt, target):
        """
        コンストラクタです。

        :param tuple gain: Pゲイン,Iゲイン,Dゲインからなる長さ3のタプルです。(P, I, D)の順番です。
        :param float dt: 制御周期です。単位はsecです。
        :param float target: 目標値です。
        """
        self.__prev = 0
        self.__curr = 0
        self.__sum = 0
        self.__kp, self.__ki, self.__kd = gain
        self.__dt = dt
        self.target = target
        self.__is_first = True

    def calc(self, val):
        """
        現在値から出力を計算するメソッドです。

        :param float val: 現在値です。
        :rtype float:
        :return: PID制御の出力です。
        """
        self.__calc_curr(val)
        return self.__calc_prop() + self.__calc_intg() + self.__calc_diff()

    def __calc_curr(self, curr):
        self.__curr = self.target - curr

    def __calc_prop(self):
        return self.__curr * self.__kp

    def __calc_intg(self):
        self.__sum += self.__curr
        return self.__sum * self.__ki * self.__dt

    def __calc_diff(self):
        if self.__is_first:
            self.__is_first = False
            return 0
        diff = self.__curr - self.__prev
        self.__prev = self.__curr
        return diff * self.__kd / self.__dt


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
