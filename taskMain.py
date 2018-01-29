from ttask import PeriodicTask
from time import sleep
from battery import Battery
from run2 import Run
from gpio import IO
from state import State
from sound import Sound

import logging


class Main(PeriodicTask):
    """
    メインタスクです。センサーから値を取得して走行します。
    """
    INTERVAL = 0.1

    def __init__(self, uss, comm, q):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        
        self.pipe_uss = uss
        self.pipe_comm = comm
        self.uss = []
        self.req = {}
        self.q = q
        self.cmds = []
        self.ms = []
        self.state = State()
        self.is_left = True
        self.is_init = True
        PeriodicTask.__init__(self)

    def init(self):
        self.cmds = []
        while self.req == {} or self.uss == []:
            self.recv()
            sleep(0.01)
        self.batt = Battery(self.req["btA"], self.req["btB"])
        self.movement = Run()
        for pin in IO.PIN:
            self.ms.append(IO(pin, IO.IN, True))
        self.ms = tuple(self.ms)
    
    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.cmds = []
        self.recv()
        uss = self.deside_uss_dir()
        self.movement.set_val(self.is_left, uss)
        self.state.uss = uss
        self.state.sns = self.req
        self.state.isLeft = self.is_left
        state = self.state.state

        if state == "init":
            self.state.judge()
        elif state == "straight":
            self.cmds += self.movement.straight()
            self.state.judge()
        elif state == "turn":
            if self.is_init:
                self.cmds += [["turn", 30, 90, Run.TARGET_DIST, int(self.is_left)]]
                self.is_init = False
            else:
                if self.arduino_is_stop():
                    self.is_init = True
                    self.state.judge()
        """
        elif state == "change":
            if self.is_init:
                self.cmds += ["turn", 30, 90, 0, int(not self.is_left)]
                self.cmds += ["straight", self.movement.speed, uss["os"] - Run.TARGET_DIST]
                self.is_init = False
            else:
                if self.arduino_is_stop():
                    self.is_init = True
            if uss["f"] < 50:
                self.sound.talk("もちてをいれかえてください")
                self.cmds += ["turn", 30, 90, 0, int(self.is_left)]
                self.state.judge()
         """
                
        print(self.req["jsX"])
        self.batt_check()
        self.cmds_send()

    def arduino_is_stop(self):
        if self.req["mode"] == 0:
            True
        else:
            False

    def deside_uss_dir(self):
        uss = {}
        uss["f"] = self.uss[0]
        uss["b"] = self.uss[4]
        if self.is_left:
            uss["sf"] = self.uss[7]
            uss["s"] = self.uss[6]
            uss["sb"] = self.uss[5]
            uss["os"] = self.uss[2]
        else:
            uss["sf"] = self.uss[1]
            uss["s"] = self.uss[2]
            uss["sb"] = self.uss[3]
            uss["os"] = self.uss[6]
        return uss
        
    def cmd_append(self, cmd):
        if cmd is None:
            return
        self.cmds += cmd
        
    def recv(self):
        if self.pipe_uss.poll():
            self.uss = self.pipe_uss.recv()
        if self.pipe_comm.poll():
            self.req = self.pipe_comm.recv()

    def batt_check(self):
        self.cmds += self.batt.generate_command(self.req["btA"], self.req["btB"])

    def cmds_send(self):
        for cmd in self.cmds:
            print(cmd)
            self.q.put(cmd)

if __name__ == '__main__':
    main = Main()
    main.start()
    print('launched')
    import time
    time.sleep(6)
    main.stop()
