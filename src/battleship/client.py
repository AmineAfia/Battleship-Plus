import sys
from common.GameController import GameController
from common.constants import Constants

def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))



if __name__ == '__main__':

    myController = GameController()
    myController.run()

    sys.exit(main())

