from arduino import Arduino
from time import sleep, time


class Request:
    """
    Arduinoとの通信のラッパーです。
    値の取得はtaskCommからのポーリングで行われます。
    命令の送信はキューを介して行われます。
    taskMainからはvalsとorder()にアクセスされ、taskCommからはget()とput()にアクセスされます。
    """

    def __init__(self, q):
        self.arduino = Arduino()
        self.q = q  # キューの生成
        self.vals = {}  # データ入れ
        self.btnL = Button()
        self.btnR = Button()

    def get(self):
        """
        値を取得します。取得した値はvalsへ格納されます。
        :return: None
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
        キュー内のコマンドをArduinoへ送信します。
        :return: None
        """
        if self.q.empty():
            return
        while not self.q.empty():  # キューが空じゃなかったらループ
            cmd = self.q.get()  # キューから取り出す
            self.arduino.send(cmd)  # 型チェックしたほうがいいじゃないの？
            self.arduino.arduino_update()

    def set_val(self, key, val):
        self.vals[key] = val


class Button():
    def __init__(self):
        self.state = False
        self.prev = 1

    def check(self, curr):
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
