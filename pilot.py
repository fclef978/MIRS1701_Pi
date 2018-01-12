#!/usr/bin/python3

from taskMain import Main
from taskPoll import Poll
from taskComm import Communication
from time import sleep

import logging
import logging.config
logging.config.fileConfig('logging.conf')


if __name__ == '__main__':
    poll = Poll()
    comm = Communication()
    poll.start()
    comm.start()
    main = Main()
    main.start()
    print("Start Pilot")
    while True:
        pass
    print("Stop Pilot")
    main.stop()
    poll.stop()
    comm.stop()
    print("bye")
