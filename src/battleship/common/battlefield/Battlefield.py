from .battleship import Ship

class Battlefield:

    #length = battlefield length <length> x <length>
    #ships = linked list of ships
    def __init__(self, length, ships):
        self._length = length
        self._ships = ships
        print("New Battlefield created with size {}x{} with ships:".format(length, length))
        for ship in ships:
            print (ship.getShipType())

    #move a ship one position
    def move(self, ship_id, direction):
        for ship in self._ships:
            if (ship._ship_id == ship_id):
                if (ship.move(direction)):
                    return True
                else:
                    return False

    def shoot(self, x_pos, y_pos):
        for ship in self._ships:
            if (ship.isAtPosition(x_pos, y_pos)):
                return True
        return False

    def hit(self, x_pos, y_pos):
        x = 0

