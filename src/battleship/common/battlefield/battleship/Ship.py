class Ship:

    #shipType = ship type
    #xPos = fixed point at x position
    #yPos = fixed point at y position
    #xLength = x length of ship
    #yLength = y length of ship
    def __init__(self, shipID, shipType, xPos, yPos, xLength, yLength):
        self._shipID = shipID
        self._shipType = shipType
        self._xPos = xPos
        self._yPos = yPos
        print("Created Ship: {} with shipID: {}".format(self._shipType, self._shipID))
        print("Fixed at x={},y={}".format(xPos, yPos))
        print("Size = {}x{}".format(xPos, yPos))

    def move(self, xPos, yPos):
        print("move {} at x={},y={}".format(self._shipID, xPos, yPos))

    def hit(self, xPos, yPos):
        hit = False


        if (hit):
            print("im hurt")
        else:
            print("easy peasy")





