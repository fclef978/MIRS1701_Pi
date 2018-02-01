import pyximport; pyximport.install()
from ptask import ProcessTask
from request import Request
from time import sleep, time

import logging


class Communication(ProcessTask):
    """
    Arduinoとの通信タスクです。ポーリングや命令の送信を行います。
    """
    INTERVAL = 0.11

    def __init__(self):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        self.set_queue()
        ProcessTask.__init__(self)
        self.req = Request(self.q)

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.req.get()
        self.send(self.req.vals)
        if self.req.btnL.state:
            if not self.q.empty():
                self.q.get()
            if not self.q.empty():
                self.q.get()
            self.q.put(["stop"])
        self.req.put()


if __name__ == '__main__':
    comm = Communication()
    p = comm.set_pipe()
    q = comm.q
    comm.start()
    print('launched')
    for _ in range(5):
        if p.poll():
            print(p.recv())
            if _ == 3:
                q.put(["reset"])
        else:
            print(None)
        sleep(1)
    comm.stop()
