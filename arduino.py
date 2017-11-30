# Arduino通信クラス
# TL 鈴木宏和
# 2017-08-26
# 2017-08-26

import serial
from time import sleep
import os


class ArduinoOpenError(Exception):
    
    def __str__(self):
        return ('Arduino Open Failed')


class Arduino:

    def __init__(self):
        if os.name == 'nt':
            self.port = 'COM4'
        self.baud_rate = 2000000
        try:
            self.ser = serial.Serial(self.port, self.baud_rate)
        except:
            self.ser = serial.Serial('/dev/ttyACM1', 115200)
            self.port = '/dev/ttyACM1'
        self.flush()
        self.buf = []
        # --------------------------------------------------------------
        print('Arduino Waiting...')

        while True:
            self.write("RasPi:Ready;")
            sleep(0.001)
            response = self.read_str_until(';')
            if response == "Arduino:OK":
                break

        print("Arduino Opened on {0}".format(self.port))

    def __del__(self):
        cmd = [99, 0, 0]
        self.send(cmd)
        self.ser.close()

    def flush(self):
        self.ser.reset_input_buffer()

    def available(self, num=0):
        if num == 0:
            return self.ser.in_waiting
        elif num > 0:
            return self.ser.in_waiting >= num
        else:
            return False

    def send(self, cmd_data):
        ser_data = self.encode(cmd_data)
        self.write(ser_data)

    def receive(self):
        cnt = 0
        ser_data = [0] * 7
        # 50ループ(だいたい50ミリ秒)でタイムアウト
        for i in range(50):
            if self.ser.in_waiting >= 7:
                ser_data[0] = self.read()
                if ser_data[0] >= 0x80: # 0x80 = 128
                    for i in range(1, 7):
                        ser_data[i] = self.read()
                    cmd_data = self.decode(ser_data)
                    return cmd_data
            sleep(0.001)

        return False
        
    def read_one_byte(self):
        result = self.ser.read()
        return result

    def read_str_until(self, terminator):
        while self.available(1):
            tmp = self.read_one_byte().decode('utf-8')
            if tmp == terminator:
                result = self.buf
                self.buf =[]
                break
            self.buf.append(tmp)
        else:
            return False

        return ''.join(result)


    def write(self, ser_data):
        self.ser.write(ser_data.encode('ASCII'))

    @staticmethod
    def encode(cmd_data):
        mid_data = [0] * 6
        ser_data = [0] * 7
        
        mid_data[0] = (cmd_data[0] >> 8) & 0x00ff
        mid_data[1] = cmd_data[0] & 0x00ff
        mid_data[2] = (cmd_data[1] >> 8) & 0x00ff
        mid_data[3] = cmd_data[1] & 0x00ff
        mid_data[4] = (cmd_data[2] >> 8) & 0x00ff
        mid_data[5] = cmd_data[2] & 0x00ff

        ser_data[0] = 0x80 | ((mid_data[0] >> 1) & 0x7f)
        ser_data[1] = ((mid_data[0] << 6) & 0x40) | ((mid_data[1] >> 2) & 0x3f)
        ser_data[2] = ((mid_data[1] << 5) & 0x60) | ((mid_data[2] >> 3) & 0x1f)
        ser_data[3] = ((mid_data[2] << 4) & 0x70) | ((mid_data[3] >> 4) & 0x0f)
        ser_data[4] = ((mid_data[3] << 3) & 0x78) | ((mid_data[4] >> 5) & 0x07)
        ser_data[5] = ((mid_data[4] << 2) & 0x7c) | ((mid_data[5] >> 6) & 0x03)
        ser_data[6] = ((mid_data[5] << 1) & 0x7e)

        return ser_data

    @staticmethod
    def decode(ser_data):
        mid_data = [0] * 6
        cmd_data = [0] * 3

        mid_data[0] = ((ser_data[0] << 1) & 0xfe) | ((ser_data[1] >> 6) & 0x01)
        mid_data[1] = ((ser_data[1] << 2) & 0xfc) | ((ser_data[2] >> 5) & 0x03)
        mid_data[2] = ((ser_data[2] << 3) & 0xf8) | ((ser_data[3] >> 4) & 0x07)
        mid_data[3] = ((ser_data[3] << 4) & 0xf0) | ((ser_data[4] >> 3) & 0x0f)
        mid_data[4] = ((ser_data[4] << 5) & 0xe0) | ((ser_data[5] >> 2) & 0x1f)
        mid_data[5] = ((ser_data[5] << 6) & 0xc0) | ((ser_data[6] >> 1) & 0x3f)

        cmd_data[0] = (mid_data[0] << 8) | mid_data[1]
        cmd_data[1] = (mid_data[2] << 8) | mid_data[3]
        cmd_data[2] = (mid_data[4] << 8) | mid_data[5]

        return cmd_data
        
if __name__ == "__main__":
    a = Arduino()
