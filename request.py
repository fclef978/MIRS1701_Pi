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
        self.vals = {'batt': 0}  # データ入れ

    def get(self):
        """
        値を取得します。取得した値はvalsへ格納されます。
        :return: None
        """
        self.arduino.send([12, 0, 0])
        sleep(0.01)
        tmp = self.arduino.receive()
        if not tmp == False:
            self.vals['batt'] = tmp[0] / 100

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
        while not self.q.empty():  # キューが空じゃなかったらループ
            cmd = self.q.get()  # キューから取り出す
            self.arduino.send(cmd)  # 型チェックしたほうがいいじゃないの？

req = Request()  # このグローバル変数を各モジュールが操作します。

if __name__ == '__main__':
    req.get()
    print(req.vals)
    req.order([2, 50, 100])
    req.put()
    sleep(10)
