import logging
from enum import Enum, IntEnum
from typing import Dict, List, Any, Optional
from .constants import Orientation, EndGameReason, Direction, ErrorCode, GameOptions
from random import randrange, choice

import asyncio
import asyncio.streams


class ProtocolConfig:
    BYTEORDER = 'big'
    STR_ENCODING = 'utf-8'
    PAYLOAD_LENGTH_BYTES = 2
    USERNAME_MAX_LENGTH = 22
    CHAT_MAX_TEXT_LENGTH = 63
    BOARD_SIZE_MIN = 10
    BOARD_SIZE_MAX = 26
    ROUND_TIMES = [_ for _ in range(25, 65, 5)]


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

    def __init__(self, name: str, field_type, fixed_length: bool, length: int=0, optional: bool=False, implicit_length: bool=False) -> None:
        self.name: str = name
        self.length_bytes: int = 1
        self.fixed_length: bool = fixed_length
        self.length: int = length
        if self.fixed_length and self.length == 0:
            raise ValueError("If a ProtocolField instance has fixed length, i.e. fixed_length=True,"
                             "it must have a non-zero length.")
        # TODO: how can I indicate the type here?
        self.type = field_type
        self.optional: bool = optional
        self.implicit_length: bool = implicit_length

    def random_value(self) -> Any:
        value: Any = None
        # fields of type str
        if self.name in ["username", "sender", "recipient", "opponent_name"]:
            value = "user{}".format(randrange(20))
        elif self.name == "text":
            value = "text{}".format(randrange(100))
        elif self.name == "password":
            value = "passwd{}".format(randrange(42))
        # fields of type int
        elif self.name == "board_size":
            value = randrange(ProtocolConfig.BOARD_SIZE_MIN, ProtocolConfig.BOARD_SIZE_MAX+1)
        elif self.name == "round_time":
            value = choice(ProtocolConfig.ROUND_TIMES)
        elif self.name == "game_id":
            value = randrange(0, 65535+1)
        elif self.name == "turn_counter":
            value = randrange(0, 255+1)
        elif self.name == "sunk":
            value = randrange(0, 1+1)
        elif self.name == "ship_id":
            value = randrange(0, 255+1)
        elif self.type in [NumShips, Position, Positions, ShipPosition, ShipPositions]:
            value = self.type.random()
        elif self.type in [GameOptions, EndGameReason, Orientation, Direction, ErrorCode]:
            value = choice(list(self.type))
        else:
            raise AttributeError("Random value for {} field '{}'' not implemented".format(self.type, self.name))
        return value


class Position:
    def __init__(self, vertical: int, horizontal: int) -> None:
        self.vertical = vertical
        self.horizontal = horizontal

    # TODO: hm, ok, this is the type of the class itself!?
    #def from_bytes(cls, data: bytes) -> Position:
    @classmethod
    def from_bytes(cls, data: bytes):
        vertical: int = _int_from_bytes(data[0:1])
        horizontal: int = _int_from_bytes(data[1:2])
        return cls(vertical, horizontal)

    @classmethod
    def random(cls):
        vertical = randrange(0, ProtocolConfig.BOARD_SIZE_MAX)
        horizontal = randrange(0, ProtocolConfig.BOARD_SIZE_MAX)
        return cls(vertical, horizontal)

    def __eq__(self, other):
        return (self.vertical == other.vertical and self.horizontal == other.horizontal)

    def to_bytes(self) -> bytes:
        b: bytes = b''
        b += _bytes_from_int(self.vertical)
        b += _bytes_from_int(self.horizontal)
        return b

    def __str__(self) -> str:
        return "({}, {})".format(self.vertical, self.horizontal)


class Positions:
    def __init__(self, positions: List[Position]=[]) -> None:
        self.positions: List[Position] = positions

    # TODO: hm, ok, this is the type of the class itself!?
    #def from_bytes(cls, data: bytes) -> Positions:
    @classmethod
    def from_bytes(cls, data: bytes):
        # TODO: raise Exception if len(data) is not a multiple of 2
        num_positions: int = int(len(data)/2)
        positions: List[Position] = []
        for i in range(num_positions):
            positions.append(Position.from_bytes(data[2*i:2*i+2]))
        return cls(positions)

    @classmethod
    def random(cls):
        num_positions: int = randrange(1, 10)
        positions: List[Position] = []
        for i in range(num_positions):
            positions.append(Position.random())
        return cls(positions)

    def __eq__(self, other):
        if not len(self.positions) == len(other.positions):
            return False
        for i, position in enumerate(self.positions):
            if not position == other.positions[i]:
                return False
        return True

    def __len__(self):
        return len(self.positions)

    def to_bytes(self) -> bytes:
        b: bytes = b''
        for position in self.positions:
            b += position.to_bytes()
        return b

    def __str__(self) -> str:
        s: str = "{"
        for position in self.positions:
            s += str(position)
        s += "}"
        return s


class ShipPosition:
    def __init__(self, position: Position, orientation: Orientation) -> None:
        self.position: Position = position
        self.orientation: Orientation = orientation

    @classmethod
    def from_bytes(cls, data: bytes):
    # TODO: def from_bytes(cls, data: bytes) -> ShipPosition:
        position: Position = Position.from_bytes(data[0:2])
        orientation: Orientation = Orientation(_int_from_bytes(data[2:3]))
        return cls(position, orientation)

    @classmethod
    def random(cls):
        position: Position = Position.random()
        orientation: Orientation = choice(list(Orientation))
        return cls(position, orientation)

    def __eq__(self, other):
        return (self.position == other.position and self.orientation == other.orientation)

    def to_bytes(self) -> bytes:
        b: bytes = b''
        b += self.position.to_bytes()
        b += _bytes_from_int(self.orientation)
        return b

    def __str__(self) -> str:
        return "({}, {}, {})".format(self.position.vertical, self.position.horizontal, self.orientation)


class ShipPositions:
    def __init__(self, positions: List[ShipPosition]) -> None:
        self.positions: List[ShipPosition] = positions

    @classmethod
    def from_bytes(cls, data: bytes):
    # TODO: def from_bytes(cls, data: bytes) -> ShipPositions:
        # TODO: raise Exception if len(data) is not a multiple of 3
        num_ship_positions: int = int(len(data)/3)
        positions: List[ShipPosition] = []
        for i in range(num_ship_positions):
            positions.append(ShipPosition.from_bytes(data[3*i:3*i+3]))
        return cls(positions)

    @classmethod
    def random(cls):
        num_ship_positions: int = randrange(1, 10)
        positions: List[ShipPosition] = []
        for i in range(num_ship_positions):
            positions.append(ShipPosition.random())
        return cls(positions)

    def __eq__(self, other):
        if not len(self.positions) == len(other.positions):
            return False
        else:
            for i, position in enumerate(self.positions):
                if not position == other.positions[i]:
                    return False
            return True

    def __len__(self):
        return len(self.positions)

    def to_bytes(self) -> bytes:
        b: bytes = b''
        for position in self.positions:
            b += position.to_bytes()
        return b

    def __str__(self) -> str:
        s: str = "{"
        for position in self.positions:
            s += str(position)
        s += "}"
        return s


class NumShips:

    def __init__(self, numbers: List[int]) -> None:
        self.numbers: List[int] = numbers

    @classmethod
    def from_ints(cls, carriers: int,
                  battleships: int,
                  cruisers: int,
                  destroyers: int,
                  submarines: int):
    # TODO:              submarines: int) -> NumShips:
        return cls([
            carriers, battleships, cruisers, destroyers, submarines])

    @classmethod
    def from_bytes(cls, data: bytes):
    # TODO: def from_bytes(cls, data: bytes) -> NumShips:
        numbers: List[int] = []
        for i in range(5):
            numbers.append(_int_from_bytes(data[i:i+1]))
        return cls(numbers)

    @classmethod
    def random(cls):
        return cls([randrange(0, 7) for _ in range(5)])

    def __eq__(self, other):
        return (self.numbers == other.numbers)

    def to_bytes(self) -> bytes:
        b: bytes = b''
        for number in self.numbers:
            b += _bytes_from_int(number)
        return b

    def __str__(self) -> str:
        return "{}".format(self.numbers)

    @property
    def carriers(self) -> int:
        return self.numbers[0]

    @property
    def battleships(self) -> int:
        return self.numbers[1]

    @property
    def cruisers(self) -> int:
        return self.numbers[2]

    @property
    def destroyers(self) -> int:
        return self.numbers[3]

    @property
    def submarines(self) -> int:
        return self.numbers[4]


# Parameters of Lobby messages
_field_username_with_length: ProtocolField = ProtocolField(name="username", field_type=str, fixed_length=False)
_field_sender_username_with_length: ProtocolField = ProtocolField(name="sender", field_type=str, fixed_length=False)
_field_recipient_username_with_length: ProtocolField = ProtocolField(name="recipient", field_type=str, fixed_length=False)
_field_username_implicit_length: ProtocolField = ProtocolField(name="username", field_type=str, fixed_length=False, implicit_length=True)
_field_text: ProtocolField = ProtocolField(name="text", field_type=str, fixed_length=False, implicit_length=True)
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
_field_positions: ProtocolField = ProtocolField(name="positions", field_type=Positions, fixed_length=False, implicit_length=True, optional=True)
_field_orientation: ProtocolField = ProtocolField(name="orientation", field_type=Orientation, fixed_length=True, length=1)
_field_reason: ProtocolField = ProtocolField(name="reason", field_type=EndGameReason, fixed_length=True, length=1)
_field_ship_position: ProtocolField = ProtocolField(name="ship_position", field_type=ShipPosition, fixed_length=True, length=3)
_field_ship_positions: ProtocolField = ProtocolField(name="ship_positions", field_type=ShipPositions, fixed_length=False, implicit_length=True)
_field_ship_id: ProtocolField = ProtocolField(name="ship_id", field_type=int, fixed_length=True, length=1)
_field_direction: ProtocolField = ProtocolField(name="direction", field_type=Direction, fixed_length=True, length=1)

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
    ProtocolMessageType.CANCEL: [],
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

ProtocolMessageParametersFieldNames: Dict[ProtocolMessageType, List[str]] = {msg_type: [field.name for field in fields] for msg_type, fields in ProtocolMessageParameters.items()}

ProtocolMessageRepeatingTypes: List[ProtocolMessageType] = [ProtocolMessageType.GAMES]


class ProtocolMessage:

    def __init__(self, msg_type: ProtocolMessageType=ProtocolMessageType.NONE, repeating_parameters: Optional[List[Dict[str, Any]]]=None) -> None:
        self.type: ProtocolMessageType = msg_type
        if repeating_parameters is None or repeating_parameters == []:
            self.repeating_parameters: List[Dict[str, Any]] = []
        else:
            self.repeating_parameters: List[Dict[str, Any]] = repeating_parameters
        self.missing_or_unkown_param: bool = False

    @classmethod
    def create_repeating(cls, msg_type: ProtocolMessageType, repeating_parameters: List[Dict[str, Any]]):
    # TODO: def create_repeating(cls, msg_type: ProtocolMessageType, repeating_parameters: List[Dict[str, Any]]) -> ProtocolMessage:
        if type(repeating_parameters) is not list:
            raise ValueError("Parameters must be a list")
        return cls(msg_type, repeating_parameters)

    @classmethod
    def empty_for_type(cls, msg_type: ProtocolMessageType):
        params: Dict[str, Any] = {}
        for field in ProtocolMessageParameters[msg_type]:
            params[field.name] = None
        return cls.create_single(msg_type, params)

    @classmethod
    def create_single(cls, msg_type: ProtocolMessageType, parameters: Optional[Dict[str, Any]] = None):
    # TODO: def create_single(cls, msg_type: ProtocolMessageType, parameters: Optional[Dict[str, Any]] = None) -> ProtocolMessage:
        if parameters is None:
            parameters = {}
        elif type(parameters) is not dict:
            raise ValueError("Parameters must be a dictionary")
        return cls(msg_type, [parameters])

    @classmethod
    def create_error(cls, error_code: ErrorCode):
    # TODO: def create_error(cls, error_code: ErrorCode) -> ProtocolMessage:
        return cls.create_single(ProtocolMessageType.ERROR, {"error_code": error_code})

    @classmethod
    def dummy(cls):
    # TODO: def dummy(cls) -> ProtocolMessage:
        return cls.create_single(ProtocolMessageType.CHAT_RECV,
                                 {"sender": "sender", "recipient": "recipient",
                                  "text": "fuck. you."})

    @classmethod
    def random(cls):
        # draw a random type
        msg_type: ProtocolMessageType = ProtocolMessageType.NONE
        while msg_type == ProtocolMessageType.NONE:
            msg_type = choice(list(ProtocolMessageType))
        return cls.random_from_type(cls, msg_type)

    @classmethod
    def random_from_type(cls, msg_type: ProtocolMessageType):
        fields = ProtocolMessageParameters[msg_type]

        if msg_type in ProtocolMessageRepeatingTypes:
            repeating_params = []
            num_repeating = randrange(1, 5)
            for _ in range(num_repeating):
                params: Dict[str, Any] = {}
                for field in fields:
                    params[field.name] = field.random_value()
                repeating_params.append(params)
            return cls.create_repeating(msg_type, repeating_params)

        else:
            params: Dict[str, Any] = {}
            for field in fields:
                params[field.name] = field.random_value()
            return cls.create_single(msg_type, params)

    def __eq__(self, other):
        if not self.type == other.type:
            return False
        elif not len(self.repeating_parameters) == len(other.repeating_parameters):
            return False
        else:
            for i, parameters in enumerate(self.repeating_parameters):
                other_parameters = other.repeating_parameters[i]
                if not len(parameters) == len(other_parameters):
                    return False
                for param in parameters:
                    if not param in other_parameters:
                        return False
                    elif not parameters[param] == other_parameters[param]:
                        return False
            return True

    def __str__(self) -> str:
        s: str = "{}:".format(self.type.name)
        for parameters in self.repeating_parameters:
            s += _protocol_parameters_to_str(parameters)
            s += ", "
        return s

    @property
    def parameters(self) -> Dict[str, Any]:
        return self.repeating_parameters[0]

    def append_parameters(self, parameters: dict) -> None:
        self.check_parameters(parameters)
        if len(self.repeating_parameters) == 1 and self.repeating_parameters[0] == {}:
            self.repeating_parameters[0] = parameters
        else:
            self.repeating_parameters.append(parameters)

    def check_parameters(self, parameters: dict):
        for field in ProtocolMessageParameters[self.type]:
            if not field.optional and not field.name in parameters:
                self.missing_or_unkown_param = True
                return
        for param in parameters:
            if not param in ProtocolMessageParametersFieldNames[self.type]:
                self.missing_or_unkown_param = True
                return

    async def send_repeating(self, writer) -> None:
        try:
            await self.send(writer)
        except ProtocolRepeatingMessageError as e:
            # construct new msg with the remaining. And there _are_ remaining, otherwise the error would not have been raised
            new_msg: ProtocolMessage = ProtocolMessage.create_repeating(self.type, self.repeating_parameters[e.last_index+1:])
            await new_msg.send_repeating(writer)

    async def send(self, writer) -> None:

        msg_bytes_type: bytes = self.type.to_bytes(1, byteorder=ProtocolConfig.BYTEORDER, signed=False)
        # initialize with 0
        msg_bytes_length: bytes = _bytes_from_int(0, length=ProtocolConfig.PAYLOAD_LENGTH_BYTES)
        msg_bytes_payload: bytes = b''
        msg_bytes_payload_length: int = 0

        overflow: bool = False

        # append type

        # logging.debug("> msg_type={}, ".format(self.type.name), end="")

        num_fields: int = len(ProtocolMessageParameters[self.type])

        for parameters_index, parameters in enumerate(self.repeating_parameters):
            params_bytes_payload: bytes = b''

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
                        raise AttributeError("Send ProtocolMessage: missing parameter {} for type {}".format(protocol_field.name, self.type))

                # TODO: can this be done the pythonic way without checking the type? See https://stackoverflow.com/a/154156
                if protocol_field.type is str:
                    parameter_bytes = parameter_value.encode(encoding=ProtocolConfig.STR_ENCODING)
                elif protocol_field.type in [int, Orientation, EndGameReason, Direction, ErrorCode, GameOptions]:
                    parameter_bytes = _bytes_from_int(int(parameter_value), length=protocol_field.length)
                elif protocol_field.type in [NumShips, Position, Positions, ShipPosition, ShipPositions]:
                    parameter_bytes = parameter_value.to_bytes()
                else:
                    logging.error("ERROR(send): unimplemented parameter type: {}".format(type(parameter_value)))

                # length field?
                # if not last_field and not protocol_field.fixed_length:
                if not protocol_field.fixed_length and not protocol_field.implicit_length:
                    # We have a length field for this field. And it has length 1 by definition
                    parameter_bytes_length = len(parameter_bytes)
                    params_bytes_payload += _bytes_from_int(parameter_bytes_length)

                # data
                params_bytes_payload += parameter_bytes

            # after each parameter list, test if the payload would still fit
            tmp_msg_bytes_payload_length: int = msg_bytes_payload_length + len(params_bytes_payload)
            try:
                # this raises OverflowError if the payload is too long
                tmp_msg_bytes_length = _bytes_from_int(tmp_msg_bytes_payload_length, length=ProtocolConfig.PAYLOAD_LENGTH_BYTES)
                # no OverflowError, thus we can append the stuff
                msg_bytes_payload += params_bytes_payload
                msg_bytes_payload_length = tmp_msg_bytes_payload_length
                msg_bytes_length = tmp_msg_bytes_length
            except OverflowError:
                # in this case, don't add the payload bytes, quit the loop, and at the end of the function, raise an exception
                overflow = True
                last_index = parameters_index-1
                break

        # check if we had an overflow directly during the first parameters, thus nothing can be sent
        if overflow and last_index < 0:
            raise OverflowError()

        # logging.debug("> {}".format(self))
        writer.write(msg_bytes_type)
        # logging.debug("send: type({})".format(msg_bytes_type))

        writer.write(msg_bytes_length)
        # logging.debug("send: length({})".format(msg_bytes_length))

        if msg_bytes_payload_length > 0:
            writer.write(msg_bytes_payload)
            # logging.debug("send: payload({})".format(msg_bytes_payload))

        await writer.drain()

        # inform the caller, that not all of the repeating parameters have been sent
        if overflow:
            raise ProtocolRepeatingMessageError(last_index)


async def parse_from_stream(client_reader, client_writer, msg_callback):

    waiting_for_msg_type: bool = True
    bytes_to_read_next: int = 1
    msg: ProtocolMessage
    msg_payload_bytes: int = 0
    msg_remaining_payload_bytes: int = 0
    parameter_index: int = -1
    parameter_count: int = 0
    parameter: ProtocolField
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

        try:
            data = await client_reader.read(bytes_to_read_next)
            if not data:
                # this means the client disconnected(?)
                break
        except ConnectionResetError as e:
            # TODO: check if the client_disconnected callback is called anyways
            break

        # logging.debug("recv: " + str(data))

        # parse data
        if waiting_for_msg_type:
            msg_type = _msg_type_from_bytes(data)
            # TODO: handle NONE
            msg = ProtocolMessage(msg_type)
            # logging.debug("start parsing type {}".format(msg_type))
            parameter_count = len(ProtocolMessageParameters[msg_type])

        elif waiting_for_payload_length:
            msg_payload_bytes = _int_from_bytes(data)
            msg_remaining_payload_bytes = msg_payload_bytes

        elif waiting_for_field_length:
            msg_remaining_payload_bytes -= bytes_to_read_next
            bytes_to_read_next = _int_from_bytes(data)

            # we have an empty parameter
            if bytes_to_read_next == 0:
                if parameter.type is str:
                    parameters[parameter.name] = ""
                else:
                    logging.error("ERROR(parse_from_stream): empty parameter for type: {}".format(parameter.type))

        else:
            msg_remaining_payload_bytes -= bytes_to_read_next

            if parameter.type is str:
                # try:
                parameters[parameter.name] = _str_from_bytes(data)
                # except UnicodeDecodeError as e:
                #     logging.error("UnicodeDecodeError while decoding parameter {} in type {}, parameters until now: {}".format(parameter.name, msg_type, parameters))
            elif parameter.type in [int, Orientation, EndGameReason, Direction, ErrorCode, GameOptions]:
                parameters[parameter.name] = _int_from_bytes(data)
            elif parameter.type in [NumShips, Position, Positions, ShipPosition, ShipPositions]:
                parameters[parameter.name] = parameter.type.from_bytes(data)
            else:
                logging.error("ERROR(parse_from_stream): unimplemented parameter type: {}".format(parameter.type))

        # prepare the next loop
        if waiting_for_msg_type:
            # Now we always have a payload length field
            # # Check if this message type has payload.
            # # If so, there will be a global length field

            # if len(ProtocolMessageParameters[msg_type]) > 0:
            waiting_for_payload_length = True
            waiting_for_msg_type = False
            bytes_to_read_next = ProtocolConfig.PAYLOAD_LENGTH_BYTES
            # # If not, the message is already complete
            # else:
            #    await finalize_msg_and_prepare_for_next()

        elif waiting_for_payload_length or not waiting_for_field_length or (waiting_for_field_length and bytes_to_read_next == 0):
            waiting_for_payload_length = False

            if msg_payload_bytes == 0:
                # for example empty GAMES message
                await finalize_msg_and_prepare_for_next()
            else:

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
    msg_type: ProtocolMessageType
    try:
        msg_type = ProtocolMessageType(_int_from_bytes(data))
    except ValueError:
        msg_type = ProtocolMessageType.NONE
    return msg_type

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

class ProtocolRepeatingMessageError(Exception):
    def __init__(self, last_index):
        self.last_index = last_index

    def __str__(self):
        return "Last sent index was {}".format(self.last_index)
