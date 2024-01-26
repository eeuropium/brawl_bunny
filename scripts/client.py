from scripts.constants import *
import socket
import threading

class Client():
    def __init__(self):
        # define where to send data to
        self.server_address_port = (SERVER_IP, PORT)

        # creates client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM specifies its UDP

        # init default message
        self.message = ""

    def run_receive(self):
        receiving_thread = threading.Thread(target = self.receive)
        receiving_thread.start()

    def receive(self):
        while True:
            try:
                message, addr = self.client_socket.recvfrom(1024)
                print(addr)
                self.message = message.decode()
            except:
                pass

    def send(self, message):
        self.client_socket.sendto(message.encode(), self.server_address_port)

    def get_message(self):
        return self.message
