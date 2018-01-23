from abc import ABCMeta, abstractclassmethod
from threading import Thread
from time import sleep, time


class PeriodicTask(Thread, metaclass=ABCMeta):
    """
    タスクを生成するための抽象クラスです。継承して使ってください。
    継承先でwork()とINTERVALをオーバーライドすれば周期INTERVALでwork()が自動実行されます。
    タスクを開始するにはstart()を実行してください。
    """

    INTERVAL = 1  # 周期を設定する定数です。オーバーライドしてください。

    def __init__(self):
        """
        コンストラクタです。スレッドの初期化とイベントの設定をします。
        """
        Thread.__init__(self)  # スレッド初期化
        self.alive = True
        self.logger.info("Thread Start")

    def __del__(self):
        """
        デストラクタです。スレッドを止めます。
        :return: None
        """
        self.stop()

    def stop(self):
        self.alive = False

    def run(self):
        """
        start()が実行されたときに実行されます。
        周期INTERVALでイベントを送り、work()を実行します。
        :return: None
        """
        Thread(target=self.init).start()  # work()を実行するタスクの生成
        while self.alive:  # 生存してたらループ
            start = time()
            Thread(target=self.work).start()  # work()を実行するタスクの生成
            sleep(self.INTERVAL - (time() - start))
        self.logger.info("Runner Stop")

    @abstractclassmethod
    def work(self):
        """
        タスクの本体です。周期INTERVALで実行されます。
        抽象メソッドです。
        :return: None
        """
        pass

    @abstractclassmethod
    def init(self):
        """
        タスクの本体です。周期INTERVALで実行されます。
        抽象メソッドです。
        :return: None
        """
        pass
