"""
超音波センサから値を取得するタスクです。一定周期でポーリングを行います。

:author: 鈴木宏和
"""

from uss import Uss
from ptask import ProcessTask
from time import sleep


class Poll(ProcessTask):
    """
    I2C通信を行うタスクを実現するためのクラスです。
    ptask.ProcessTaskを継承して、マルチプロセスで動作しています。
    """
    #: 実行周期です。
    INTERVAL = 0.01

    def __init__(self):
        """
        コンストラクタです。
        """
        ProcessTask.__init__(self)
        self.uss = Uss()

    def work(self):
        """
        タスクの本体となるメソッドです。

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
            print(p.__recv())
        else:
            print(None)
        sleep(1)
