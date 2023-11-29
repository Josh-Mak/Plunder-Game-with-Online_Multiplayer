import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.0.0.12"
        self.port = 5050
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    # returns is a number to figure out if client is player 1 (0) or player 2 (1)
    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048 * 4))
        except socket.error as e:
            print(e)
