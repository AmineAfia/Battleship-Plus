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

        @asyncio.coroutine
        def _send_and_wait(msg: ProtocolMessage, seconds_to_wait: float=0.5):
            yield from msg.send(writer)
            if seconds_to_wait > 0:
                yield from asyncio.sleep(seconds_to_wait, loop=loop)

        for i in [1, 2]:

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.LOGIN,
                                                        {"username": "testuser{}".format(i)}))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.CREATE_GAME,
                                            {"board_size": 5,
                                             "num_ships": NumShips([1, 2, 3, 4, 5]),
                                             "round_time": 25,
                                             "options": GameOptions.PASSWORD,
                                             "password": "foobar"
                                                 }))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.CREATE_GAME,
                                            {"board_size": 5,
                                             "num_ships": NumShips([1, 2, 3, 4, 5]),
                                             "round_time": 25,
                                             "options": 0
                                                 }))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.CHAT_SEND, {"username": "testuser", "text": "bummsfallerafalleri hurz"}))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.MOVE, {"turn_counter": 2, "ship_id": 146579, "direction": Orientation.EAST}))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.GAME, {
                "game_id": 60000, "username": "you", "board_size": 7, "num_ships": NumShips([1, 2, 3, 4, 5]), "round_time": 25, "options": GameOptions.PASSWORD}))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.JOIN, {"game_id": 60000, "password": "bumms"}))
            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.JOIN, {"game_id": 60001}))

            yield from _send_and_wait(ProtocolMessage(ProtocolMessageType.LOGOUT))

        writer.close()

    # creates a client and connects to our server
    try:
        loop.run_until_complete(client())
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
