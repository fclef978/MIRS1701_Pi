from ttask import PeriodicTask
from time import sleep
from battery import Battery
from run2 import Run
from gpio import IO

import logging


class Main(PeriodicTask):
    """
    メインタスクです。センサーから値を取得して走行します。
    """
    INTERVAL = 0.1

    def __init__(self, uss, comm):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        
        self.pipe_uss = uss
        self.pipe_comm = comm
        self.uss = []
        self.req = {}
        
        sleep(1)  # 先に起動すると困る
        PeriodicTask.__init__(self)
        
        self.cmds = []
        
        self.recv()
        self.batt = Battery(self.req["btA"], self.req["btB"])
        self.movement = Run()
        
        self.ms = []
        for pin in IO.PIN:
            print (pin)
            self.ms.append(IO(pin, IO.IN, True))
        self.ms = tuple(self.ms)

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.cmds = []
        self.recv()
        self.movement.set_val(True, self.uss)
        cmd = self.movement.straight()
        self.cmds += cmd
        self.batt_check()
        self.cmds_send()
        
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
            print (cmd)
            (cmd)

if __name__ == '__main__':
    main = Main()
    main.start()
    print('launched')
    import time
    time.sleep(6)
    main.stop()
