import sys
from common.GameController import GameController
from common.constants import Constants

def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))



if __name__ == '__main__':


    length = 10
    ships = [0,0,0,0,2]

    myController = GameController()
    myController.run(length, ships)

    sys.exit(main())

