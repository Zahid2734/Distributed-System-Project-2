import random
import socket
import time
import Queue
from threading import Thread
import pickle
import copy

multicast_ports = [6001, 6002, 6003]
multicast_group = "127.0.0.1"
PID = 0
own_port = 6001
event_queue = Queue.Queue()


class Test:
    vec = [0] * 3
    ppid = 1


mine = Test()


class ReceiverThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.bind((multicast_group, own_port))

        while True:
            data, address = sock.recvfrom(1024)
            event = pickle.loads(data)
            if event.ppid != PID + 1:
                event_queue.put(event)


class ProcessingThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def run(self):

        while True:
            try:
                event = event_queue.get()
                v = event.vec
            except Exception as e:
                continue

            for i in range(len(v)):
                if v[i] > mine.vec[i]:
                    if i == 2:
                        print("the received event is 3.{}".format(v[i]))
                    elif i == 1:
                        print("the received event is 2.{}".format(v[i]))
                    else:
                        pass
            for i in range(len(v)):
                mine.vec[i] = max(mine.vec[i], v[i])


class EventThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.event_count = 0

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        no = 0
        while True:
            rand_number = random.randint(0, 1000000)
            if rand_number == 0 and no <= 9:
                no = no + 1
                self.event_count += 1
                mine.vec[PID] = self.event_count
                event = copy.deepcopy(mine)
                event.vec = copy.deepcopy(mine.vec)
                event.ppid = copy.deepcopy(mine.ppid)
                event.vec[PID] = event.vec[PID]
                time.sleep(3)
                print("send event, updating event 1.{}".format(event.vec[0]))
                x = pickle.dumps(event)
                for port in multicast_ports:
                    sock.sendto(x, (multicast_group, port))



if __name__ == "__main__":
    rcv_thread = ReceiverThread()
    send_thread = EventThread()
    process_thread = ProcessingThread()
    rcv_thread.start()
    send_thread.start()
    process_thread.start()
