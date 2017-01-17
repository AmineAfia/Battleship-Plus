from .battlefield import Battlefield
from .battlefield.battleship import Battleship


class GameController:

    def createGame(self, length, ships):
        self._gameName = "Battleship+"
        self._battlefield = Battlefield(length, ships)



    def move(self, battlefield, shipID, xPos, yPos):
        battlefield.move(self._battlefield, shipID, xPos, yPos)
        #print("move {} at x=={},y={}".format(shipID, xPos, yPos))

    def shoot(xPos, yPos):
        print("shoot at x={},y={}".format(xPos, yPos))


    #here we go
    if __name__ == "__main__":

        print("creating battlefield with ships...")

        #size = 5x5
        length = 5
        #added a Battleship at x=1, y=1, with shipID=1
        ships = Battleship(1,1,1)
        createGame(length, ships)




