from abc import ABCMeta, abstractclassmethod
from multiprocessing import Process, Pipe, Queue, Event
from time import sleep


class ProcessTask(Process):

    INTERVAL = 1

    def __init__(self):
        self.pipe = None
        self.buf = {}
        self.killer = Event()
        Process.__init__(self)

    def __del__(self):
        """
        デストラクタです。スレッドを止めます。
        :return: None
        """
        self.stop()

    def set_pipe(self, duplex=True):
        r, s = Pipe(duplex)
        self.pipe = r
        return s

    def set_queue(self):
        self.q = Queue()
        return self.q
        
    def stop(self):
        self.killer.set()

    def is_dead(self):
        return self.killer.is_set()

    def run(self):
        while not self.is_dead():
            self.work()
            sleep(self.INTERVAL)

    @abstractclassmethod
    def work(self):
        """
        タスクの本体です。
        抽象メソッドです。
        :return: None
        """
        pass

    def recv(self):
        if self.pipe.poll():
            self.buf = self.pipe.recv()
            return self.buf
        else:
            return False

    def send(self, data):
        self.pipe.send(data)
