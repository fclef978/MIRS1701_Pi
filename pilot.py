from taskMain import Main
from taskPoll import Poll
from taskComm import Communication
from time import sleep

import logging
import logging.config
logging.config.fileConfig('logging.conf')


if __name__ == '__main__':
    main = Main()
    poll = Poll()
    comm = Communication()
    main.start()
    poll.start()
    comm.start()
    print("Start Pilot")
    sleep(5)
    print("Stop Pilot")
    main.stop()
    poll.stop()
    comm.stop()
    print("bye")
