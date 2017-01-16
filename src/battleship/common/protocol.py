#from enum import Enum
from enum import IntEnum
from typing import Dict, List


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
