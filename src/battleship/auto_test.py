import sys
import asyncio
import asyncio.streams
from typing import Dict, List
from common.constants import Constants
from common.protocol import ProtocolMessage, ProtocolMessageType, NumShips
from common.constants import Orientation, Direction, EndGameReason, ErrorCode, GameOptions
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType, ShipPositions, Position, Positions, ShipPosition, NumShips

def get_cmd()
    return ["chat", "user1", "NOOB"]


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

        # Ding was die Verbindung managed zum Server
        battleship_client = BattleshipClient(loop, msg_callback, closed_callback)
        await battleship_client.connect(Constants.SERVER_IP, Constants.SERVER_PORT)

        # Noch son Ding was die Verbindung managed zum Server
        battleship_client_one = BattleshipClient(loop, msg_callback, closed_callback)
        await battleship_client_one.connect(Constants.SERVER_IP, Constants.SERVER_PORT)


        # the following messages are just to test
        # normally you can just call `await battleship_client.send(msg)`
        # await is necessary because it's asynchronous

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.LOGIN,
                                                    {"username": "testuser1".format(client_id)}))

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CHAT_SEND, {"username": "testuser2".format((client_id + 1) % 2), "text": "client {} schießt den server ab :P".format(client_id)}))

        #await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CHAT_SEND, {"username": "", "text": "z"}))


	####################################################################################################################
	# Start Playing #
	####################################################################################################################

	####################################################################################################################
	# Logout #
	####################################################################################################################
        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.LOGOUT))

        battleship_client.close()

    # creates a client and connects to our server
    try:
        num_clients: int = 1
        tasks = []
        for i in range(num_clients):
            tasks.append(asyncio.ensure_future(client(i)))
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()


if __name__ == '__main__':
    sys.exit(main())
