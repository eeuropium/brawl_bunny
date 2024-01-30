from scripts.constants import *
import socket

# does not work for list maps
def map_to_string(map):
    s = ""

    for key, value in map.items():
        s += str(key)
        s += ":"
        s += str(value)
        s += ","

    return s[:-1]

class MatchMaking():
    def __init__(self, server):
        super().__init__()

        self.server = server
        self.mac_playernum_map = {}

        self.okay_next_state = [False for i in range(4)]

    def update(self, data, client_address):
        if not data:
            return

        if len(data) == 4 and data[:2] == "OK":
            ok_text, player_number = data.split(":")

            self.okay_next_state[int(player_number) - 1] = True

        else:
            client_mac = data

            if client_mac not in self.mac_playernum_map.keys():
                self.mac_playernum_map[client_mac] = len(self.mac_playernum_map) + 1

        if all(self.okay_next_state):
            self.server.update_state(CharacterSelection)

    def broadcast(self, client_address):
        map_string = map_to_string(self.mac_playernum_map)
        self.server.send(map_string, client_address)

class CharacterSelection():
    def __init__(self, server):
        self.server = server

        # selection index to player number map
        self.selection_map = {i:0 for i in range(4)}

        # self.selection_map = {i:-1 for i in range(1, 5)} # player number to selection index map

    def update(self, data, client_address):
        if not data:
            return

        print(data)
        player_number, selection_index = map(int, data.split(":"))

        # condition1: checks that player is making a request
        # condition2: character that the client wants to select is not selected yet, client is allowed to select this character
        if selection_index != -1 and self.selection_map[selection_index] == 0:
            # assign new selection to player
            self.selection_map[selection_index] = player_number

            # remove previous selection of this player
            for index in self.selection_map.keys():
                if index != selection_index and self.selection_map[index] == player_number:
                    self.selection_map[index] = 0

    def broadcast(self, client_address):
        map_string = map_to_string(self.selection_map)

        self.server.send(map_string, client_address)


class Server():
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM specifies its UDP
        self.server_socket.bind((SERVER_IP, PORT))

        self.state = MatchMaking(self)
        self.state_prefix = STATE_PREFIX_MAP[self.state.__class__.__name__]

    def run(self):
        while True:
            self.state_prefix = STATE_PREFIX_MAP[self.state.__class__.__name__]
            data, client_address = self.receive()

            print(data)

            # update information server is holding
            self.state.update(data, client_address)

            # send updated information to this client
            self.state.broadcast(client_address)

    def receive(self):
        data, client_address = self.server_socket.recvfrom(1024) # receive data from client
        data = data.decode()

        print(data)

        # return empty string if client not in the same state as server
        if data[0] != self.state_prefix:
            return "", client_address

               # remove state prefix from message
        return data[1:], client_address

    def send(self, message, client_address):
        message = self.state_prefix + message

        self.server_socket.sendto(message.encode(), client_address)

    def update_state(self, new_state):
        self.state = new_state(self)


    # def update(self, *args):
    #     self.matchmaking(*args)
    #
    # def matchmaking(self, data, client_address):
    #     print(data, client_address)
    #
    # def broadcast(self, client_address):
    #     self.send("0", client_address)

if __name__ == "__main__":
    server = Server()
    server.run()
