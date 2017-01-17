from .Ship import Ship

class Battleship(Ship):

    def __init__(self, shipID, xPos, yPos):
        self._shipType = "Battleship"
        self._xlength = 5
        self._yLength = 1
        Ship.__init__(self, shipID, self._shipType, xPos, yPos, self._xLength, self._yLength)