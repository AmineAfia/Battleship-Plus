from .battleship import Ship

class Battlefield:

    #length = battlefield length <length> x <length>
    #ships = linked list of ships
    def __init__(self, length, ships):
        self._length = length
        self._ships = ships
        print("New Battlefield created with size {}x{}".format(length, length))


    def move(self, shipID, xPos, yPos):
        print("move {} at x={},y={}".format(shipID, xPos, yPos))

    def shoot(self, xPos, yPos):
        hit = False
        print("shoot at x={},y={}".format(xPos, yPos))


        if(hit):
            print("boooooom!!!!!")
        else:
            print("fail!")
        return hit

    def hit(self, xPos, yPos):
        x = 0

