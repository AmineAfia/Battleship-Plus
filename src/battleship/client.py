import sys
import asyncio
import asyncio.streams
from common.constants import Constants
from common.protocol import ProtocolMessage, ProtocolMessageType, NumShips
from common.constants import Orientation, Direction, EndGameReason, ErrorCode, GameOptions


def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))

    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def client():
        reader, writer = yield from asyncio.streams.open_connection(
            Constants.SERVER_IP, Constants.SERVER_PORT, loop=loop)

        for i in [1, 2]:

            yield from asyncio.sleep(1, loop=loop)
            login_message = ProtocolMessage(ProtocolMessageType.LOGIN,
                                            {"username": "testuser{}".format(i)})
            yield from login_message.send(writer)

            yield from asyncio.sleep(1, loop=loop)
            create_game_message = ProtocolMessage(ProtocolMessageType.CREATE_GAME,
                                            {"board_size": 5,
                                             "num_ships": NumShips([1, 2, 3, 4, 5]),
                                             "round_time": 25,
                                             "options": GameOptions.PASSWORD,
                                             "password": "foobar"
                                                 })
            yield from create_game_message.send(writer)

            yield from asyncio.sleep(1, loop=loop)
            chat_send_message = ProtocolMessage(ProtocolMessageType.CHAT_SEND, {"username": "testuser", "text": "bummsfallerafalleri hurz"})
            yield from chat_send_message.send(writer)

            yield from asyncio.sleep(1, loop=loop)
            move_ship_message = ProtocolMessage(ProtocolMessageType.MOVE, {"turn_counter": 2, "ship_id": 146579, "direction": Orientation.EAST})
            yield from move_ship_message.send(writer)

            yield from asyncio.sleep(1, loop=loop)
            logout_message = ProtocolMessage(ProtocolMessageType.LOGOUT)
            yield from logout_message.send(writer)

        yield from asyncio.sleep(1, loop=loop)
        writer.close()

    # creates a client and connects to our server
    try:
        loop.run_until_complete(client())
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
