import socket


HOST = "127.0.0.1"
PORT = 8080
buffer_size = 7

file_name = "test_file.txt"


def get_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Connecting to port %s and server %s"%(PORT,HOST)
    server_socket.connect((HOST, PORT))
    ack = server_socket.recv(buffer_size)
    if ack == "ACK":
        print "Connected to server and got acknowledgments: ",ack
        return server_socket


def main():
    connect = get_socket()
    for i in range(10):
        print "Requesting for access to the server..."
        connect.send("ACQUIRE")
        data = connect.recv(buffer_size)
        if data == "ACCESS":
            print "Got Access to the file. Editing File..."
            file_obj = open(file_name, 'r+')
            content = int(file_obj.read())
            file_obj.seek(0)
            file_obj.write(str(content+1))
            file_obj.close()
            print "             After editing, file content is:               " + str(content + 1)
            connect.send("RELEASE")
            data = connect.recv(buffer_size)
        elif data == "REJECT":
            print "Access is denied by server. retry again.."

    print "Closing connect..."
    connect.close()

if __name__ == '__main__':
    main()