# Kamil Şen

import socket
import threading
import uuid
import random
import string
import time
import os
import sys
import atexit
import signal
import syslog

# Host and Port informations of server.
LOCALHOST = "127.0.0.1"
PORT = 6622

# Rooms and players of server as dictionaries.
rooms = {}
players = {}

# A code generated from server and sent to clients on connection. It will be 
# used for transfering result of game as a layer of cheat protection.
c_s_code = str(uuid.uuid4())

# Function that generates random 5 character string with ascii uppercase characters and digits.
def get_rand_five():
    id = ''
    for i in range(5):
        id = id + (random.choice(string.ascii_uppercase + string.digits))
    return id   

# Function that generates random 5 character string that is not already exist as a room id
# with ascii uppercase characters and digits.
def get_room_ID():
    while True:
        id = get_rand_five()
        if id not in rooms:
            break
    return id   

# Function that generates random 5 character string that is not already exist as a player id
# with ascii uppercase characters and digits.
def get_player_ID():
    while True:
        id = get_rand_five()
        if id not in players:
            break
    return id

# Function that used for get key value of a room which is room id with a given value.
def roomid_by_roominfo(info):
    for roomid, roominfo in rooms.items():
        if roominfo == info:
            return roomid

# Class that operations of a thread that responds to a client
class ClientThread(threading.Thread):

    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        syslog.syslog("New connection added: " + str(clientAddress))

    # Function that creates a room for a game with given clients player id and room type
    def init_new_game(self,clients_player_ID,room_type):
        new_room = get_room_ID()
        rooms[new_room] = {}
        rooms[new_room]["room_players"] = []
        rooms[new_room]["room_type"] = room_type
        rooms[new_room]["room_players"].append(clients_player_ID)
        rooms[new_room]["emptyslot"] = "1"
        rooms[new_room]["room_status"] = "new"
        rooms[new_room]["results"] = []
        players[clients_player_ID]["room_id"] = new_room 

    # Function thats going to be executed when client exits.
    def client_exit(self, clients_player_ID): 
        try:
            # If player is alone in the room, room is going to be deleted
            if rooms[players[clients_player_ID]["room_id"]]["emptyslot"] == "1":
                del rooms[players[clients_player_ID]["room_id"]]
            # If there is two player in the room player is removed from rooms player list 
            # And other informations about room changed according to its new status
            else:
                rooms[players[clients_player_ID]["room_id"]]["emptyslot"] = "1"
                rooms[players[clients_player_ID]["room_id"]]["room_players"].remove(clients_player_ID)
                rooms[players[clients_player_ID]["room_id"]]["room_status"] = "new"
                rooms[players[clients_player_ID]["room_id"]]["results"].clear
        except:
            pass
        
        # If client entered to game once and have an entry on players list deletes it from players list
        try:
            del players[clients_player_ID]
        except:
            pass    
        
        # Sends exit sign back. Used on main menu exits of client.
        try:
            server_res = "EXIT"
            self.csocket.send(bytes(server_res,'utf-8'))
        except:
            pass   
    
    # Function that runs on end of a game. When both players left deletes room.
    def end_of_game(self, clients_player_ID):         
        try:
            if rooms[players[clients_player_ID]["room_id"]]["emptyslot"] == "1":
                del rooms[players[clients_player_ID]["room_id"]]
            else:
                rooms[players[clients_player_ID]["room_id"]]["emptyslot"] = "1"
                rooms[players[clients_player_ID]["room_id"]]["room_players"].remove(clients_player_ID)
                rooms[players[clients_player_ID]["room_id"]]["room_status"] = "delete"
                rooms[players[clients_player_ID]["room_id"]]["results"].clear
        except:
            pass
    
    # Function that runs while a player waiting a match for a game.
    # Returns True if players exits while waiting, False if players got a match.
    def wait_match(self,clients_player_ID):
        is_exit = False  
        # Waits in loop until another player enters to the room
        while rooms[players[clients_player_ID]["room_id"]]["room_status"] != "match":                 
            try:
                self.csocket.setblocking(False)
                recv_data = self.csocket.recv(4096)
                client_choice = recv_data.decode()
                cc_splited = client_choice.split()
                # If player exits while waiting starts client_exit
                if cc_splited[0] == "EXIT":
                    is_exit = True
                    self.csocket.setblocking(True)
                    self.client_exit(clients_player_ID)
                    break
            except:
                pass
            self.csocket.setblocking(True)
            time.sleep(1)
        return is_exit              

    # Function that runs while a player waiting for result of a game.
    # Returns True if players exits while waiting, False if results arived or player waited 30 seconds for results.
    def wait_result(self,clients_player_ID):        
        is_exit = False
        counter = 0
        # Waits in loop for both players have a result in rooms result list.
        # If player waits 30 seconds for result of other player its assumed other player left and players exits loop
        while len(rooms[players[clients_player_ID]["room_id"]]["results"]) != 2 and counter < 30:
            try:
                self.csocket.setblocking(False)
                recv_data = self.csocket.recv(4096)
                client_choice = recv_data.decode()
                cc_splited = client_choice.split()
                # If player exits while waiting starts client_exit
                if cc_splited[0] == "EXIT":
                    is_exit = True
                    self.client_exit(clients_player_ID)
                    break
            except:
                pass
            self.csocket.setblocking(True)
            counter = counter + 1

            time.sleep(1)    
        return is_exit   

    # Function that defines servers main menu and game loop for a client.
    def menu_opt(self,clients_player_ID):
        
        # Holds data thats recieved from client.
        client_choice = ""
        # Holds data going to be sent to a client.
        server_res = ""

        while True:
            recv_data = self.csocket.recv(4096)
            client_choice = recv_data.decode()
            cc_splited = client_choice.split()
            # Only accepting not empty data from here.
            while len(cc_splited)  <= 0:
                recv_data = self.csocket.recv(4096)
                client_choice = recv_data.decode()
                cc_splited = client_choice.split()

            # If first element of splited recieved data is NEWGAME clients wants to create a new private game.
            if cc_splited[0] == "NEWGAME":
                # Room for game created.
                self.init_new_game(clients_player_ID,"private")
                # WAITMATCH sign with room id to share sent to client
                server_res = "WAITMATCH" + " " + (players[clients_player_ID]["room_id"])
                self.csocket.send(bytes(server_res,'utf-8'))
                # Waiting for a match.
                exit_check = self.wait_match(clients_player_ID)
                # If wait ends with exit conditition break the loop
                if exit_check == True:
                    break
                # If reached at this point cleint have a match so sending MATCH sign
                server_res = "MATCH"
                self.csocket.send(bytes(server_res,'utf-8'))

            # If first element of splited recieved data is NEWGAME clients wants to join a private game.
            if cc_splited[0] == "JOIN":
                # Second element of join sign is room id, if room with that id exist and not full player enter to room.
                if cc_splited[1] in rooms and rooms[cc_splited[1]]["emptyslot"] == "1":
                    rooms[cc_splited[1]]["room_players"].append(clients_player_ID)
                    rooms[cc_splited[1]]["emptyslot"] = "0"
                    rooms[cc_splited[1]]["room_status"] = "match"
                    players[clients_player_ID]["room_id"] = cc_splited[1]
                    # Player entered a room that created before so have a match at this point.
                    server_res = "MATCH"
                    self.csocket.send(bytes(server_res,'utf-8'))

                   
                else:
                    server_res = "CANTJOIN"
                    # If room with room id that recieved from client does not exit a sign according to that sent to client.
                    if cc_splited[1] not in rooms:
                        server_res = server_res + " " + ("NOTEXIST")
                    # If room with room id that recieved from client is full a sign according to that sent to client.
                    else:
                        server_res = server_res + " " + ("FULL")    
                    self.csocket.send(bytes(server_res,'utf-8'))
            
            # If first element of splited recieved data is RANDOMGAME clients wants to join a public game.
            if cc_splited[0] == "RANDOMGAME":
                room_found = 0
                # Searching for a room to join in rooms. If a public room with empty slot player joins to room
                for room in rooms.values():
                    if room["room_type"] == "public" and room["emptyslot"] == "1" :
                        room_found = 1
                        room["room_players"].append(clients_player_ID)
                        room["emptyslot"] = "0"
                        room["room_status"] = "match"
                        players[clients_player_ID]["room_id"] = roomid_by_roominfo(room)
                        # Since joining a room that exist client have a match at this point.
                        server_res =  "MATCH"
                        self.csocket.send(bytes(server_res,'utf-8'))
                # If there is no room available creating a new room.
                if room_found == 0:
                    self.init_new_game(clients_player_ID,"public")
                    # Sending client WAITMATCHRAND sign to wait a match.
                    server_res = "WAITMATCHRAND"
                    self.csocket.send(bytes(server_res,'utf-8'))
                    # Waiting for a match.
                    exit_check = self.wait_match(clients_player_ID)
                    # If wait ends with exit conditition break the loop
                    if exit_check == True:
                        break
                    server_res = "MATCH"
                    self.csocket.send(bytes(server_res,'utf-8'))

            # If first element of splited recieved data is RANDOMGAME clients wants to exit so client_exit called.
            if cc_splited[0] == "EXIT":
                self.client_exit(clients_player_ID)
                break
            
            # If first element of splited recieved data is RESULT client sending result of the game played.
            if cc_splited[0] == "RESULT":
                # Checking for c_s_code as a layer of cheat control.
                if cc_splited[1] == c_s_code:   
                    # Casting result that recieved as third element of splited recieved data to float.
                    client_result = float(cc_splited[2])
                    # Adding result to the results list of room.
                    rooms[players[clients_player_ID]["room_id"]]["results"].append(client_result)
                    # Waiting for a match.
                    is_exit = self.wait_result(clients_player_ID)
                    # If wait ends with exit conditition break the loop
                    if is_exit == True:
                        break
                    # Else both players result arrived to server or player that served by thread
                    # waited enough to server assume other player result not going to arrive.
                    else:
                        # If there is only 1 result in result list of room it win with other result not going to arrive option.
                        if len(rooms[players[clients_player_ID]["room_id"]]["results"]) == 1:
                            server_res = "WIN"
                        else:
                            # Finding other result than result of client served by thread.
                            for result in rooms[players[clients_player_ID]["room_id"]]["results"]:
                                if result != client_result:
                                    other_result = result
                                if result == client_result and result == 100000:
                                    other_result = result
                            # If client result is less than other result client player respond time is better.
                            # So client served by thread wins.
                            if client_result < other_result:
                                server_res = "WIN"
                            # With precision of results its safe to assume that result will 
                            # be different if not both players are cheated. So else player loses. 
                            else:
                                server_res = "LOSE"
                        # Ending the game and when last player left deleting the room.
                        self.end_of_game(clients_player_ID)      
                        # Sending sign of WIN or LOSE to client.
                        self.csocket.send(bytes(server_res,'utf-8'))

    # Overridden run method of thread class that starts thread activity     
    def run(self):
        syslog.syslog ("Connection from : " + str(clientAddress))
        server_res = "CONNECTED" + " " + (c_s_code)
        self.csocket.send(bytes(server_res,'utf-8'))
       
        clients_player_ID = get_player_ID()
        
        players[clients_player_ID] = {}
        players[clients_player_ID]["socket"] = self.csocket
        players[clients_player_ID]["room_id"] = ""
        
        self.menu_opt(clients_player_ID)

# Daemonizing part start

# File that contains pid's
pidfile = '_.pid'

try: 
    pid = os.fork() 
    if pid > 0:
        sys.exit(0) 
except OSError as e: 
    sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
    sys.exit(1)

os.setsid() 
os.umask(0) 

try: 
    pid = os.fork() 
    if pid > 0:
        sys.exit(0) 
except OSError as e: 
    sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
    sys.exit(1) 

syslog.syslog("Now acting as daemon.")
atexit.register(os.remove, pidfile)

# Redirect standard file descriptors
sys.stdout.flush()
sys.stderr.flush()
si = open(os.devnull, 'r')
so = open(os.devnull, 'a+')
se = open(os.devnull, 'a+')
os.dup2(si.fileno(), sys.stdin.fileno())
os.dup2(so.fileno(), sys.stdout.fileno())
os.dup2(se.fileno(), sys.stderr.fileno())

syslog.syslog("Redirected standard file descriptors.")

signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit())

syslog.syslog("Registered signal.")

# Writing pidfile.        
pid = str(os.getpid())
with open(pidfile,'w+') as pidfp:
    pidfp.write("%s\n" % pid)

# Daemonizing part end.    

# Starting server and waiting for requests.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
syslog.syslog("Server started and waiting for requests")

while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    # Creating a thread that responsible from a client and starting it.
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()