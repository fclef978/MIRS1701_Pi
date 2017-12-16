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
        elif os.name == 'posix':
            self.port = '/dev/ttyACM0'
        self.baud_rate = 2000000
        try:
            self.ser = serial.Serial(self.port, self.baud_rate)
        except:
            self.ser = serial.Serial('/dev/ttyACM1', 115200)
            self.port = '/dev/ttyACM1'
        self.flush()
        self.buf = []
        print('Arduino Waiting...')

        while self.open():
            pass

        print("Arduino Opened on {0}".format(self.port))

    def __del__(self):
        cmd = ['reset']
        self.send(cmd)
        self.ser.close()

    def open(self):
        self.write("RasPi:Ready;")
        sleep(0.001)
        response = self.read_str_until(';')
        if response == "Arduino:OK":
            return True
        return False

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

    def arduino_update(self):
        ser_data = self.encode(["update"])
        self.write(ser_data)

    def receive(self):
        tmp = self.read_str_until(';')
        if not tmp:
            return False
        return tmp.split(':')
        
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
            ser_data = "RM:5;BA:{0};BB:{1};".format(cmd_data[1], cmd_data[2])
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
