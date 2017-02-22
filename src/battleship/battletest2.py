import sys
import asyncio
import asyncio.streams
from typing import Dict, List
from common.constants import Constants
from common.protocol import ProtocolMessage, ProtocolMessageType, NumShips
from common.constants import Orientation, Direction, EndGameReason, ErrorCode, GameOptions
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType, ShipPositions, Position, Positions, ShipPosition, NumShips


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
        #await battleship_client.connect("192.168.0.1", "4242")
        # the following messages are just to test
        # normally you can just call `await battleship_client.send(msg)`
        # await is necessary because it's asynchronous

        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.LOGIN,
                                                    {"username": "testuser2".format(client_id)}))

        input("PUSH THE BUTTON for chatting")
        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.CHAT_SEND, {"username": "testuser1".format((client_id + 1) % 2), "text": "Hi Loser, Grüße von client {}".format(client_id)}))
        game_id = input("PUSH THE BUTTON game_id: ")
        await _send_and_wait(ProtocolMessage.create_single(ProtocolMessageType.JOIN, {"game_id": game_id}))

        input("PUSH THE BUTTON to place a game")
        msg = ProtocolMessage.create_single(ProtocolMessageType.PLACE,
                                            {"ship_positions": ShipPositions([
                                                ShipPosition(Position(0, 0), Orientation.EAST)])})

        await _send_and_wait(msg)
	####################################################################################################################
	# Start Playing #
	####################################################################################################################
        end = input("x=exit, m=move, s=shoot:_")
        while end is not "x":
            if end == "s":
                turn_counter = int(input("insert turn_counter to shoot: "))
                x_pos = int(input("shot x_pos: "))
                y_pos = int(input("shoot y_pos: "))
                msg = ProtocolMessage.create_single(ProtocolMessageType.SHOOT,
                     			{"position": Position(y_pos, x_pos),
                	     		"turn_counter": turn_counter})

            if end == "m":    
                turn_counter = int(input("insert turn_counter to move: "))
                move_direction = int(input("insert move direction: "))
                msg = ProtocolMessage.create_single(ProtocolMessageType.MOVE,
                                                    {"ship_id": 0, "direction": move_direction,
                                                     "turn_counter": turn_counter})


            await _send_and_wait(msg)
            end = input("x=exit, m=move, s=shoot:_")

	#ABORT
        input("PUSH THE BOTTEN for abort")
        msg = ProtocolMessage.create_single(ProtocolMessageType.ABORT)
        await _send_and_wait(msg)
	####################################################################################################################
	# Logout #
	####################################################################################################################
        input("PUSH THE BUTTON to logout")
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
