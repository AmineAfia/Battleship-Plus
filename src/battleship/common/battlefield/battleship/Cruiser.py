from .Ship import Ship

class Cruiser(Ship):

    def __init__(self, shipID, xPos, yPos):
        self._shipType = "Cruiser"
        self._xlength = 4
        self._yLength = 1
        Ship.__init__(self, shipID, self._shipType, xPos, yPos, self._xLength, self._yLength)