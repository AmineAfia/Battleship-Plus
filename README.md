## Battleship+
Implementation of team 4 using python and Terminal as a user interface.
## Getting Strated
#### Prerequisitions
To run the project youhn need to have:

- Python 3
- urwid
- mypy (optional for linting)

Clone the repo and cd to it.

#### Run
- open 3 Terminal windows/tabs then run in each:
	- Terminal 1: `make run-server`
	- Terminal 2: `make run-client`
	- Terminal 3: `make run-client`

#### Run in developer mode
IF you want to follow the clients log as well, instead of run-client
- Terminal 2: `make run-client1`
- Terminal 3: `make run-client2`

Open 2 new Terminal windows/tabs, cd to the battleship directory and run
- Terminal 4: `tail -f client1.log`
- Terminal 5: `tail -f client2.log`

#### Command arguments for custome ip and port

```
usage: server.py [-h] [-i IP] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        IP to listen on for client connections
  -p PORT, --port PORT  Port to listen on for client connections
```

```
usage: client.py [-h] [-i IP] [-p PORT] [-l LOGFILE]

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        server IP
  -p PORT, --port PORT  server port
  -l LOGFILE, --logfile LOGFILE
                        file for logs
```

# Tests/debuging

- We tested all functionalities of our client and server in the pre-interop test, 
the following [link](https://amineafia.github.io/Battleship-test-cases/) is a check list for the test cases we examed.

- To test the server's functionalities: use the scripts in `src/battleship/battletest1` and `src/battleship/battletest2`. 

- To test the server behavior with 100 client use the script in lotsofclients.py

- Random messages for the server in `random_messages.py`

- We used mypy as a type checker, to check the server and client run the following commands:
	```
	make mypy-server
	```
	```
	make mypy-client
	```

# Architecture
The game is structured as a Server-Client architechture, with one server that manages different clients playing with each other.

Both the server and the client have to follow the RFC rules for structured communication. 
To do that a GameController is an interface for the client and the server for RFC specifications checkings.

The client is based on the MVC architechture, where the GameController (the controller) is responsible for controlling the clients behavior, 
the ClientLobbyController class (the model) is responsible for handling the interactions with the server and different views in the frontend folder that use the model's/controller's data to render the user interface.
