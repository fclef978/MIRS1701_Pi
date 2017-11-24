from task import Task
from request import req


class Communication(Task):
    """
    Arduinoとの通信タスクです。一定周期でポーリングや命令の送信を行います。
    """
    INTERVAL = 1

    def __init__(self):
        """
        コンストラクタです。
        """
        Task.__init__(self)

    def work(self):
        """
        主となる関数です。
        :return: None
        """
        req.get()
        req.put()

if __name__ == '__main__':
    comm = Communication()
    comm.start()
    print('launched')
