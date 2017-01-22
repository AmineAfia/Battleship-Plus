from enum import IntEnum


class Constants:
    SERVER_PORT = 4711
    SERVER_IP = '127.0.0.1'


class Orientation(IntEnum):
    NORTH = 0
    EAST = 1


class EndGameReason(IntEnum):
    OPPONENT_ABORT = 0
    OPPONENT_TIMEOUT = 1
    YOU_WON = 2
    OPPONENT_WON = 3
    SERVER_CLOSED_CONNECTION = 4
    OTHER = 5


class Direction(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3