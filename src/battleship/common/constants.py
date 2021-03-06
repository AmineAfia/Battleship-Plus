from enum import IntEnum, IntFlag


class Constants:
    SERVER_PORT = 4242
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


class ErrorCode(IntEnum):
    UNKNOWN = 0
    # Illegal State Errors
    ILLEGAL_STATE_ALREADY_LOGGED_IN = 1
    ILLEGAL_STATE_NOT_LOGGED_IN = 2
    ILLEGAL_STATE_NOT_IN_GAME = 3
    ILLEGAL_STATE_NOT_YOUR_TURN = 4
    ILLEGAL_STATE_GAME_ALREADY_STARTED = 8
    ILLEGAL_STATE_NUMBER_OF_GAMES_LIMIT_EXCEEDED = 9
    # Syntax Errors
    SYNTAX_MISSING_OR_UNKNOWN_PARAMETER = 10
    SYNTAX_MESSAGE_TEXT_TOO_LONG = 11
    SYNTAX_USERNAME_TOO_LONG = 12
    SYNTAX_INVALID_BOARD_SIZE = 13
    SYNTAX_INVALID_ROUND_TIME = 14
    SYNTAX_INVALID_PARAMETER = 15
    SYNTAX_PASSWORD_TOO_LONG = 16
    # Parameter Errors
    PARAMETER_OPTION_NOT_SUPPORTED = 100
    PARAMETER_USERNAME_ALREADY_EXISTS = 101
    PARAMETER_USERNAME_DOES_NOT_EXIST = 102
    PARAMETER_WRONG_RECIPIENT = 103
    PARAMETER_UNKNOWN_GAME_ID = 104
    PARAMETER_PASSWORD_REQUIRED = 105
    PARAMETER_INVALID_PASSWORD = 106
    PARAMETER_ILLEGAL_JOIN = 107
    PARAMETER_TOO_MANY_SHIPS = 108
    PARAMETER_POSITION_OUT_OF_BOUNDS = 110
    PARAMETER_OVERLAPPING_SHIPS = 111
    PARAMETER_WRONG_NUMBER_OF_SHIPS = 112
    PARAMETER_INVALID_SHIP_ID = 113
    PARAMETER_SHIP_IMMOVABLE = 114
    PARAMETER_INVALID_TURN_COUNT = 115
    PARAMETER_INVALID_USERNAME = 116
    PARAMETER_ALREADY_HIT_POSITION = 117
    # UI calls errors
    INTERN_NO_MORE_SHIP_TO_PLACE = 200
    INTERN_NO_MORE_SHIP_TO_PLACE_OF_TYPE = 201
    INTERN_NO_SHIP_AT_LOCATION = 202
    INTERN_SHIP_ID_DOES_NOT_EXIST = 203


class GameOptions(IntFlag):
    PASSWORD = 128
