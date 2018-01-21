#!/usr/bin/env python

import pyximport; pyximport.install()
from taskMain import Main
from taskPoll import Poll
from taskComm import Communication
from time import sleep

import logging
import logging.config
logging.config.fileConfig('logging.conf')


if __name__ == '__main__':
    poll = Poll()
    pollPipe = poll.set_pipe()
    poll.start()
    comm = Communication()
    commPipe = comm.set_pipe()
    comm.start()
    main = Main(pollPipe, commPipe, comm.q)
    main.start()
    print("Start Pilot")
    input("Enter to STOP")
    print("Stop Pilot")
    main.stop()
    poll.stop()
    comm.stop()
    print("bye")
