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
    STARTGAME = 100
    PLACED = 101
    YOUSTART = 102
    WAIT = 103
    HIT = 104
    FAIL = 105
    MOVED = 106
    TIMEOUT = 107
    ENDGAME = 108
    PLACE = 150
    MOVE = 151
    SHOOT = 152
    LOGIN = 170
    LOGOUT = 171


class ProtocolField:

    def __init__(self, name: str, field_type, length_bytes: int=1):
        self.name = name
        self.length_bytes = length_bytes
        self.type = field_type


# TODO: is it pythonic to declare it as a global dictionary?
ProtocolMessageParameters: Dict[ProtocolMessageType, List[ProtocolField]] = {
    ProtocolMessageType.LOGIN: [ProtocolField("username", str, 2)],
    ProtocolMessageType.LOGOUT: []
}


class ProtocolMessage(object):

    def __init__(self, msg_type: ProtocolMessageType, parameters: dict=None):
        self.type = msg_type
        if parameters is None:
            self.parameters = {}
        else:
            self.parameters = parameters

    def __str__(self):
        return "{}: {}".format(self.type.name, self.parameters)

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
                parameter_bytes = parameter_value.to_bytes(1, byteorder=ProtocolConfig.BYTEORDER, signed=False)

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
            else:
                print("ERROR: unimplemented parameter type: {}".format(parameter.type))

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
