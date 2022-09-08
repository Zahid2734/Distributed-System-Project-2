import pickle
import random
import socket
import time
from threading import Thread

vector_ports = [6003, 6001]
vector_host = "127.0.0.1"
PID = 2
own_port = 6002
vector = [0, 0, 0]


class ReceiverThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global vector
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.bind((vector_host, own_port))

        while True:
            data, address = sock.recvfrom(1024)
            data = pickle.loads(data)
            vector = data
            print("RECEIVED: ", vector)


class EventThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global vector
        no = 0
        print("Please wait for some time to generate events")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        while True:
            # time.sleep(1)
            rand_number = random.randint(0, 1000000 )
            if rand_number == 0 and no <=5:
                no = no+1
                vector[PID - 1] += 1
                message = pickle.dumps(vector)
                print("[" + str(PID) + "]: ", vector)
                for port in vector_ports:
                    sock.sendto(message, (vector_host, port))
                time.sleep(4)


rcv_thread = ReceiverThread()
send_thread = EventThread()
rcv_thread.start()
send_thread.start()