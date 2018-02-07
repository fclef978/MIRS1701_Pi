"""
バッテリーを管理するモジュールです。

:author: 鈴木宏和
"""


class BatteryVoltageDiffError(Exception):
    """
    バッテリーが不正値のときのための例外クラスです。
    """
    def __init__(self, diff, a, b):
        self.diff = diff
        self.a = a
        self.b = b

    def __str__(self):
        return """
        Battery Voltage Difference is {0}V. A = {1}V, B = {2}V.
        It is Dangerous because it is more than 1.0V!!
        This robot cannot start...
        """.format(self.diff, self.a, self.b)


class Battery:
    """
    バッテリーを管理するクラスです。
    電源電圧を監視し、常に適切な方のバッテリーに切り替えます。
    """

    #: 許容電位差を表す属性です。
    __ACCEPTABLE_DIFF = 0.3

    def __init__(self, a, b):
        """
        コンストラクタです。

        :param float a: バッテリーAの電圧です。
        :param float b: バッテリーBの電圧です。
        """
        self.set_values(a, b)
        # if self.__diff > 1.0:
        #     raise BatteryVoltageDiffError(self.__diff, a, b)
        self.__isAOn = False
        self.__isBOn = False
        self.__isInit = True
        print("A{0}V, B{1}V".format(a, b))

    def generate_command(self, a, b):
        """
        バッテリー切り替えコマンドを生成します。

        :param a: バッテリーAの電圧です。
        :param b: バッテリーBの電圧です。
        :rtype: list
        :return: コマンドです。(長さ1のリストの中に入っています)
        """
        self.set_values(a, b)
        cmd = []
        tmp = self.__judge()
        if tmp is not None:
            (a, b) = tmp
            if a:
                cmd.append(["Battery", 1, 0])
            elif b:
                cmd.append(["Battery", 0, 1])
        return cmd

    def __judge(self):
        """
        バッテリー切り替えの判定をします。

        :rtype: tuple, None
        :return: バッテリーを切り替える場合は長さ2のboolのタプルが返り、切り替えない場合はNoneが返ります。タプルは(左, 右)の順番です。
        """
        if self.__isInit:
            self.__isInit = False
            if self.__is_a_high():
                self.__isAOn = True
                return (True, False)
            else:
                self.__isBOn = True
                return (False, True)

        if self.__isAOn:
            if self.__is_a_high():
                return None
            elif self.__diff > Battery.__ACCEPTABLE_DIFF:
                self.__isBOn = True
                return (False, True)
        elif self.__isBOn:
            if not self.__is_a_high():
                return None
            elif self.__diff > Battery.__ACCEPTABLE_DIFF:
                self.__isAOn = True
                return (True, False)
        return None

    def set_values(self, a, b):
        """
        値をセットします。

        :param a: バッテリーAの電圧です。
        :param b: バッテリーA\Bの電圧です。
        :return: なし
        """
        self.a = a
        self.b = b
        self.__diff = self.__calc_volt_diff()

    def __is_a_high(self):
        """
        バッテリー電圧を比較します。

        :rtype: bool
        :return: Aの方が高ければTrue、そうでなければFalseを返します。
        """
        return self.a > self.b

    def __calc_volt_diff(self):
        """
        バッテリー電圧差を計算します。

        :rtype: float
        :return: 電位差です。
        """
        return abs(self.a - self.b)

if __name__ == "__main__":
    b = Battery(8.0, 8.2)
    print(b.generate_command(8.0, 8.2))
    print(b.generate_command(8.0, 7.8))
    print(b.generate_command(8.0, 7.6))
    print(b.generate_command(7.2, 7.6))
