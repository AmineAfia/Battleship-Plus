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
        self._xLength = xLength
        self._yLength = yLength
        self._hitCounter = 0
        self._hitMap = [[0 for x in range(xLength)] for y in range(yLength)]
        print("Created Ship: {} with shipID: {}".format(self._shipType, self._shipID))
        print("Fixed at x={},y={}".format(xPos, yPos))
        print("Size = {}x{}".format(xPos, yPos))

    #can not move it hit
    def move(self, xPos, yPos):
        print("move {} at x={},y={}".format(self._shipID, xPos, yPos))

    #return if enemy get a score
    def hit(self, xPos, yPos):
        hit = False

        if (hit):
            self._hitCounter = self._hitCounter + 1
            print("im hurt")
        else:
            print("easy peasy")
        return hit

    def alive(self):
        alive = True
        if(self._hitCounter == self._xLength * self._yLength):
            alive = False
        return alive






