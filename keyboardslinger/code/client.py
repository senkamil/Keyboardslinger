# 260201024 - Kamil Şen Ceng 421 - Client - Final Project

import artfile
import time
import os
import socket
import sys
import select
import signal
from termios import tcflush, TCIFLUSH

# Host and Port information for connect to server.
SERVER = "127.0.0.1"
PORT = 6622

# This code going to be received from server on connection and will be used for
# transfering result of game to server as a layer of cheat protection. 
c_s_code = ""

# Valid inputs for main menu
valid_inputs = ["NEWGAME", "JOIN", "RANDOMGAME", "EXIT"]

# Function that used for clear console.
def console_clear():
    os.system('cls' if os.name=='nt' else 'clear')

# Function that used in game for cowboys walk away animation.
# At this point of the game sending an input is rule violation.
# If any input recieved function returns 1 which denotes rule violation, else returns 0 for no rule violation.
def print_cowboys():
    for i in range(len(artfile.slingers_list)):
        time.sleep(1.3)
        console_clear()
        print(artfile.slingers_list[i])
    if select.select([sys.stdin,],[],[],0.0)[0]:
        return 1
    else:
        return 0

# Function that prints main menu.
def print_startscreen():
        print(artfile.main_slingers)
        print(artfile.menu_choice)

# Function that used for get input from player and send them to server if input is valid according to valid_inputs list.
def send_input(socket):
    while True:
        send_inp = input()
        splited_inp = send_inp.split()
        if len(splited_inp) > 0:
            if splited_inp[0] not in valid_inputs:
                print("Please enter a valid input")
            if splited_inp[0] in valid_inputs:
                break
    socket.sendall(bytes(send_inp,'UTF-8'))

# Function that defines a duel in game. Returns players reaction time as float.
# Players reaction time is time passed from slinger_7 printed which is shoot indicator to player input.
def duel():

    # One of the players will be waiting for a match. So giving some time and countdown for being ready to game.
    for i in range(5):
        time.sleep(1.3)
        print("RIVAL KEYBOARDSLINGER ARRIVED, DUEL WILL START IN" + " " + str(5-i))

    # Printing cowboys walk away animation if this function do not returns 0 this indicates a rule violation occured.
    cheat = print_cowboys()
    if cheat > 0:
        # If player is tried to cheat and shoot while cowboys not apart this function returns 100000
        # This result is logically to high (1.15 days) and guarantees players loss also indicates player is a cheater
        return 100000

    # Calculating players reaction time
    t1 = time.perf_counter()
    inp = input()
    t2 = time.perf_counter()
    result = t2 - t1
    return result

# Function that used for wait on continue screen after game.
def con_wait():
    while True:
        if select.select([sys.stdin,],[],[],0.0)[0]:
            break

def main():  
    
    # Creating a socket and connecting to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))

    # A player can leave with closing terminal, ctrl-z command etc.
    # In this case server needed to be notified player is left.
    # This fucntion handles that kinds of exits.
    def signal_handle(signum, frame):
        try:
            if signum in [1, 2, 3, 15, 19, 20]:
                client.sendall(bytes("EXIT",'UTF-8'))
                sys.exit(0) 
        except:
            sys.exit(0)     

    # Signals that going to be catched and handled
    signal.signal(signal.SIGHUP, signal_handle)
    signal.signal(signal.SIGINT, signal_handle)
    signal.signal(signal.SIGQUIT, signal_handle)
    signal.signal(signal.SIGTERM, signal_handle)
    signal.signal(signal.SIGTSTP, signal_handle)

    # Recieving data from server and spliting it.
    recv_data =  client.recv(4096).decode()
    recv_splited = recv_data.split()

    global c_s_code 

    # Until first element of splited data recieved is CONNECTED wait there.
    while recv_splited[0] != "CONNECTED":
    
        recv_data =  client.recv(4096).decode()
        recv_splited = recv_data.split()

    # If first element of splited data recieved is CONNECTED client connected to server and recieved c_s_code from server
    if recv_splited[0] == "CONNECTED":
        c_s_code = recv_splited[1]

    # Main loop of client
    done = True
    while done:
        
        # Printing main menu and getting a valid input from player and sending it to server.
        print_startscreen()
        send_input(client)

        # Recieving data from server.
        recv_data =  client.recv(4096).decode()
        recv_splited = recv_data.split()

        # If first element of splited recieved data is EXIT player exites from the game.
        if recv_splited[0] == "EXIT":
            client.sendall(bytes("EXIT",'UTF-8'))
            done = False
            break    
        
        # If player waitng a match or have a match enters this part.
        if recv_splited[0] == "WAITMATCH" or recv_splited[0] == "WAITMATCHRAND" or recv_splited[0] == "MATCH":

            # While player do not have a match waits here for a match and tumbleweed animation printed.
            while recv_splited[0] != "MATCH":

                # while socket is bloking it waits for a data to recieve. For play tumbleweed animation while player
                # waits setting blocking to False.
                client.setblocking(False)
                try:
                    recv_data =  client.recv(4096).decode()
                    recv_splited = recv_data.split()   
                except:
                    for i in range(len(artfile.tumbleweed_list)):
                        time.sleep(1.3)
                        console_clear()
                        print(artfile.main_slingers)
                        print(artfile.tumbleweed_list[i])

                        # If first element of splited recieved data is WAITMATCH player wait a match
                        # for a private game themself opened. A room id to share is printed.
                        if recv_splited[0] == "WAITMATCH":
                            print("ROOM ID TO SHARE FOR DUEL" + " " + (recv_splited[1]))    

            # Setting blocking back to True 
            client.setblocking(True)
         
            # At this point player have a match and game can be start
            
            # Game starts and result of player is sent to server.
            result = duel()
            format_result = f"{result:.25f}"
            client.sendall(bytes("RESULT" + " " + c_s_code + " " + format_result,'utf-8'))
            
            # Recieving data from server.
            recv_data =  client.recv(4096).decode()
            recv_splited = recv_data.split()   

            # If first element of splited recieved data is WIN player wins.
            if recv_splited[0] == "WIN":
                console_clear()
                # Player wins screen printed
                print(artfile.slingers_8)
                print("press enter to continue main menu")
                time.sleep(1)
                con_wait()
                console_clear()

            # If first element of splited recieved data is LOSE player loses
            if recv_splited[0] == "LOSE":
                console_clear()
                # Player lose screen printed
                print(artfile.slingers_9)
                # If player result is 100000 this indicates player is a cheater.
                if result == 100000:
                    console_clear()
                    # Player lose screen printed and stays for 3 seconds.
                    print(artfile.slingers_9)
                    time.sleep(3)
                    console_clear()
                    tcflush(sys.stdin, TCIFLUSH)
                    # Player cheated screen printed.
                    print(artfile.cheat)
                    # Players client shutted down
                    client.sendall(bytes("EXIT",'UTF-8'))
                    done = False
                    break
                # If player is not a cheater player can return main menu.
                else:    
                    print("press enter to continue main menu")
                    con_wait()
                    console_clear()

        # If first element of splited recieved data is CANTJOIN enters here
        if recv_splited[0] == "CANTJOIN":
            # If second element of splited recieved data is FULL player is trying to enter a game with 2 players
            if recv_splited[1] == "FULL":
                console_clear()
                # Player notified about game is full
                print ("THE ROOM YOU WANT TO JOIN IS FULL")
            # If second element of splited recieved data is NOTEXIST player is trying to enter a game does not exist
            if recv_splited[1] == "NOTEXIST":
                console_clear()
                 # Player notified about game does not exist.
                print("THE ROOM YOU WANT TO JOIN DOES NOT EXIST")    
            continue

    client.close()

if __name__ == "__main__":
    main()
