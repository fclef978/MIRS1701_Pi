from abc import ABCMeta, abstractclassmethod
from multiprocessing import Process, Pipe
from time import sleep


class ProcessTask(Process):

    INTERVAL = 1

    def __init__(self):
        self.alive = True
        self.pipe = None
        self.buf = {}
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

    def is_kill(self):
        self.recv()
        if "terminate" in self.buf:
            if self.buf["terminate"]:
                return True
        return False

    def run(self):
        while self.alive:
            if self.is_kill():
                break
            self.work()
            sleep(self.INTERVAL)

    def stop(self):
        self.alive = False

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


def process_kill(pipe):
    pipe.send({"terminate": True})
