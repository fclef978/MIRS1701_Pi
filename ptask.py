"""
マルチプロセスを行うためのモジュールです。

:author: 鈴木宏和
"""

from abc import ABCMeta, abstractclassmethod
from multiprocessing import Process, Pipe, Queue, Event
from time import sleep


class ProcessTask(Process, metaclass=ABCMeta):
    """
    プロセスを生成、管理するための抽象クラスです。継承して使います。
    workメソッドとINTERVAL属性をオーバーライドすれば周期INTERVALでworkメソッドが何度も実行されます。
    タスクを開始するにはstartメソッドを実行してください。また、タスクを停止するにはstopメソッドを実行してください。
    set_pipeメソッドやset_queueメソッドによって得られるConnectionオブジェクトやQueueオブジェクトを介してメインプロセスと通信を行ってください。
    なお、INTERVAL属性は、あくまで目安の周期であり、workメソッドの実際の実行周期はworkメソッドの実行時間に依存します。

    このクラス自体がmultiprocessing.Processを継承しています。そのため、Processと名前が衝突がしないようにしてください。
    また、multiprocessingの仕様で、一部マルチプロセスにできないオブジェクトがあります。
    実行時にPickle関係の例外が発生する場合はどこかに使用できないオブジェクトが使われているということになります。
    その場合はそのオブジェクトの使用を取りやめるほかに解決法がありません。
    """
    #: タスクを走らせる周期を表す属性です。単位はsecです。あくまで目安の周期なのであまりあてにはなりません。
    INTERVAL = 1

    def __init__(self):
        """
        コンストラクタです。
        """
        self.pipe = None
        self.buf = {}
        self.__killer = Event()
        Process.__init__(self)

    def __del__(self):
        """
        デストラクタです。スレッドを止めます。

        :return: None
        """
        self.stop()

    def set_pipe(self, duplex=True):
        """
        プロセス間通信のためのConnectionオブジェクトを生成するメソッドです。

        :param bool duplex: 双方向通信にするか否かを設定します。デフォルトはFalseです。双方向通信をしない場合は送信専用になります。
        :rtype: Connection
        :return: 通信用Connectionオブジェクトです。duplexがFalseの場合、送信専用になります。
        """
        r, s = Pipe(duplex)
        self.pipe = r
        return s

    def set_queue(self):
        """
        プロセス間通信のためのQueueオブジェクトを生成するメソッドです。

        :rtype: Queue
        :return: 通信用Queueオブジェクトです。
        """
        self.q = Queue()
        return self.q

    def stop(self):
        """
        プロセスを止めるメソッドです。メインプロセスからでも実行できます。

        :return: なし
        """
        self.__killer.set()

    def __is_dead(self):
        """
        プロセスが生存中か否か判定するメソッドです。

        :rtype: bool
        :return: 生存中ならTrue、stopされたらFalseを返します。
        """
        return self.__killer.is_set()

    def run(self):
        """
        startメソッド実行したときに走るメソッドです。
        workメソッドを繰り返し実行します。

        :return: なし
        """
        while not self.__is_dead():
            self.work()
            sleep(self.INTERVAL)

    @abstractclassmethod
    def work(self):
        """
        タスクの本体となるメソッドです。
        抽象メソッドです。

        :return: なし
        """
        pass

    def recv(self):
        """
        Connectionオブジェクトから値を受信するメソッドです。
        受信データはself.buf内に格納されます。

        :rtype: dict, bool
        :return: 成功したら受信データを、失敗したらFalseを返します。
        """
        if self.pipe.poll():
            self.buf = self.pipe.__recv()
            return self.buf
        else:
            return False

    def send(self, data):
        """
        Connectionオブジェクトにデータを送信するメソッドです。

        :param dict data: 送信するデータです、
        :return: なし
        """
        self.pipe.send(data)
