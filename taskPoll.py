import pyximport; pyximport.install()
from uss import Uss
from ptask import ProcessTask
from time import sleep


class Poll(ProcessTask):
    """
    超音波センサから値を取得するタスクです。一定周期でポーリングを行います。
    """
    
    INTERVAL = 0.01

    def __init__(self, pipe=None):
        """
        コンストラクタです。
        """
        ProcessTask.__init__(self)
        self.uss = Uss()

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.uss.get()
        self.send(self.uss.vals)

if __name__ == '__main__':
    poll = Poll()
    p = poll.set_pipe()
    poll.start()
    print('launched')
    for _ in range(5):
        if p.poll():
            print(p.recv())
        else:
            print(None)
        sleep(1)
