from scripts.constants import *
import socket


class Server():
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM specifies its UDP
        self.server_socket.bind((SERVER_IP, PORT))

    def run(self):
        while True:
            data, client_address = self.receive()
            self.update(data, client_address)
            self.broadcast(client_address)

    def receive(self):
        data, client_address = self.server_socket.recvfrom(1024) # receive data from client
        data = data.decode()

        return data, client_address

    def send(self, message, client_address):
        self.server_socket.sendto(message.encode(), client_address)

    def update(self, *args):
        self.matchmaking(*args)

    def matchmaking(self, data, client_address):
        print(data, client_address)

    def broadcast(self, client_address):
        self.send("0", client_address)

server = Server()
server.run()
