from taskMain import Main
from taskPoll import Poll
from taskComm import Communication

if __name__ == '__main__':
    main = Main()
    poll = Poll()
    comm = Communication()
    main.start()
    poll.start()
    comm.start()

    import time
    time.sleep(10)

    main.stop()
    poll.stop()
    comm.stop()
