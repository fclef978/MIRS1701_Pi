from task import Task
from uss import uss
from request import req
from time import sleep

import logging


class Main(Task):
    """
    メインタスクです。センサーから値を取得して走行します。
    """
    INTERVAL = 2

    def __init__(self):
        """
        コンストラクタです。
        """
        self.logger = logging.getLogger(__name__)
        self.num = 0
        sleep(1)  # 先に起動すると困る
        Task.__init__(self)

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        self.num += 1;

if __name__ == '__main__':
    main = Main()
    main.start()
    print('launched')
    import time
    time.sleep(6)
    main.stop()
