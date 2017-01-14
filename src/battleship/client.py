import sys
import asyncio
import asyncio.streams
from common.constants import Constants
from common.protocol import ProtocolMessage, ProtocolMessageType


def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))

    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def client():
        reader, writer = yield from asyncio.streams.open_connection(
            Constants.SERVER_IP, Constants.SERVER_PORT, loop=loop)

        login_message = ProtocolMessage(ProtocolMessageType.LOGIN, {"username": "testuser"})
        yield from login_message.send(writer)

        writer.close()

    # creates a client and connects to our server
    try:
        loop.run_until_complete(client())
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
