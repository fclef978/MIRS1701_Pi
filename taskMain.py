"""
メインタスクです。センサーから値を取得して走行します。

:author: 鈴木宏和
"""

from ttask import PeriodicTask
from time import sleep
from battery import Battery
from run import Run
from gpio import IO
from databox import DataBox

import logging


class Main(PeriodicTask):
    """
    メインタスクを実現するクラスです。
    ttask.PeriodicTaskを継承して、マルチスレッドを利用した精度の高い周期実行を行います。
    """
    #: 実行周期です。
    INTERVAL = 0.1

    def __init__(self, uss, comm, q):
        """
        コンストラクタです。

        :param Connection uss: taskPollとのConnectionオブジェクトです。
        :param Connection comm: taskCommとのConnectionオブジェクトです。
        :param Queue q: taskCommとのQueueオブジェクトです。
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
        """
        タスクを開始する際に初期化を行うメソッドです。

        :return: なし
        """
        self.cmds = []
        while self.req == {} or self.uss == []:
            self.__recv()
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
        タスクの本体となるメソッドです。

        :return: なし
        """
        self.cmds = []
        self.__recv()
        self.data.set_value(self.uss, self.req)
        self.cmds += self.movement.execute()
        self.__batt_check()
        self.__cmds_send()
        
    def __cmd_append(self, cmd):
        if cmd is None:
            return
        self.cmds += cmd
        
    def __recv(self):
        if self.pipe_uss.poll():
            self.uss = self.pipe_uss.recv()
        if self.pipe_comm.poll():
            self.req = self.pipe_comm.recv()

    def __batt_check(self):
        self.cmds += self.batt.generate_command(self.req["btA"], self.req["btB"])

    def __cmds_send(self):
        for cmd in self.cmds:
            self.q.put(cmd)
