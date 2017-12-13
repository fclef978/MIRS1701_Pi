from uss import uss
from task import Task

import logging

class Poll(Task):
    """
    超音波センサから値を取得するタスクです。一定周期でポーリングを行います。
    """
    INTERVAL = 1

    def __init__(self):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        Task.__init__(self)

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        uss.get()

if __name__ == '__main__':
    poll = Poll()
    poll.start()
    print('launched')
