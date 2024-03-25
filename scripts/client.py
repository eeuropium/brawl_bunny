from scripts.constants import *
import socket
import threading
from uuid import getnode
import random

class Client():
    def __init__(self):
        # define where to send data to
        self.server_address_port = (SERVER_IP, PORT)

        # creates client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM specifies its UDP

        # init default message
        self.message = ""

        if TESTING or LOCAL_SERVER:
            self.mac_address = random.randint(0, int(1e6)) # fake mac address as a random integer
             # 1e6 is a float and some older python versions cannot do the randrange on a float so we convert it to int
        else:
            self.mac_address = getnode() # get actual mac address

    def run_receive(self):
        receiving_thread = threading.Thread(target = self.receive, daemon = True)
        # daemon true allows all threads to stop
        # without it, only the main thread will exit, the other threads will continue to work

        receiving_thread.start()

    def receive(self):
        while True:
            try:
                message, addr = self.client_socket.recvfrom(1024)
                self.message = message.decode()
            except:
                pass

    def send(self, state_prefix, message):
        message = state_prefix + message
        self.client_socket.sendto(message.encode(), self.server_address_port)

    def get_message(self):
        return self.message

    def get_mac_address(self):
        return self.mac_address
