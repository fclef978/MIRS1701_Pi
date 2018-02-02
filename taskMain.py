import pyximport; pyximport.install()
from ttask import PeriodicTask
from time import sleep
from battery import Battery
from run import Run
from gpio import IO
from databox import DataBox

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
        self.is_left = True
        self.is_init = True
        self.data = DataBox()
        self.data.is_left = self.is_left
        PeriodicTask.__init__(self)

    def init(self):
        self.cmds = []
        while self.req == {} or self.uss == []:
            self.recv()
            sleep(0.01)
        while True:
            try:
                self.batt = Battery(self.req["btA"], self.req["btB"])
            except KeyError:
                continue
            break
        self.movement = Run(self.data)
        for pin in IO.PIN:
            self.ms.append(IO(pin, IO.IN, True))
        self.ms = tuple(self.ms)
    
    def work(self):
        """
        主となる関数です。
        シンプルに実装したい。
        :return: None
        """
        print(self.data.is_left)
        #print(self.data.ard)
        print(self.data.uss)
        self.cmds = []
        self.recv()
        self.data.set_value(self.uss, self.req)
        self.cmds += self.movement.execute()
        self.batt_check()
        self.cmds_send()
        # print(self.data.uss, self.cmds, self.movement.state.state, self.data.ard)
        
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
            self.q.put(cmd)
