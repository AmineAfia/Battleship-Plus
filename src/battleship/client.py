import sys
from common.GameController import GameController
from common.constants import Constants

def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))



if __name__ == '__main__':


    length = 10
    ships = [0,0,0,0,2]

    myController = GameController()

    cmd = ""
    while (cmd != "exit"):
        cmd = input("Was du wolle?")
        print (cmd)



    myController.run(length, ships)
    myController.place(1, 0, 0, 1)
    myController.place(2, 0, 1, 1)

    myController.play()

    sys.exit(main())

