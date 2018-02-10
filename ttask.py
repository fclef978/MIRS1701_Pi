"""
マルチスレッドを行うためのモジュールです。

:author: 鈴木宏和
"""

from abc import ABCMeta, abstractclassmethod
from threading import Thread
from time import sleep, time


class PeriodicTask(Thread, metaclass=ABCMeta):
    """
    スレッドを生成、管理するための抽象クラスです。継承して使います。
    workメソッドとINTERVAL属性をオーバーライドすれば周期INTERVALでworkメソッドが何度も実行されます。
    タスクを開始するにはstartメソッドを実行してください。また、タスクを停止するにはstopメソッドを実行してください。
    なお、workメソッドの実行時間がINTERVALよりも長い場合、その分周期が伸びます。

    このクラス自体がthreading.Threadを継承しています。そのため、Threadと名前が衝突がしないようにしてください。
    """
    #: 周期を表す属性です。
    INTERVAL = 1

    def __init__(self):
        """
        コンストラクタです。スレッドの初期化をします。
        """
        Thread.__init__(self)  # スレッド初期化
        self.alive = True
        self.logger.info("Thread Start")

    def __del__(self):
        """
        デストラクタです。スレッドを止めます。

        :return: なし
        """
        self.stop()

    def stop(self):
        """
        スレッドを止めるメソッドです。

        :return: なし
        """
        self.alive = False

    def run(self):
        """
        startメソッド実行したときに走るメソッドです。
        workメソッドを繰り返し実行します。

        :return: なし
        """
        self.init()
        while self.alive:  # 生存してたらループ
            start = time()
            t = Thread(target=self.work)  # work()を実行するタスクの生成
            t.start()
            sleep(self.INTERVAL - (time() - start))
            t.join()
        self.logger.info("Runner Stop")

    @abstractclassmethod
    def work(self):
        """
        タスクの本体となるメソッドです。
        抽象メソッドです。

        :return: なし
        """
        pass

    @abstractclassmethod
    def init(self):
        """
        タスクを実行する際、様々な初期化処理を行うメソッドです。
        抽象メソッドです。

        :return: なし
        """
        pass
