from RPi import GPIO
import time


class IO:
    PIN = [11, 13, 15, 19, 21, 23, 29, 31]
    RESET = 32

    IN = GPIO.IN
    OUT = GPIO.OUT

    def __init__(self, port, dir, isPullUp=False):
        self.port = port
        self.dir = dir
        self.isPullUp = isPullUp
        GPIO.setmode(GPIO.BOARD)
        if self.dir == IO.IN:
            if self.isPullUp:
                GPIO.setup(self.port, self.dir, pull_up_down=GPIO.PUD_UP)
            else:
                GPIO.setup(self.port, self.dir)
        elif self.dir == IO.OUT:
            GPIO.setup(self.port, self.dir)

    def __del__(self):
        GPIO.cleanup(self.port)

    def read(self):
        return GPIO.input(self.port)

    def write(self, state):
        if self.dir == IO.OUT:
            GPIO.output(self.port, state)
            return True
        else:
            print("Port {0} is not OUTPUT".format(self.port))
            return False
            
    def on(self):
        self.write(True)
            
    def off(self):
        self.write(False)

    def inv(self):
        self.write(not self.read())
