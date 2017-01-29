import sys
import asyncio
import asyncio.streams
from typing import Dict, List
from common.constants import Constants
from common.protocol import ProtocolMessage, ProtocolMessageType, NumShips
from common.constants import Orientation, Direction, EndGameReason, ErrorCode, GameOptions
from common.network import BattleshipClient


def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))

    loop = asyncio.get_event_loop()

    async def client(client_id: int):

        async def msg_callback(msg: ProtocolMessage):
            print("< [{}] {}".format(client_id, msg))

        def closed_callback():
            print("< [{}] server closed connection".format(client_id))

        async def _send_and_wait(msg: ProtocolMessage, seconds_to_wait: float = 0.5):
            print("> [{}] {}".format(client_id, msg))
            await battleship_client.send(msg)
            if seconds_to_wait > 0:
                await asyncio.sleep(seconds_to_wait)

        battleship_client = BattleshipClient(Constants.SERVER_IP, Constants.SERVER_PORT, loop, msg_callback, closed_callback)
        await battleship_client.connect()

        # the following messages are just to test
        # normally you can just call `await battleship_client.send(msg)`
        # await is necessary because it's asynchronous

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.LOGIN,
                                                    {"username": "testuser{}".format(i)}))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CREATE_GAME,
                                        {"board_size": 5,
                                         "num_ships": NumShips([1, 2, 3, 4, 5]),
                                         "round_time": 25,
                                         "options": GameOptions.PASSWORD,
                                         "password": "foobar"
                                             }))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CREATE_GAME,
                                        {"board_size": 5,
                                         "num_ships": NumShips([1, 2, 3, 4, 5]),
                                         "round_time": 25,
                                         "options": 0
                                             }))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CHAT_SEND, {"username": "testuser", "text": "bummsfallerafalleri hurz"}))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.MOVE, {"turn_counter": 2, "ship_id": 146579, "direction": Orientation.EAST}))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.GAME, {
            "game_id": 60000, "username": "you", "board_size": 7, "num_ships": NumShips([1, 2, 3, 4, 5]), "round_time": 25, "options": GameOptions.PASSWORD}))

        await _send_and_wait(ProtocolMessage.create_repeating(ProtocolMessageType.GAMES, [
            {"game_id": 60000, "username": "you", "board_size": 7, "num_ships": NumShips([1, 2, 3, 4, 5]),
                "round_time": 25, "options": GameOptions.PASSWORD},
            {"game_id": 60001, "username": "she", "board_size": 8, "num_ships": NumShips([1, 2, 3, 4, 6]),
                "round_time": 30, "options": 0},
            {"game_id": 60002, "username": "they", "board_size": 9, "num_ships": NumShips([1, 2, 3, 4, 7]),
             "round_time": 35, "options": GameOptions.PASSWORD}]))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.JOIN, {"game_id": 60000, "password": "bumms"}))
        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.JOIN, {"game_id": 60001}))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.LOGOUT))

        battleship_client.close()

    # creates a client and connects to our server
    try:
        num_clients: int = 2
        tasks = []
        for i in range(num_clients):
            tasks.append(asyncio.ensure_future(client(i)))
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
