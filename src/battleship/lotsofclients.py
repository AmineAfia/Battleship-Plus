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

    finished = asyncio.Event()

    async def client(client_id: int):

        async def msg_callback(msg: ProtocolMessage):
            print("< [{}] {}".format(client_id, msg))

        def closed_callback():
            print("< [{}] server closed connection".format(client_id))

        async def _send_and_wait(msg: ProtocolMessage, seconds_to_wait: float = 0.0):
            print("> [{}] {}".format(client_id, msg))
            await battleship_client.send(msg)
            if seconds_to_wait > 0:
                await asyncio.sleep(seconds_to_wait)

        battleship_client = BattleshipClient(loop, msg_callback, closed_callback)
        await battleship_client.connect(Constants.SERVER_IP, Constants.SERVER_PORT)

        # the following messages are just to test
        # normally you can just call `await battleship_client.send(msg)`
        # await is necessary because it's asynchronous

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.LOGIN,
                                                    {"username": "user{}".format(client_id)}))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CREATE_GAME,
                                         {"board_size": 10,
                                          "num_ships": NumShips([1, 1, 1, 1, 1]),
                                          "round_time": 25,
                                          "options": GameOptions.PASSWORD,
                                          "password": "foobar"
                                              }))

        await finished.wait()

        battleship_client.close()

    # creates a client and connects to our server
    try:
        num_clients: int = 10
        tasks = []
        for i in range(num_clients):
            tasks.append(asyncio.ensure_future(client(i)))
        loop.run_until_complete(asyncio.gather(*tasks))

        input("press any key to exit")
        finished.set()
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
