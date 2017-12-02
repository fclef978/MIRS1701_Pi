from task import Task
from uss import uss
from request import req
from time import sleep


class Main(Task):
    """
    メインタスクです。センサーから値を取得して走行します。
    """
    INTERVAL = 0.01

    def __init__(self):
        """
        コンストラクタです。
        """
        self.num = 0
        sleep(1)  # 先に起動すると困る
        Task.__init__(self)

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        print(req.vals)
        if self.num % 2 == 0:
            req.order(["Straight", 50, 10])
        else:
            req.order(["Stop"])
        self.num += 1

if __name__ == '__main__':
    main = Main()
    main.start()
    print('launched')
    import time
    time.sleep(6)
    main.stop()
