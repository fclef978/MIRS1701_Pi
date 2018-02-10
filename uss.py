"""
超音波センサを制御するモジュールです。

:author: 鈴木宏和
"""

from time import sleep
import smbus2


class SRF02OpenError(Exception):
    """
    SRF02を開けなかったときの例外クラスです。
    """
    def __init__(self, addr):
        self.addr = addr

    def __str__(self):
        return ('Address {0} is not SRF02'.format(self.addr))

i2c = smbus2.SMBus(1)


class SRF02:
    """
    SRF02を制御するためのクラスです。
    """
    #: 測定にかかる時間を表す属性です。
    INTERVAL = 0.05
    #: 最小測定可能距離を表す属性です。
    MIN_DIST = 16
    #: 最大測定可能距離を表す属性です。
    MAX_DIST = 600

    def __init__(self, addr):
        """
        コンストラクタです。開けなかった場合、例外を発生させます。

        :param int addr: I2Cアドレスです。
        :except: SRF02OpenError
        """
        self.addr = addr
        # ソフトウェアリビジョンの確認
        if not i2c.read_byte_data(self.addr, 0) == 0x06:
            raise SRF02OpenError(self.addr)
        else:
            print("SRF02 opened in {0}".format(self.addr))

    def emit(self):
        """
        超音波を発射させます。

        :return: なし
        """
        sleep(0.002)
        i2c.write_byte_data(self.addr, 0x00, 0x51)

    def get(self):
        """
        SRF02から値を得ます。必ずemitメソッドを実行した後に実行してください。

        :rtype: int
        :return: 計測値
        """
        sleep(0.002)
        data = i2c.read_i2c_block_data(self.addr, 0x02, 2)
        data = (data[0] << 8) | data[1]
        if data < SRF02.MIN_DIST or data > SRF02.MAX_DIST:
            return SRF02.MAX_DIST                                   #超音波センサの測定不可区間
        else:
            return data                   #壁からの距離をかえす


class Uss:
    """
    I2Cを介した超音波センサとの通信のラッパクラスです。
    値の取得はtaskPollからのポーリングで行われます。
    self.valsに値が格納されます。
    """
    #: 超音波センサの数を表す属性です。
    NUM = 8
    #: アドレスの最小値を表す属性です。
    ADDR_BASE = 0x70

    def __init__(self):
        """
        コンストラクタです。超音波センサをオープンします。
        """
        self.addr = range(Uss.ADDR_BASE, Uss.ADDR_BASE+Uss.NUM)
        self.srf = []
        for x in self.addr:
            self.srf.append(SRF02(x))
        self.vals = [0] * Uss.NUM

    def get(self):
        """
        値を取得します。取得した値はvalsへ格納されます。

        :return: なし
        """
        for srf in self.srf:
            srf.emit()
        sleep(SRF02.INTERVAL * 1.1)

        def f(x):
            return x.get()
        tmp = map(f, self.srf)
        self.vals = list(tmp)


if __name__ == '__main__':
    uss = Uss()
    while True:
        uss.get()
        print(uss.vals)
        sleep(1)
