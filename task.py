from abc import ABCMeta, abstractclassmethod
from threading import Thread, Event
from time import sleep

import logging


class Task(Thread, metaclass=ABCMeta):
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
        self.e = Event()  # イベント生成
        self.alive = True  # 生存情報
        self.logger.info("Thread Start")

    def __del__(self):
        """
        デストラクタです。スレッドを止めます。
        :return: None
        """
        if self.alive:
            self.stop()  # 停止

    def run(self):
        """
        start()が実行されたときに実行されます。
        周期INTERVALでイベントを送り、work()を実行します。
        :return: None
        """
        t = Thread(target=self.thread)  # work()を実行するタスクの生成
        t.start()  # タスク実行
        while self.alive:  # 生存してたらループ
            self.e.set()  # イベント送信
            sleep(self.INTERVAL)  # 周期実行
        self.e.set()  # 終了時もイベント送信しないとwait()で引っかかる
        self.logger.info("Runner Stop")

    def stop(self):
        """
        スレッドを止めます。
        :return: None
        """
        self.alive = False
        self.logger.info("Send Stop Signal")

    def thread(self):
        """
        work()を実行します。周期を管理するrun()とは別タスクになっています。
        イベントが来るとスレッドが生存中かどうか確認してからwork()を実行します。
        :return:
        """
        while True:
            self.e.wait()  # イベント待ち
            if not self.alive:  # 生存確認
                self.logger.info("Thread Stop")
                return
            self.work()  # 実行
            self.e.clear()  # イベントクリア

    @abstractclassmethod
    def work(self):
        """
        タスクの本体です。周期INTERVALで実行されます。
        抽象メソッドです。
        :return: None
        """
        pass
