from .battlefield import *

class GameController:
    def __init__(self):
        self._gameName = "Battleship+"



    def move(battlefield, shipID, xPos, yPos):
        print("move {} at x=={},y={}".format(shipID, xPos, yPos))

    def shoot(xPos, yPos):
        print("shoot at x=={},y={}".format(xPos, yPos))