#from enum import Enum
from enum import IntEnum
from typing import Dict, List

import asyncio
import asyncio.streams


class ProtocolConfig:
    BYTEORDER = 'little'
    STR_ENCODING = 'utf-8'


class ProtocolMessageType(IntEnum):
    NONE = 0
    # Lobby, Server messages
    CHAT_RECV = 1
    GAMES = 2
    GAME = 3
    DELETE_GAME = 4
    # Lobby, Client messages
    LOGIN = 51
    LOGOUT = 52
    CHAT_SEND = 53
    CREATE_GAME = 54
    CANCEL = 55
    JOIN = 56
    GET_GAMES = 57
    # Game, Server messages
    STARTGAME = 101
    PLACED = 102
    YOUSTART = 103
    WAIT = 104
    HIT = 105
    FAIL = 106
    MOVED = 107
    TIMEOUT = 108
    ENDGAME = 109
    # Game, Client messages
    PLACE = 151
    MOVE = 152
    SHOOT = 153
    ABORT = 154
    # Error message
    ERROR = 255


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


class ProtocolField:

    def __init__(self, name: str, field_type, fixed_length: bool, length: int=0):
        self.name = name
        self.length_bytes = 1
        self.fixed_length = fixed_length
        self.length = length
        if self.fixed_length and self.length == 0:
            raise ValueError("If a ProtocolField instance has fixed length, i.e. fixed_length=True,"
                             "it must have a non-zero length.")
        self.type = field_type


class Position:
    def __init__(self, vertical: int, horizontal: int):
        self.vertical = vertical
        self.horizontal = horizontal

    @classmethod
    def from_bytes(cls, data: bytes):
        vertical = _int_from_bytes(data[0:1])
        horizontal = _int_from_bytes(data[1:2])
        return cls(vertical, horizontal)

    def to_bytes(self) -> bytes:
        b = b''
        b += _bytes_from_int(self.vertical)
        b += _bytes_from_int(self.horizontal)
        return b

    def __str__(self):
        return "({}, {})".format(self.vertical, self.horizontal)


class Positions:
    def __init__(self, positions: List[Position]):
        self.positions = positions

    @classmethod
    def from_bytes(cls, data: bytes):
        num_positions = len(data)/2
        positions = []
        for i in range(num_positions):
            positions.append(Position.from_bytes(data[i:i+2]))
        return cls(positions)

    def to_bytes(self) -> bytes:
        b = b''
        for position in self.positions:
            b += position.to_bytes()
        return b

    def __str__(self):
        s = "{"
        for position in self.positions:
            s += str(position)
        s += "}"
        return s


class ShipPosition:
    def __init__(self, position: Position, orientation: Orientation):
        self.position = position
        self.orientation = orientation

    @classmethod
    def from_bytes(cls, data: bytes):
        position = Position(data[0:2])
        orientation = Orientation(_int_from_bytes(data[2:3]))
        return cls(position, orientation)

    def to_bytes(self) -> bytes:
        b = b''
        b += self.position.to_bytes()
        b += _bytes_from_int(self.orientation)
        return b

    def __str__(self):
        return "({}, {}, {})".format(self.position.vertical, self.position.horizontal, self.orientation)


class ShipPositions:
    def __init__(self, positions: List[ShipPosition]):
        self.positions = positions

    @classmethod
    def from_bytes(cls, data: bytes):
        num_ship_positions = len(data)/3
        positions = []
        for i in range(num_ship_positions):
            positions.append(ShipPosition.from_bytes(data[3*i:3*i+3]))
        return cls(positions)

    def to_bytes(self) -> bytes:
        b = b''
        for position in self.positions:
            b += position.to_bytes()
        return b

    def __str__(self):
        s = "{"
        for position in self.positions:
            s += str(position)
        s += "}"
        return s


class NumShips:

    def __init__(self, numbers: List[int]):
        self.numbers = numbers

    @classmethod
    def from_ints(cls, carriers: int,
                  battleships: int,
                  cruisers: int,
                  destroyers: int,
                  submarines: int):
        return cls([
            carriers, battleships, cruisers, destroyers, submarines])

    @classmethod
    def from_bytes(cls, data: bytes):
        numbers: List[int] = []
        for i in range(5):
            numbers.append(_int_from_bytes(data[i:i+1]))
        return cls(numbers)

    def to_bytes(self) -> bytes:
        b = b''
        for number in self.numbers:
            b += _bytes_from_int(number)
        return b

    def __str__(self):
        return "{}".format(self.numbers)

    @property
    def carriers(self):
        return self.numbers[0]

    @property
    def battleships(self):
        return self.numbers[1]

    @property
    def cruisers(self):
        return self.numbers[2]

    @property
    def destroyers(self):
        return self.numbers[3]

    @property
    def submarines(self):
        return self.numbers[4]


# Parameters of Lobby messages
_field_username: ProtocolField = ProtocolField(name="username", field_type=str, fixed_length=False)
_field_text: ProtocolField = ProtocolField(name="text", field_type=str, fixed_length=False)
_field_board_size: ProtocolField = ProtocolField(name="board_size", field_type=int, fixed_length=True, length=1)
_field_num_ships: ProtocolField = ProtocolField(name="num_ships", field_type=NumShips, fixed_length=True, length=5)
_field_round_time: ProtocolField = ProtocolField(name="round_time", field_type=int, fixed_length=True, length=1)
_field_options: ProtocolField = ProtocolField(name="options", field_type=int, fixed_length=True, length=1)
_field_password: ProtocolField = ProtocolField(name="password", field_type=str, fixed_length=False)
_field_game_id: ProtocolField = ProtocolField(name="game_id", field_type=int, fixed_length=True, length=2)

# Not yet defined parameters of Game messages
_field_turn_counter: ProtocolField = ProtocolField(name="turn_counter", field_type=int, fixed_length=True, length=1)
_field_opponent_name: ProtocolField = _field_username
_field_sunk: ProtocolField = ProtocolField(name="sunk", field_type=int, fixed_length=True, length=1)
_field_position: ProtocolField = ProtocolField(name="position", field_type=Position, fixed_length=True, length=2)
_field_positions: ProtocolField = ProtocolField(name="positions", field_type=Positions, fixed_length=False)
_field_orientation: ProtocolField = ProtocolField(
    name="orientation", field_type=Orientation, fixed_length=True, length=1)
_field_reason: ProtocolField = ProtocolField(name="reason", field_type=EndGameReason, fixed_length=True, length=1)
_field_ship_id: ProtocolField = ProtocolField(name="ship_id", field_type=int, fixed_length=True, length=5)
_field_direction: ProtocolField = ProtocolField(name="direction", field_type=Orientation, fixed_length=True, length=1)


# TODO: is it pythonic to declare it as a global dictionary?
ProtocolMessageParameters: Dict[ProtocolMessageType, List[ProtocolField]] = {
    ProtocolMessageType.LOGIN: [_field_username],
    ProtocolMessageType.LOGOUT: [],
    ProtocolMessageType.CHAT_SEND: [_field_username, _field_text],
    ProtocolMessageType.CREATE_GAME:
        [_field_board_size, _field_num_ships, _field_round_time, _field_options, _field_password]
}


class ProtocolMessage(object):

    def __init__(self, msg_type: ProtocolMessageType, parameters: dict=None):
        self.type = msg_type
        if parameters is None:
            self.parameters = {}
        else:
            self.parameters = parameters

    def __str__(self):
        s = "{}: {{".format(self.type.name)
        for key, value in self.parameters.items():
            s += "{}: {}, ".format(key, value)
        s += "}"
        return s

    # TODO: this should be wrapped in an connection class, with some logic to prevent overlapping protocol messages,
    # TODO: sort of a scheduler, no rather a queue
    async def send(self, writer):
        # send type
        writer.write(self.type.to_bytes(1, byteorder=ProtocolConfig.BYTEORDER, signed=False))

        print("> msg_type={}, ".format(self.type.name), end="")

        # send each parameter with length and value in the defined order
        for protocol_field in ProtocolMessageParameters[self.type]:

            parameter_value = self.parameters[protocol_field.name]

            # TODO: can this be done the pythonic way without checking the type? See https://stackoverflow.com/a/154156
            if type(parameter_value) is str:
                parameter_bytes = parameter_value.encode(encoding=ProtocolConfig.STR_ENCODING)
            elif type(parameter_value) is int:
                parameter_bytes = _bytes_from_int(parameter_value)
            elif type(parameter_value) is NumShips:
                parameter_bytes = parameter_value.to_bytes()
            else:
                print("ERROR(send): unimplemented parameter type: {}".format(type(parameter_value)))

            # send length
            writer.write(len(parameter_bytes).to_bytes(
                protocol_field.length_bytes, byteorder=ProtocolConfig.BYTEORDER, signed=False))

            # send value
            writer.write(parameter_bytes)

            print("{}({}, {} byte)={}, ".format(
                protocol_field.name, type(parameter_value), protocol_field.length_bytes, parameter_value), end="")

        print(".", flush=True)


@asyncio.coroutine
def parse_from_stream(client_reader, client_writer, msg_callback):

    waiting_for_msg_type: bool = True
    read_bytes: int = 1
    msg: ProtocolMessage = None
    parameter_index: int = -1
    parameter: ProtocolField = None
    waiting_for_field_length: bool = False

    while True:
        #print("< Reading {} bytes".format(read_bytes))

        data = yield from client_reader.read(read_bytes)
        if not data:  # this means the client disconnected
            break

        # parse data
        if waiting_for_msg_type:
            msg_type = _msg_type_from_bytes(data)
            msg = ProtocolMessage(msg_type)

        elif waiting_for_field_length:
            read_bytes = _int_from_bytes(data)

        else:
            if parameter.type is str:
                msg.parameters[parameter.name] = _str_from_bytes(data)
            elif parameter.type is int:
                msg.parameters[parameter.name] = _int_from_bytes(data)
            elif parameter.type is NumShips:
                msg.parameters[parameter.name] = NumShips.from_bytes(data)
            else:
                print("ERROR(parse_from_stream): unimplemented parameter type: {}".format(parameter.type))

        # prepare the next loop
        if waiting_for_msg_type or not waiting_for_field_length:
            # the next thing to do is read the length field of the parameter
            parameter_index += 1
            try:
                parameter = ProtocolMessageParameters[msg_type][parameter_index]
                waiting_for_field_length = True
                read_bytes = parameter.length_bytes
                waiting_for_msg_type = False
            except IndexError:
                # there is no next parameter, so prepare for the next protocol message
                waiting_for_msg_type = True
                parameter_index = -1
                read_bytes = 1
                msg_callback(msg)

        elif waiting_for_field_length:
            # next is to read the actual data
            waiting_for_field_length = False

        # This enables us to have flow control in our connection.
        yield from client_writer.drain()


def _msg_type_from_bytes(data) -> ProtocolMessageType:
    return ProtocolMessageType(_int_from_bytes(data))


def _int_from_bytes(data: bytes) -> int:
    return int.from_bytes(data, byteorder=ProtocolConfig.BYTEORDER, signed=False)


def _str_from_bytes(data: bytes) -> str:
    return data.decode(encoding=ProtocolConfig.STR_ENCODING)


def _bytes_from_int(data: int) -> bytes:
    return data.to_bytes(1, byteorder=ProtocolConfig.BYTEORDER, signed=False)
