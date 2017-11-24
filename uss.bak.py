from time import sleep
import random


class Uss:
    """
    I2Cを介した超音波センサとの通信タスクです。
    値の取得はtaskPollからのポーリングで行われます。
    taskMainからはvalsにアクセスされ、taskCommからはget()にアクセスされます。
    """

    NUM = 9  # 超音波センサの数
    ADDR_BASE = 0x70  # アドレスの最小値

    def __init__(self):
        """
        コンストラクタです。
        I2Cオブジェクトを取得し、超音波センサをオープンします。
        """
        self.i2c = None  # I2Cオブジェクト
        self.addr = []  # アドレス群
        self.vals = []  # データ入れ
        for i in range(Uss.ADDR_BASE, Uss.ADDR_BASE+Uss.NUM):
            self.addr.append(i)
            self.vals.append(None)
            print("USS opened in {0}".format(i))

    def get(self):
        """
        値を取得します。取得した値はvalsへ格納されます。
        :return: None
        """
        for uss in self.addr:
            # print("USS polled in {0}".format(uss))
            pass
        sleep(0.05)
        for i in range(Uss.NUM):
            self.vals[i] = random.randint(0, 300)

uss = Uss()  # このグローバル変数を各モジュールが操作します。


if __name__ == '__main__':
    u = Uss()
    print(len(u.vals))
    while True:
        u.get()
        for val in u.vals:
            print(val)
        sleep(1)
