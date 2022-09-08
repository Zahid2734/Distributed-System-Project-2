import fcntl
import time
import Queue
import socket
from thread import *

filename = "test_file.txt"
lock_stat = False
current_queue = Queue.Queue()
lock_file = open(filename, 'r+')
buffer_size = 7


def get_lock(data, address):
    global lock_stat, current_queue, lock_file
    if lock_stat:
        print "current address [" + str(address) + "] Locking unavailable"
        current_queue.put((data, address))
        data.send("REJECT")
    else:
        if current_queue.empty():
            print "current address [" + str(address) + "] locking granted"
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            lock_stat = True
            data.send("ACCESS")
        else:
            queue_connection = current_queue.get()
            print "data processing from queue:", queue_connection[1]
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            lock_stat = True
            queue_connection[0].send("ACCESS")
            print "current address [" + str(queue_connection[1]) + "] locking granted"
    time.sleep(5)
    return


def lock_release(data, address):
    print "current address [" + str(address) + "] locking release"
    global lock_stat, current_queue, lock_file
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_stat = False
    data.send("Released")
    return


def threaded(data, address):
    for i in range(100):
        value = data.recv(buffer_size)
        print "[" + str(address) + "]Received command: ", value
        input_values = value.split(' ')
        if input_values[0] == "ACQUIRE":
            get_lock(data, address)
        elif input_values[0] == "RELEASE":
            lock_release(data, address)
        else:
            continue


def main():
    HOST = "127.0.0.1"
    PORT = 8080

    s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "server on at port %s and server %s" % (PORT, HOST)
    s_socket.bind((HOST, PORT))
    s_socket.listen(5)

    while True:
        print "waiting for connection.."
        connection, data = s_socket.accept()
        print "Got connection from ", data
        print "Sending acknowledgment.."
        connection.send("ACK")
        start_new_thread(threaded, (connection, data,))

    s_socket.close()


if __name__ == '__main__':
    main()


