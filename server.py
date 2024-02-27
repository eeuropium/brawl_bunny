from scripts.constants import *
from scripts.managers import EndStateTimer
from scripts.entity import *
from scripts.map import Map
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

        self.end_timer = EndStateTimer(3)

    def update(self, data, client_address):
        if self.end_timer.next_state(all(self.selection_map.values())):
            self.server.update_state(Gameplay)
            self.server.state.init_character_selections(self.selection_map)

        if not data:
            return

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

class Gameplay():
    def __init__(self, server):
        self.server = server
        self.map = Map("map2.json")

    def init_character_selections(self, selection_map):
        self.players = {}

        # correct order
        self.players[selection_map[0]] = OrbBunny()
        self.players[selection_map[1]] = NatureBunny()
        self.players[selection_map[2]] = AngelBunny()
        self.players[selection_map[3]] = ShadowBunny()

        # testing
        # self.players[selection_map[0]] = NatureBunny()
        # self.players[selection_map[1]] = ShadowBunny()
        # self.players[selection_map[2]] = OrbBunny()
        # self.players[selection_map[3]] = AngelBunny()

    def update(self, data, client_address):
        if not data:
            return

        # splitting up inputs
        player_number, message = data.split(":")
        player_number = int(player_number)

        # getting corresponding player object
        player = self.players[player_number]

        # get collision boxes to pass into player update later
        map_obj_collision_boxes = self.map.get_neighbouring_chunk_data(player.x, player.y, "map_obj_collision_boxes")
        map_obj_hitboxes = self.map.get_neighbouring_chunk_data(player.x, player.y, "map_obj_hitboxes")

        if player_number > TOTAL_PLAYERS // 2: # player is in red team
            enemies = [self.players[i] for i in range(1, TOTAL_PLAYERS // 2 + 1)] # +1 because self.players is a dictionary with one indexing
        else:
            enemies = [self.players[i] for i in range(TOTAL_PLAYERS // 2 + 1, TOTAL_PLAYERS + 1)]

        # update player with input received from client and map objects
        player.update(message, map_obj_collision_boxes, map_obj_hitboxes, enemies)

        # print(self.players[player_number].x, self.players[player_number].y)

    def broadcast(self, client_address):
        s = ""

        for player_number, player_object in self.players.items():
            s += str(player_number) + ":" + player_object.get_server_send_message()
            s += "|"

        self.server.send(s[:-1], client_address)

class Server():
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM specifies its UDP
        self.server_socket.bind((SERVER_IP, PORT))

        self.state = MatchMaking(self)
        # self.state = Gameplay(self) # for testing

        self.state_prefix = STATE_PREFIX_MAP[self.state.__class__.__name__]

    def run(self):
        while True:
            self.state_prefix = STATE_PREFIX_MAP[self.state.__class__.__name__]
            data, client_address = self.receive()

            # update information server is holding
            self.state.update(data, client_address)

            # send updated information to this client
            self.state.broadcast(client_address)

    def receive(self):
        data, client_address = self.server_socket.recvfrom(1024) # receive data from client
        data = data.decode()

        # print(data)

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


if __name__ == "__main__":
    server = Server()
    server.run()
