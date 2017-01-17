from .Ship import Ship

class AircraftCarrier(Ship):

    def __init__(self, shipID, xPos, yPos):
        self._shipType = "AircraftCarrier"
        self._xlength = 5
        self._yLength = 2
        Ship.__init__(self, shipID, self._shipType, xPos, yPos, self._xLength, self._yLength)