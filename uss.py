from time import sleep
import smbus2


class SRF02OpenError(Exception):
    def __init__(self, addr):
        self.addr = addr

    def __str__(self):
        return ('Address {0} is not SRF02'.format(self.addr))

i2c = smbus2.SMBus(1)


class SRF02:

    LEFT = 0x70
    RIGHT = 0x71

    INTERVAL = 0.05
    MIN_DIST = 16
    MAX_DIST = 600
    CENTER_DIST = 10

    def __init__(self, addr):
        self.addr = addr
        # ソフトウェアリビジョンの確認
        if not i2c.read_byte_data(self.addr, 0) == 0x06:
            raise SRF02OpenError(self.addr)
        else:
            print("SRF02 opened in {0}".format(self.addr))    #超音波センサでなければ例外

    def emit(self):
        i2c.write_byte_data(self.addr, 0x00, 0x51)     #超音波出す

    def get(self):                            #返ってくるまで待つ
        data = i2c.read_i2c_block_data(self.addr, 0x02, 2)
        data = (data[0] << 8) | data[1]
        if data < SRF02.MIN_DIST or data > SRF02.MAX_DIST:
            return False                                    #超音波センサの測定不可区間
        else:
            return data + SRF02.CENTER_DIST                   #機体からの距離をかえす


class Uss:
    """
    I2Cを介した超音波センサとの通信タスクです。
    値の取得はtaskPollからのポーリングで行われます。
    taskMainからはvalsにアクセスされ、taskCommからはget()にアクセスされます。
    """

    NUM = 8  # 超音波センサの数
    ADDR_BASE = 0x70  # アドレスの最小値

    def __init__(self):
        """
        コンストラクタです。
        I2Cオブジェクトを取得し、超音波センサをオープンします。
        """

        self.addr = range(Uss.ADDR_BASE, Uss.ADDR_BASE+Uss.NUM)
        self.srf = []
        for x in self.addr:
            self.srf.append(SRF02(x))
        self.vals = [0] * Uss.NUM  # データ入れ

    def get(self):
        """
        値を取得します。取得した値はvalsへ格納されます。
        :return: None
        """
        for srf in self.srf:
            srf.emit()
        sleep(0.05)
        tmp = map(lambda x: x.get(), self.srf)
        self.vals = list(tmp)

uss = Uss()  # このグローバル変数を各モジュールが操作します。


if __name__ == '__main__':
    while True:
        uss.get()
        print(uss.vals)
        sleep(1)
