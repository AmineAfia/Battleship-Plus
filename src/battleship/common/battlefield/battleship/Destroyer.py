from .Ship import Ship

class Destroyer(Ship):

    def __init__(self, shipID, xPos, yPos):
        self._shipType = "Destroyer"
        self._xlength = 3
        self._yLength = 1
        Ship.__init__(self, shipID, self._shipType, xPos, yPos, self._xLength, self._yLength)