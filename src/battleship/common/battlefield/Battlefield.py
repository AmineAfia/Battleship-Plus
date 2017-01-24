from .battleship import Ship
from ..constants import Orientation, Direction

class Battlefield:

    #length = battlefield length <length> x <length>
    #ships = linked list of ships
    #_my_battlefield = my battlefield
    #_enemy_battlefield = enemy battlefield matrix, 0=hidden, 1=hit, 2=miss
    def __init__(self, length, ships):
        self._ships = ships
        self._my_battlefield = [[length], [length]]
        self._enemy_battlefield = [[length], [length]]
        print("New Battlefield created with size {}x{} with ships:".format(length, length))
        for ship in ships:
            print (ship.getShipType())

    #move a ship one position further
    def move(self, ship_id, direction):
        for ship in self._ships:
            if (ship._ship_id == ship_id):
                if (ship.move(direction)):
                    return True
                else:
                    return False

    #enemy strike
    def strike(self, x_pos, y_pos):
        for ship in self._ships:
            if (ship.strikeAtPosition(x_pos, y_pos)):
                return True
        return False

    #shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if ((x_pos * y_pos) >= len(self._enemy_battlefield)):
            #shoot at hidden field
            if (self._enemy_battlefield[x_pos][y_pos] == 0):
                return True
            #shoot at already damaged ship
            elif (self._enemy_battlefield[x_pos][y_pos] == 1):
                return True
            #shoot at missed field again
            elif (self._enemy_battlefield[x_pos][y_pos] == 2):
                return True
            else:
                return False
        return False

    def place(self, ship_id, x_pos, y_pos, orientation):
        for ship in self._ships:
            if (ship.getShipId() == ship_id):
                if (self.noShipAtPlace(x_pos, y_pos)):
                    ship.place(x_pos, y_pos, orientation)
                else:
                    print("error a ship is already at this place")


    def noShipAtPlace(self, x_pos, y_pos):
        for ship in self._ships:
            if (ship.isShipAtLocation(x_pos, y_pos)):
                return False
        return True





