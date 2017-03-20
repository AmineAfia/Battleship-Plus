# Battleship+
|<img src="https://media.giphy.com/media/3o6Mv4JnwwAXOievm0/source.gif" alt="Overview" width="900"/>|
|:-------------------------------------------------------------------------------------------------:|

The GIF shows two clients (two upper tabs) playing with each other and the server (lower tab) output. 
More screen shots are located in the [screen_shots folder](./screen_shots).

## Getting Started
### Prerequisites
To run the project you need to have:

- Python 3.6
- urwid
- pyfiglet
- mypy (optional for linting)

Clone the repo and cd to it.

### Run
- open 3 Terminal windows/tabs then run in each:
	- Terminal 1: `make run-server`
	- Terminal 2: `make run-client`
	- Terminal 3: `make run-client`

### Run in developer mode
If you want to follow the clients log as well, instead of `run-client`
- Terminal 2: `make run-client1`
- Terminal 3: `make run-client2`

Open 2 new Terminal windows/tabs, cd to the battleship directory and run
- Terminal 4: `tail -f client1.log`
- Terminal 5: `tail -f client2.log`

### Command arguments for custome ip and port

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

### IPv6

This Battleship+ implementation supports IPv6. The used Python
libraries made this completely transparent for us developers and
thus for the users.

Simply provide an IPv6 address via the command line options, or in the case of the client, enter it into the login screen:

```
python src/battleship/server.py --ip ::1
```

```
python src/battleship/client.py --ip ::1
```

## Tests/debuging

- We tested all functionalities of our client and server in the pre-interop test, 
the following [link](https://amineafia.github.io/Battleship-test-cases/) is a check list for the test cases we examined.

- To test the server's functionalities: use the scripts in `src/battleship/battletest1` and `src/battleship/battletest2`. 

- To test the server's behavior with 100 clients use the script in `lotsofclients.py` and start the server with the `make run-server-large` which sets a high limit of 4096 allowed open files to allow a lot of incoming client connections.

- To test the sending and parsing of messages on the level of the protocol layer, use `random_messages.py`

- We used mypy as a type checker. To check the server and client run the following commands:
	```
	make mypy-server
	```
	```
	make mypy-client
	```

## Architecture
The game is structured as a client-server architechture, with one server managing different clients playing with each other.

Both the server and the client have to follow the RFC rules for structured communication.
To do that a GameController offers an interface for the client and the server for checking the RFC specifications (Bettleship rules).

The client is based on the MVC architechture, where the GameController (controller and model for a game) is responsible for controlling the clients behavior, 
the ClientLobbyController class (controller and model for the client) is responsible for handling the interactions with the server. The frontend is a collection of 
different views in the frontend folder that use the model's/controller's data to render the user interface.

Both client and server are single-threaded applications. The asynchronous handling of network and UI events is done by Python's asyncio.
In the case of the client, the urwid UI framework and the network share one event loop.

Entrypoints to read the code are

- `src/battleship/client.py`: the client
- `src/battleship/server.py`: the server
- `src/battleship/common/GameController.py`: the game controller
- `src/battleship/common/protocol.py`: the protocol message creation and parsing code