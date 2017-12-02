# import arduino
from queue import Queue
from arduino import Arduino
from time import sleep


class Request:
    """
    Arduinoとの通信のラッパーです。
    値の取得はtaskCommからのポーリングで行われます。
    命令の送信はキューを介して行われます。
    taskMainからはvalsとorder()にアクセスされ、taskCommからはget()とput()にアクセスされます。
    """

    def __init__(self):
        self.arduino = Arduino()
        self.q = Queue()  # キューの生成
        self.vals = {}  # データ入れ

    def get(self):
        """
        値を取得します。取得した値はvalsへ格納されます。
        :return: None
        """
        while True:
            tmp = self.arduino.receive()
            if not tmp:
                break
            self.vals[tmp[0]] = float(tmp[1])

    def order(self, cmd):
        """
        キューへコマンドを挿入します。
        :param cmd: Arduinoコマンド
        :return: None
        """
        self.q.put(cmd)  # エンキュー

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

req = Request()  # このグローバル変数を各モジュールが操作します。

if __name__ == '__main__':
    sleep(1.5)
    req.get()
    print(req.vals)
    req.order(['Straight', 50, 100])
    req.put()
    sleep(1)
