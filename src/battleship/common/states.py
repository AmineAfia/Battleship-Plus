from enum import Enum, auto


class ClientConnectionState(Enum):
    NOT_CONNECTED = auto()
    CONNECTED = auto()
    GAME_CREATED = auto()
    GAME_SELECTION = auto()
    PLAYING = auto()


class GameState(Enum):
    PLACE_SHIPS = auto()
    WAITING = auto()
    YOUR_TURN = auto()
    OPPONENTS_TURN = auto()
    GAME_ENDED = auto()
    GAME_ABORTED = auto()

