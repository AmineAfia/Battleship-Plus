from enum import Enum, IntEnum
from typing import Dict, List
from .constants import Orientation, EndGameReason, Direction, ErrorCode, GameOptions


import asyncio
import asyncio.streams


class ProtocolConfig:
    BYTEORDER = 'little'
    STR_ENCODING = 'utf-8'
    PAYLOAD_LENGTH_BYTES = 2
    CHAT_MAX_TEXT_LENGTH = 63


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


class ProtocolField:

    def __init__(self, name: str, field_type, fixed_length: bool, length: int=0, optional: bool=False, implicit_length: bool=False):
        self.name = name
        self.length_bytes = 1
        self.fixed_length = fixed_length
        self.length = length
        if self.fixed_length and self.length == 0:
            raise ValueError("If a ProtocolField instance has fixed length, i.e. fixed_length=True,"
                             "it must have a non-zero length.")
        self.type = field_type
        self.optional = optional
        self.implicit_length = implicit_length


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
_field_username_with_length: ProtocolField = ProtocolField(name="username", field_type=str, fixed_length=False)
_field_sender_username_with_length: ProtocolField = ProtocolField(name="sender", field_type=str, fixed_length=False)
_field_recipient_username_with_length: ProtocolField = ProtocolField(name="recipient", field_type=str, fixed_length=False)
_field_username_implicit_length: ProtocolField = ProtocolField(name="username", field_type=str, fixed_length=False, implicit_length=True)
_field_text: ProtocolField = ProtocolField(name="text", field_type=str, fixed_length=False)
_field_board_size: ProtocolField = ProtocolField(name="board_size", field_type=int, fixed_length=True, length=1)
_field_num_ships: ProtocolField = ProtocolField(name="num_ships", field_type=NumShips, fixed_length=True, length=5)
_field_round_time: ProtocolField = ProtocolField(name="round_time", field_type=int, fixed_length=True, length=1)
_field_options: ProtocolField = ProtocolField(name="options", field_type=GameOptions, fixed_length=True, length=1)
_field_password: ProtocolField = ProtocolField(name="password", field_type=str, fixed_length=False, optional=True, implicit_length=True)
_field_game_id: ProtocolField = ProtocolField(name="game_id", field_type=int, fixed_length=True, length=2)

# Not yet defined parameters of Game messages
_field_turn_counter: ProtocolField = ProtocolField(name="turn_counter", field_type=int, fixed_length=True, length=1)
_field_opponent_name: ProtocolField = ProtocolField(name="opponent_name", field_type=str, fixed_length=False, implicit_length=True)
_field_sunk: ProtocolField = ProtocolField(name="sunk", field_type=int, fixed_length=True, length=1)
_field_position: ProtocolField = ProtocolField(name="position", field_type=Position, fixed_length=True, length=2)
_field_positions: ProtocolField = ProtocolField(name="positions", field_type=Positions, fixed_length=False, implicit_length=True)
_field_orientation: ProtocolField = ProtocolField(
    name="orientation", field_type=Orientation, fixed_length=True, length=1)
_field_reason: ProtocolField = ProtocolField(name="reason", field_type=EndGameReason, fixed_length=True, length=1)
_field_ship_position: ProtocolField = ProtocolField(
    name="ship_position", field_type=ShipPosition, fixed_length=True, length=3)
_field_ship_positions: ProtocolField = ProtocolField(
    name="ship_positions", field_type=ShipPositions, fixed_length=False, implicit_length=True)
_field_ship_id: ProtocolField = ProtocolField(name="ship_id", field_type=int, fixed_length=True, length=5)
_field_direction: ProtocolField = ProtocolField(name="direction", field_type=Orientation, fixed_length=True, length=1)

# Errors
_field_error_code: ProtocolField = ProtocolField(name="error_code", field_type=ErrorCode, fixed_length=True, length=1)


# TODO: is it pythonic to declare it as a global dictionary?
ProtocolMessageParameters: Dict[ProtocolMessageType, List[ProtocolField]] = {
    ProtocolMessageType.NONE: [],
    # Lobby, Server messages
    ProtocolMessageType.CHAT_RECV: [_field_sender_username_with_length, _field_recipient_username_with_length, _field_text],
    ProtocolMessageType.GAMES: [_field_game_id, _field_username_with_length, _field_board_size,
                                _field_num_ships, _field_round_time, _field_options],
    ProtocolMessageType.GAME: [_field_game_id, _field_username_implicit_length, _field_board_size,
                               _field_num_ships, _field_round_time, _field_options],
    ProtocolMessageType.DELETE_GAME: [_field_game_id],
    # Lobby, Client messages
    ProtocolMessageType.LOGIN: [_field_username_implicit_length],
    ProtocolMessageType.LOGOUT: [],
    ProtocolMessageType.CHAT_SEND: [_field_username_with_length, _field_text],
    ProtocolMessageType.CREATE_GAME: [_field_board_size, _field_num_ships, _field_round_time,
                                      _field_options, _field_password],
    ProtocolMessageType.CANCEL: [_field_game_id],
    ProtocolMessageType.JOIN: [_field_game_id, _field_password],
    ProtocolMessageType.GET_GAMES: [],
    # Game, Server messages
    ProtocolMessageType.STARTGAME: [_field_board_size, _field_num_ships, _field_round_time, _field_opponent_name],
    ProtocolMessageType.PLACED: [],
    ProtocolMessageType.YOUSTART: [],
    ProtocolMessageType.WAIT: [],
    ProtocolMessageType.HIT: [_field_sunk, _field_position],
    ProtocolMessageType.FAIL: [_field_position],
    ProtocolMessageType.MOVED: [_field_positions],
    ProtocolMessageType.TIMEOUT: [],
    ProtocolMessageType.ENDGAME: [_field_reason],
    # Game, Client messages
    ProtocolMessageType.PLACE: [_field_ship_positions],
    ProtocolMessageType.MOVE: [_field_turn_counter, _field_ship_id, _field_direction],
    ProtocolMessageType.SHOOT: [_field_turn_counter, _field_position],
    ProtocolMessageType.ABORT: [],
    # Error message
    ProtocolMessageType.ERROR: [_field_error_code]
}

ProtocolMessageRepeatingTypes: List[ProtocolMessageType] = [ProtocolMessageType.GAMES]


class ProtocolMessage(object):

    def __init__(self, msg_type: ProtocolMessageType, repeating_parameters: list=None):
        self.type = msg_type
        if repeating_parameters is None or repeating_parameters == []:
            self.repeating_parameters = []
        else:
            self.repeating_parameters = repeating_parameters

    @classmethod
    def create_repeating(cls, msg_type: ProtocolMessageType, repeating_parameters: list):
        if type(repeating_parameters) is not list:
            raise ValueError("Parameters must be a list")
        return cls(msg_type, repeating_parameters)

    @classmethod
    def create_single(cls, msg_type: ProtocolMessageType, parameters: dict=None):
        if parameters is None:
            parameters = {}
        elif type(parameters) is not dict:
            raise ValueError("Parameters must be a dictionary")
        return cls(msg_type, [parameters])

    @classmethod
    def create_error(cls, error_code: ErrorCode):
        return cls.create_single(ProtocolMessageType.ERROR, {"error_code": error_code})

    @classmethod
    def dummy(cls):
        return cls.create_single(ProtocolMessageType.CHAT_RECV,
                                 {"sender": "sender", "recipient": "recipient",
                                  "text": "fuck. you."})

    def __str__(self):
        s = "{}:".format(self.type.name)
        for parameters in self.repeating_parameters:
            s += _protocol_parameters_to_str(parameters)
            s += ", "
        return s

    @property
    def parameters(self):
        return self.repeating_parameters[0]

    def append_parameters(self, parameters: dict):
        if len(self.repeating_parameters) == 1 and self.repeating_parameters[0] == {}:
            self.repeating_parameters[0] = parameters
        else:
            self.repeating_parameters.append(parameters)

    async def send(self, writer):

        msg_bytes_type = b''
        msg_bytes_length = b''
        msg_bytes_payload = b''

        # append type
        msg_bytes_type += self.type.to_bytes(1, byteorder=ProtocolConfig.BYTEORDER, signed=False)

        # print("> msg_type={}, ".format(self.type.name), end="")

        num_fields = len(ProtocolMessageParameters[self.type])

        for parameters in self.repeating_parameters:
            # send each parameter with length and value in the defined order
            for num_field, protocol_field in enumerate(ProtocolMessageParameters[self.type]):
                #last_field = (num_field == num_fields-1)

                try:
                    parameter_value = parameters[protocol_field.name]
                except KeyError:
                    if protocol_field.optional:
                        # Now handle the different cases in the protocol.
                        if self.type == ProtocolMessageType.CREATE_GAME and (parameters["options"] & GameOptions.PASSWORD):
                            raise AttributeError("Send ProtocolMessage: missing password, but options say there shoud be one.")
                        # In case of JOIN_GAME, we simply don't know at this layer, if a password is needed.
                        # So just don't send one.
                        else:
                            continue
                    else:
                        raise AttributeError("Send ProtocolMessage: missing parameter {}".format(parameter_value))

                # TODO: can this be done the pythonic way without checking the type? See https://stackoverflow.com/a/154156
                if type(parameter_value) is str:
                    parameter_bytes = parameter_value.encode(encoding=ProtocolConfig.STR_ENCODING)
                elif type(parameter_value) in [int, Orientation, EndGameReason, Direction, ErrorCode, GameOptions]:
                    parameter_bytes = _bytes_from_int(parameter_value, length=protocol_field.length)
                elif type(parameter_value) is NumShips:
                    parameter_bytes = parameter_value.to_bytes()
                else:
                    print("ERROR(send): unimplemented parameter type: {}".format(type(parameter_value)))

                # length field?
                # if not last_field and not protocol_field.fixed_length:
                if not protocol_field.fixed_length and not protocol_field.implicit_length:
                    # We have a length field for this field. And it has length 1 by definition
                    parameter_bytes_length = len(parameter_bytes)
                    msg_bytes_payload += _bytes_from_int(parameter_bytes_length)

                # data
                msg_bytes_payload += parameter_bytes

                # print("{}({}, {} byte)={}, ".format(
                #     protocol_field.name, type(parameter_value), protocol_field.length_bytes, parameter_value), end="")

        msg_bytes_payload_length = len(msg_bytes_payload)

        # this raises OverflowError if the payload is too long
        msg_bytes_length = _bytes_from_int(msg_bytes_payload_length, length=ProtocolConfig.PAYLOAD_LENGTH_BYTES)

        #print("> {}".format(self))
        writer.write(msg_bytes_type)
        #print("type({})".format(msg_bytes_type))
        if num_fields > 0:
            writer.write(msg_bytes_length)
            #print("length({})".format(msg_bytes_length))
            writer.write(msg_bytes_payload)
            #print("payload({})".format(msg_bytes_payload))

        await writer.drain()

        # print(".", flush=True)


async def parse_from_stream(client_reader, client_writer, msg_callback):

    waiting_for_msg_type: bool = True
    bytes_to_read_next: int = 1
    msg: ProtocolMessage = None
    msg_payload_bytes: int = 0
    msg_remaining_payload_bytes: int = 0
    parameter_index: int = -1
    parameter_count: int = 0
    parameter: ProtocolField = None
    parameters: dict = {}
    waiting_for_field_length: bool = False
    waiting_for_payload_length: bool = False

    async def finalize_msg_and_prepare_for_next():
        nonlocal waiting_for_msg_type, parameter_index, bytes_to_read_next, parameters
        waiting_for_msg_type = True
        parameter_index = -1
        msg.append_parameters(parameters)
        parameters = {}
        bytes_to_read_next = 1
        await msg_callback(msg)

    def get_implicit_length():
        # calculate it with parameter_index and remaining bytes
        accumulated_length_of_remaining_params: int = 0
        for other_param in ProtocolMessageParameters[msg_type][parameter_index+1:]:
            try:
                accumulated_length_of_remaining_params += other_param.length
            except:
                # TODO: if length is not defined for the parameter, this is not a valid protocol message type
                pass
        return msg_remaining_payload_bytes - accumulated_length_of_remaining_params

    while True:

        data = await client_reader.read(bytes_to_read_next)
        if not data:  # this means the client disconnected
            break

        # parse data
        if waiting_for_msg_type:
            msg_type = _msg_type_from_bytes(data)
            msg = ProtocolMessage(msg_type)
            parameter_count = len(ProtocolMessageParameters[msg_type])

        elif waiting_for_payload_length:
            msg_payload_bytes = _int_from_bytes(data)
            msg_remaining_payload_bytes = msg_payload_bytes

        elif waiting_for_field_length:
            msg_remaining_payload_bytes -= bytes_to_read_next
            bytes_to_read_next = _int_from_bytes(data)

        else:
            msg_remaining_payload_bytes -= bytes_to_read_next

            if parameter.type is str:
                parameters[parameter.name] = _str_from_bytes(data)
            elif parameter.type is int:
                parameters[parameter.name] = _int_from_bytes(data)
            # TODO: this is a lot of repetition, can this be generalized?
            elif parameter.type is Orientation:
                parameters[parameter.name] = Orientation(_int_from_bytes(data))
            elif parameter.type is Direction:
                parameters[parameter.name] = Direction(_int_from_bytes(data))
            elif parameter.type is EndGameReason:
                parameters[parameter.name] = EndGameReason(_int_from_bytes(data))
            elif parameter.type is ErrorCode:
                parameters[parameter.name] = ErrorCode(_int_from_bytes(data))
            elif parameter.type is GameOptions:
                parameters[parameter.name] = GameOptions(_int_from_bytes(data))
            elif parameter.type is NumShips:
                parameters[parameter.name] = NumShips.from_bytes(data)
            else:
                print("ERROR(parse_from_stream): unimplemented parameter type: {}".format(parameter.type))

        # prepare the next loop
        if waiting_for_msg_type:
            # Check if this message type has payload.
            # If so, there will be a global length field
            if len(ProtocolMessageParameters[msg_type]) > 0:
                waiting_for_payload_length = True
                waiting_for_msg_type = False
                bytes_to_read_next = ProtocolConfig.PAYLOAD_LENGTH_BYTES
            # If not, the message is already complete
            else:
                await finalize_msg_and_prepare_for_next()

        elif waiting_for_payload_length or not waiting_for_field_length:
            waiting_for_payload_length = False

            # the next thing to do is read the length field of a parameter,
            # or the content of a parameter
            parameter_index += 1

            # check if we have a repeating message type and
            # if we are currently at the end, and there is more to come
            if msg_type in ProtocolMessageRepeatingTypes:
                if parameter_index == parameter_count:
                    if msg_remaining_payload_bytes > 0:
                        parameter_index = 0
                        msg.append_parameters(parameters)
                        parameters = {}

            # Is there is a next parameter?
            if parameter_index < parameter_count:

                waiting_for_msg_type = False

                parameter = ProtocolMessageParameters[msg_type][parameter_index]

                # If it's fixed length, we read the payload as a next step.
                if parameter.fixed_length:
                    waiting_for_field_length = False
                    bytes_to_read_next = parameter.length

                # If it's variable length, we might have a length field to read.
                # We have a length field if it's _not_ the last parameter
                # elif parameter_index < parameter_count-1:
                elif not parameter.implicit_length:
                    waiting_for_field_length = True
                    bytes_to_read_next = parameter.length_bytes

                # If it's variable length _and_ the last field, all the remaining
                # bytes belong to this field
                else:
                    waiting_for_field_length = False
                    bytes_to_read_next = get_implicit_length()
                    # If there are no more bytes, apparently the message is finished.
                    # This can be the case when no password is set.
                    if bytes_to_read_next == 0:
                        await finalize_msg_and_prepare_for_next()

            # there is no next parameter, so prepare for the next protocol message
            else:
                await finalize_msg_and_prepare_for_next()

        elif waiting_for_field_length:
            # next is to read the actual data
            waiting_for_field_length = False

        # This enables us to have flow control in our connection.
        await client_writer.drain()


def _msg_type_from_bytes(data) -> ProtocolMessageType:
    return ProtocolMessageType(_int_from_bytes(data))


def _int_from_bytes(data: bytes) -> int:
    return int.from_bytes(data, byteorder=ProtocolConfig.BYTEORDER, signed=False)


def _str_from_bytes(data: bytes) -> str:
    return data.decode(encoding=ProtocolConfig.STR_ENCODING)


def _bytes_from_int(data: int, length: int=1) -> bytes:
    return data.to_bytes(length, byteorder=ProtocolConfig.BYTEORDER, signed=False)


def _protocol_parameters_to_str(parameters: dict) -> str:
    s = "{"
    for key, value in parameters.items():
        if isinstance(value, Enum):
            s += "{}: {}, ".format(key, value.name)
        else:
            s += "{}: {}, ".format(key, value)
    s += "}"
    return s
