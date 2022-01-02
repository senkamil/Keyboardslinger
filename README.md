# Keyboardslinger

## Game Description
  Keyboardslinger is a western style gun duel game that can be played with two players that are connected to a server. Game works on Linux terminals. A player can create a new private game with a room id to share, join an already existing private room with room id or can join or create a random game for play with a random opponent. After two players match the game starts. Gunslingers walk apart and after the fifth step they turn back to each other and shoot warning displays. At this point the player should press enter and shoot. Player that shoots faster after the shoot warning is displayed wins. If a player presses enter before shoot warning this is a rule violation. Player loses, gets shot screen displayed, after 3 seconds the grim reaper screen is displayed and the player is kicked out from the game.

## Execution Gif
![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/Execution%20Gif/260201024_Ceng421_execution.gif)

## Implementation details 
  For implementation of the project Python 3.8.5 is used. Game coded and tested on Ubuntu 20.04.2 LTS. Game works on the terminal and clears the terminal for animations and screen changes. Since every operating system's terminal clear works differently, unexpected behavior can be and probably occur on other operating systems. This may apply to other Linux distributions or modified terminals but I think there shouldn’t be any problem.

 For the main logic of server and client part of the code I took help from http://net-informations.com/python/net/thread.htm and for daemonizing operation of server I utilized and slightly modified a part of https://gist.github.com/josephernest/77fdb0012b72ebdf4c9d19d6256a1119 . Project consists of three main files. Those files are client.py, server.py and artfile.py . Server and client parts source code explains nearly every detail step by step. Any implementation detail can be found in source code. Artfile contains ASCII arts used in game.

  As an implementation choice the game doesn’t work synchronously for opponents. This way, average player waiting time is less . Games run on client and performance of players evaluated on server and result of game sended to clients.

  As a note, since one of the players can leave or disconnect for any reason after 30 seconds if there is no performance info arrived to the server for a player, the other player wins.
  
## Instructions
Before continuing to steps of instructions, Port that defined on code can be in use on the system. Also for example if you start and kill and start again server for example port that defined will not be usable for a while. In this cases you should change PORT variable in both server and client code to an available port

1 - Server should be started first, for start server open terminal on folder that contains files and enter. Server is daemonized :

	python3 server.py

2 -  For start client open terminal on folder that contains files and enter :
 
	python3 client.py

3 - Since game need 2 players you need to open one more client like in step 2

4 -  At the main screen of the game for client there are 4 options. Options should be written with uppercase as displayed.

	a - NEWGAME
	b - JOIN
	c - RANDOMGAME
	d - EXIT

NEWGAME creates a new private game. After enter this command a room id to share is displayed like :

	ROOM ID TO SHARE FOR DUEL 7ZWNA

JOIN with a room id used for enter a private game like :

	JOIN 7ZWNA

RANDOMGAME is used for enter a public game if there is any available public game exists or create a new public game and wait for a match.

EXIT used for exit from the game.

5 - Only press enter once when you see SHOOT on screen

6 - For close server:

	pkill -9 -f server.py

## Execution Screenshots
Screenshots can also be found in the screenshots folder in case something is not readable. Also since I feel screenshots are not that descriptive for a game I included a gif of execution. To limit its size it is in x2 speed. Gif can be found in the Execution Gif folder.


### Main screen

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/1-Main_screen.png)



### NEWGAME wait and JOIN

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/2-NEWGAME_wait_and_JOIN.png)


### Game Start Screen

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/3-game_start_screen.png)



### Walk Apart Screen

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/4-walk_apart_screen.png)




### Normal game end screen

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/5-normal_game_end_screen.png)


### Win with other player left screen

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/6-win_with_other_left.png)



### Cheater final screen

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/7-cheater_final_screen.png)



### Server screenshot
(Logs on this screenshot contains some logs from test I made )

![alt text](https://github.com/senkamil/Keyboardslinger/blob/main/keyboardslinger/screenshots/8-Server_screenshot.jpeg)

# References

http://net-informations.com/python/net/thread.htm
    
https://gist.github.com/josephernest/77fdb0012b72ebdf4c9d19d6256a1119
    
https://patorjk.com/software/taag/#p=display&f=Graffiti&t=
    
https://svzanten.home.xs4all.nl/ascii/line_art/couples.html
    
https://asciiart.website/index.php?art=creatures/grim%20reapers


