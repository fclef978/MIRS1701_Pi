#!/usr/bin/env python

"""
起動および、各種タスクの生成を行うモジュールです。

:author: 鈴木宏和
"""

from taskMain import Main
from taskPoll import Poll
from taskComm import Communication
from time import sleep


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
    comm.req.arduino.reset_pin.off()
    comm.stop()
    print("bye")
