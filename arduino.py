"""
Arduinoとの通信をするモジュールです。
:author: 鈴木宏和
"""

from serial import Serial
from time import sleep, time
from gpio import IO
import os


class ArduinoOpenError(Exception):
    """
    Arduinoとの通信失敗時用の例外クラスです。
    """
    def __str__(self):
        return ('Arduino Open Failed')


class Arduino:
    """
    Arduinoとの通信を行うクラスです。
    """

    def __init__(self):
        """
        コンストラクタです。ここで通信開始から通信確立まで行います。
        """
        self.__reset_pin = IO(IO.RESET, IO.OUT)
        # self.reset_pin.off()
        # sleep(0.01)
        self.__reset_pin.on()
        sleep(0.5)
        if os.name == 'nt':
            self.port = 'COM4'
        elif os.name == 'posix':
            self.port = '/dev/ttyACM0'
        self.baud_rate = 2000000
        try:
            self.__ser = Serial(self.port, self.baud_rate)
        except:
            self.__ser = Serial('/dev/ttyACM1', self.baud_rate)
            self.port = '/dev/ttyACM1'
        self.__flush()
        self.__buf = []
        print('Arduino Waiting...')

        while self.__open():
            pass

        print("Arduino Opened on {0}".format(self.port))

    def __del__(self):
        """
        デストラクタです。ポートを閉じてArduinoをリセットします。
        :return: なし
        """
        try:
            self.__ser.close()
        except TypeError:
            pass
        self.__reset_pin.off()
        sleep(1)
        self.__reset_pin.on()

    def __open(self):
        """
        Arduinoとの通信確立をするメソッドです。
        :rtype: bool
        :return: 成功したらTrue, 失敗したらFalse
        """
        self.__write("RasPi:Ready;")
        sleep(0.001)
        response = self.__read_str_until(';')
        if response == "Arduino:OK":
            return True
        return False

    def __flush(self):
        """
        受信バッファを空にするメソッドです。
        :return: なし
        """
        self.__ser.reset_input_buffer()

    def __available(self, num=0):
        """
        受信バッファのデータ数を返します。
        引数を指定すると、そのバイト分溜まっているか判定します。
        :param int num: デフォルト引数で、指定すると、指定したバイト分バッファに溜まっているかの判定になる。
        :rtype: int, bool
        :return: バイト数または判定結果
        """
        if num == 0:
            return self.__ser.in_waiting
        elif num > 0:
            return self.__ser.in_waiting >= num
        else:
            return False

    def send(self, cmd_data):
        """
        Arduinoにコマンドを送信するメソッドです。
        :param list cmd_data: コマンドです。
        :return: なし
        """
        ser_data = self.encode(cmd_data)
        print(ser_data)
        self.__write(ser_data)

    def arduino_update(self):
        """
        Arduinoにコマンドアップデート信号を送るメソッドです。
        :return: なし
        """
        ser_data = self.encode(["update"])
        self.__write(ser_data)

    def receive(self):
        """
        Arduinoから情報を受信するメソッドです。
        :rtype: list, bool
        :return: 失敗するとFalseを、成功すると文字列の配列を返します。
        """
        tmp = self.__read_str_until(';')
        if not tmp:
            return False
        return tmp.split(':')
        
    def __read_one_byte(self):
        """
        バッファから1バイト読み出すメソッドです。
        :rtype: bytearray
        :return: 受信したものを返します。(長さ1のbytearrayでエンコーディングはASCII)
        """
        result = self.__ser.read()
        return result

    def __read_str_until(self, terminator):
        """
        指定した文字が現れるまでバッファから読み出します。
        途中で終わってしまった場合、その読みかけの文字列を内部で保存し、次回呼び出し時に先頭に連結します。
        :param str terminator: 終了文字です(長さ1のstr)
        :rtype: str
        :return: 受信した文字列です。失敗すると空文字列になります。
        """
        try:
            while self.__available(1):
                tmp = self.__read_one_byte().decode('utf-8')
                if tmp == terminator:
                    result = self.__buf
                    self.__buf = []
                    break
                self.__buf.append(tmp)
            else:
                return False
            return ''.join(result)
        except UnicodeDecodeError:
            return ""

    def __write(self, ser_data):
        """
        Arduinoに文字列を送信するメソッドです。
        :param str ser_data: 送信文字列です。
        :return: なし
        """
        self.__ser.write(ser_data.encode('ASCII'))

    @staticmethod
    def encode(cmd_data):
        """
        コマンド型リストを送信型の文字列に変換します。
        :param list cmd_data: コマンドです。
        :rtype: str
        :return: 送信用文字列です。
        """
        cmd = cmd_data[0].lower()
        if cmd == "update":
            ser_data = "CU:1;"
        elif cmd == "stop":
            ser_data = "RM:1;"
        elif cmd == "straight":
            ser_data = "RM:2;RS:{0};RD:{1};".format(cmd_data[1], cmd_data[2])
        elif cmd == "rotation":
            ser_data = "RM:3;RO:{0};RA:{1};".format(cmd_data[1], cmd_data[2])
        elif cmd == "velocity":
            ser_data = "RM:4;VL:{0};VR:{1};".format(cmd_data[1], cmd_data[2])
        elif cmd == "battery":
            ser_data = "RM:10;BA:{0};BB:{1};".format(cmd_data[1], cmd_data[2])
        elif cmd == "turn":
            ser_data = "RM:5;TS:{0};TA:{1};TR:{2};TD:{3};".format(cmd_data[1], cmd_data[2], cmd_data[3], cmd_data[4])
        elif cmd == "reset":
            ser_data = "RM:100;"
        else:
            ser_data = None

        return ser_data
        
if __name__ == "__main__":
    a = Arduino()
    a.send(["STRAIGHT", 12, 13])
    a.arduino_update()
    sleep(2)
    print(a.receive())
