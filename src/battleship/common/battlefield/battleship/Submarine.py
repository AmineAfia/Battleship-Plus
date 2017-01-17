from .Ship import Ship

class Submarine(Ship):

    def __init__(self, shipID, xPos, yPos):
        self._shipType = "Submarine"
        self._xlength = 2
        self._yLength = 1
        Ship.__init__(self, shipID, self._shipType, xPos, yPos, self._xLength, self._yLength)
