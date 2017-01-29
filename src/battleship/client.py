import sys
from common.GameController import GameController
from common.constants import Orientation, Direction, Constants
from common.protocol import ProtocolMessage, ProtocolMessageType


def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))


if __name__ == '__main__':

    #def msg_callback(msg: ProtocolMessage):
        #if msg.type == ProtocolMessageType.CHAT_RECV:
            #print(msg.parameters["sender"])
            #print(msg.parameters["recipient"])
            #pass

    game_id = 1
    my_controller = GameController(game_id)

    #cmd = ""
    #while (cmd != "exit"):
        #cmd = input("Was du wolle?")
        #print (cmd)

    #CREATE THE BATTLEFIELD
    length = 10
    ships = [0, 0, 0, 0, 1]
    cmd = ["create", length, ships]
    my_controller.run(cmd)

    #PLACE THE SHIPS
    ship_id = 1
    x_pos = 0
    y_pos = 0
    orientation = Orientation.EAST
    cmd = ["place", ship_id, x_pos, y_pos, orientation]
    my_controller.run(cmd)

    # MOVE YOUR SHIP
    ship_id = 1
    direction = Direction.EAST
    cmd = ["move", ship_id, direction]
    my_controller.run(cmd)

    #STRIKE FROM ENEMY
    x_pos = 0
    y_pos = 0
    cmd = ["strike", x_pos, y_pos]
    my_controller.run(cmd)
    
    #SHOOT AT ENEMY BATTLEFIELD
    x_pos = 0
    y_pos = 0
    cmd = ["shoot", x_pos, y_pos]
    my_controller.run(cmd)

    #ABORT
    cmd = ["abort"]
    my_controller.run(cmd)




    sys.exit(main())

