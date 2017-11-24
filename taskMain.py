from task import Task
from uss import uss
from request import req
from time import sleep


class Main(Task):
    """
    メインタスクです。センサーから値を取得して走行します。
    """
    INTERVAL = 4

    def __init__(self):
        """
        コンストラクタです。
        """
        Task.__init__(self)
        sleep(1)  # 先に起動すると困る

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        print(uss.vals)
        print(req.vals)
        req.order([2, 50, 10])

if __name__ == '__main__':
    main = Main()
    main.start()
    print('launched')
    import time
    time.sleep(6)
    main.stop()
