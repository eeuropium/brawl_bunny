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

        if USE_MAP == 3:
            self.map = Map("map3.json")
        else:
            self.map = Map("map2.json")

        ''' Match Data '''
        self.match_timer = LimitTimer(MATCH_DURATION)
        self.match_timer.start()

        self.respawn_timers = [LimitTimer(RESPAWN_WAIT_TIME + 1) for i in range (TOTAL_PLAYERS)]

        self.blue_score = 0
        self.red_score = 0

        self.match_end_timer = LimitTimer(MATCH_END_WAIT_TIME)

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

    def get_match_ended(self):
        return self.blue_score == KILLS_TO_WIN or self.red_score == KILLS_TO_WIN or self.match_timer.is_over()

    def update(self, data, client_address):
        if not data or self.get_match_ended():
            return

        # splitting up inputs
        player_number, message = data.split(":")
        player_number = int(player_number)

        # getting corresponding player object
        player = self.players[player_number]

        # get collision boxes to pass into player update later
        map_obj_collision_boxes = self.map.get_neighbouring_chunk_data(player.x, player.y, "map_obj_collision_boxes")
        map_obj_hitboxes = self.map.get_neighbouring_chunk_data(player.x, player.y, "map_obj_hitboxes")

        # get list of enemies
        if player_number > TOTAL_PLAYERS // 2: # player is in red team
            enemies = [self.players[i] for i in range(1, TOTAL_PLAYERS // 2 + 1)] # +1 because self.players is a dictionary with one indexing
        else:
            enemies = [self.players[i] for i in range(TOTAL_PLAYERS // 2 + 1, TOTAL_PLAYERS + 1)]

        # update player with input received from client and map objects
        player.update(message, map_obj_collision_boxes, map_obj_hitboxes, enemies)

        # calculate match score by checking if player has just died
        respawn_timer = self.respawn_timers[player_number - 1]

        if respawn_timer.is_active() and respawn_timer.is_over():
            respawn_timer.end()

        if not respawn_timer.is_active() and player.health == 0:
            respawn_timer.start()

            # check which team the player belongs to and inrcement the score of the opposite team
            if player_number <= TOTAL_PLAYERS // 2: # blue died, red score increments
                self.red_score += 1
            else:
                self.blue_score += 1 # red died, blue score increments

    def broadcast(self, client_address):
        if not self.match_end_timer.is_active():
            s = ""

            for player_number, player_object in self.players.items():
                match_data = [player_number, self.blue_score, self.red_score, int(MATCH_DURATION - self.match_timer.time_elapsed())]
                s += ','.join([str(e) for e in match_data]) + ":" + player_object.get_server_send_message()
                s += "|"


            s = s[:-1] # remove the last "|" separator

            if self.get_match_ended():
                self.match_end_timer.start()
        else:
            s = f"ENDED,{self.blue_score},{self.red_score}"

            if self.match_end_timer.is_over():
                if self.blue_score == self.red_score:
                    winning_team = "D" # D for draw
                elif self.blue_score > self.red_score:
                    winning_team = "B" # B for blue team
                else:
                    winning_team = "R" # R for red team

                self.server.update_state(EndScreen)
                self.server.state.init_result_prefix(winning_team)

        self.server.send(s, client_address)

class EndScreen():
    def __init__(self, server):
        self.next_state_timer = LimitTimer(1)
        self.next_state_timer.start()

        self.server = server

    def init_result_prefix(self, prefix):
        self.result_prefix = prefix

    def update(self, data, client_address):
        if self.next_state_timer.is_active() and self.next_state_timer.is_over():
            self.server.update_state(MatchMaking)

    def broadcast(self, client_address):
        self.server.send(self.result_prefix, client_address)

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
