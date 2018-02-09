"""
Arduinoとの通信のラッパーモジュールです。
"""

from arduino import Arduino
from time import sleep, time


class Request:
    """
    Arduinoとの通信のラッパーです。
    値の取得はtaskCommからのポーリングで行われます。
    命令の送信はキューを介して行われます。
    """

    def __init__(self, q):
        """
        コンストラクタです。

        :param Queue q: 送信データの入ったキューです。
        """
        self.arduino = Arduino()
        self.q = q  # キューの生成
        self.vals = {}  # データ入れ
        self.btnL = Button()
        self.btnR = Button()

    def get(self):
        """
        値を取得するメソッドです。取得した値はvalsへ格納されます。

        :return: なし
        """
        start = time()
        while True:
            tmp = self.arduino.receive()
            to = time() - start
            if not tmp:
                break
            if (not len(tmp) == 2) or to > 0.1:
                continue
            self.vals[tmp[0]] = float(tmp[1])
            if tmp[0] == "ctrlA":
                self.btnL.check(tmp[1])
                self.vals["tglL"] = self.btnL.state
            elif tmp[0] == "ctrlB":
                self.btnR.check(tmp[1])
                self.vals["tglR"] = self.btnR.state

    def put(self):
        """
        キュー内のコマンドをArduinoへ送信するメソッドです。

        :return: なし
        """
        if self.q.empty():
            return
        while not self.q.empty():  # キューが空じゃなかったらループ
            cmd = self.q.get()  # キューから取り出す
            self.arduino.send(cmd)  # 型チェックしたほうがいいじゃないの？
            self.arduino.arduino_update()


class Button:
    """
    コントローラボタンにソフトウェア的にトグル動作をさせるためのクラスです。

    :author: 坂下尚史
    """
    def __init__(self):
        """
        コンストラクタです。
        """
        self.state = False
        self.prev = 1

    def check(self, curr):
        """
        現在値からボタンの状態を判定します。

        :param int,bool curr: 現在値です。
        :rtype: bool
        :return: 現在のトグル動作の状態です。
        """
        curr = int(curr)
        if not curr == self.prev:
            if not curr:
                self.state = not self.state
        self.prev = curr
        return self.state

if __name__ == '__main__':
    req = Request()
    req.order(['Straight', 10, 10])
    req.get()
    print(req.vals)
    req.put()
    sleep(1)
