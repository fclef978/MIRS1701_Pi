from task import Task
from uss import uss
from request import req
from time import sleep
from battery import Battery
from run2 import Run

import logging


class Main(Task):
    """
    メインタスクです。センサーから値を取得して走行します。
    """
    INTERVAL = 0.1

    def __init__(self):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        self.num = 0
        sleep(1)  # 先に起動すると困る
        Task.__init__(self)
        self.batt = Battery(req.vals["btA"], req.vals["btB"]);
        self.movement = Run()

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.num += 1;
        cmds = [];
        cmds += self.batt.generate_command(req.vals["btA"], req.vals["btB"])
        for cmd in cmds:
            print (cmd)
            req.order(cmd)
        x, th = self.movement.position(uss.vals, 1);
        req.order(["velocity", int(-th * 0.5), int(th * 0.5)])
        #req.order(["velocity", 100, 100])

if __name__ == '__main__':
    main = Main()
    main.start()
    print('launched')
    import time
    time.sleep(6)
    main.stop()
