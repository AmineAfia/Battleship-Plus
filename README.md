# Battleship+

# Getting Strated
## Prerequisitions
To run the project youhn need to have:

- Python 3
- urwid
## Run
- Clone the repo
- open 3 Terminal windows/tabs and cd to g4/src/battleship then run:
	- Terminal 1: `make run-server`
	- Terminal 2: `make run-client`
	- Terminal 3: `make run-client`

## Run in developer mode
IF you want to follow the clients log as well, open 2 new Terminal windows/tabs, cd to the battleship directory and run

```
tail -f client1.log
```
```
tail -f client2.log
```
and instead of run-client

```
make run-client1
```
```
make run-client2
```

# Tests/debuging

```
make mypy-server
```
```
make mypy-client
```

# Architecture
