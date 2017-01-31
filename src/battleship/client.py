import sys
from common.GameController import GameController
from common.constants import Orientation, Direction, Constants, GameOptions
from common.protocol import ProtocolMessage, ProtocolMessageType, ShipPositions, Position, ShipPosition, NumShips
from frontend.welcome import Welcome
from common.errorHandler.BattleshipError import BattleshipError

def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))
    game_id = 1
    my_controller = GameController(game_id)
    welcome = Welcome(my_controller)
    welcome.main_welcome()

	#def msg_callback(msg: ProtocolMessage):
        #if msg.type == ProtocolMessageType.CHAT_RECV:
            #print(msg.parameters["sender"])
            #print(msg.parameters["recipient"])
            #pass

    try:

        #CREATE THE BATTLEFIELD
        length = 10
        ships = [0, 0, 0, 1, 1]
        cmd = ["create", length, ships]
        msg = ProtocolMessage.create_single(ProtocolMessageType.CREATE_GAME,
                                            {"board_size": 10, "num_ships": NumShips(ships),
                                             "round_time": 25, "options": GameOptions.PASSWORD,
                                             "password": "foo"})
        my_controller.run(msg)

        #PLACE THE SHIPS
        ship_id = 1
        x_pos = 0
        y_pos = 0
        orientation = Orientation.EAST
        x_pos2 = 0
        y_pos2 = 2
        orientation2 = Orientation.EAST
        msg = ProtocolMessage.create_single(ProtocolMessageType.PLACE,
                                            {"ship_positions": ShipPositions([
                       ShipPosition(Position(y_pos, x_pos), orientation),
                       ShipPosition(Position(y_pos2, x_pos2), orientation2)])})

        my_controller.run(msg)


        my_controller.start_game()

        # MOVE YOUR SHIP
        ship_id = 2
        direction = Direction.EAST

        msg = ProtocolMessage.create_single(ProtocolMessageType.MOVE,
                                            { "ship_id": 1, "direction": Direction.EAST })
        my_controller.run(msg)

        #STRIKE FROM ENEMY = SHOOT
        x_pos = 0
        y_pos = 0

        msg = ProtocolMessage.create_single(ProtocolMessageType.SHOOT,
                                            { "ship_position": ShipPosition(Position(y_pos, x_pos), orientation  ) })
        my_controller.run(msg)

        #SHOOT AT ENEMY BATTLEFIELD
        x_pos = 0
        y_pos = 0
        my_controller.shoot(x_pos, y_pos)

        #ABORT
        msg = ProtocolMessage.create_single(ProtocolMessageType.ABORT)
        my_controller.run(msg)

    except BattleshipError as e:
        print("{}".format(e))


if __name__ == '__main__':
    sys.exit(main())
