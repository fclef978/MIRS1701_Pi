from ptask import ProcessTask
from request import Request
from time import sleep, time

import logging


class Communication(ProcessTask):
    """
    Arduinoとの通信タスクです。一定周期でポーリングや命令の送信を行います。
    """
    INTERVAL = 0.1

    def __init__(self):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        ProcessTask.__init__(self)
        self.req = Request()
    
    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.req.get()
        self.send(self.req.vals)
        self.req.put()
        # print("debug")

if __name__ == '__main__':
    comm = Communication()
    p = comm.set_pipe()
    comm.start()
    print('launched')
    for _ in range(5):
        if p.poll():
            print(p.recv())
        else:
            print(None)
        sleep(1)
    comm.stop()
