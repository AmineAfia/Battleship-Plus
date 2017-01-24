from .battleship import Ship
from ..constants import Orientation, Direction

class Battlefield:

    #length = battlefield length <length> x <length>
    #ships = linked list of ships
    #_my_battlefield = my battlefield
    #_enemy_battlefield = enemy battlefield matrix, 0=hidden, 1=hit, 2=miss
    def __init__(self, length, ships):
        self._length = length
        self._ships = ships
        self._my_battlefield = [[0 for x in range(self._length - 1)] for y in range(self._length - 1)]
        self._enemy_battlefield = [[0 for x in range(self._length - 1)] for y in range(self._length - 1)]
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
    #check if already shot at this place
    def strike(self, x_pos, y_pos):
        iter_list = [x for x in range(self._length - 1)]
        for i in iter_list:
            for j in iter_list:
                if (self._my_battlefield[i][j] == 1):
                    print("already shot at this part of a ship")
                    return False
                elif (self._my_battlefield[i][j] == 2):
                    print("already missed at this place")
                    return False
                #shoot at hidden place
                elif (self._my_battlefield[i][j] == 0):
                    for ship in self._ships:
                        if (ship.strikeAtPosition(x_pos, y_pos)):
                            self._my_battlefield[i][j] = 1
                            return True
                    self._my_battlefield[i][j] = 2
        #no ship was hit
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

    #place the ship
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

    def noShipAtPlaceBut(self, x_pos, y_pos, ship_id):
        for ship in self._ships:
            if (ship.isShipAtLocation(x_pos, y_pos)):
                if not (ship.getShipId() == ship_id):
                    return False
        return True

    def placementFinished(self):

        for ship in self._ships:
            if not (ship.isPlaced()):
                return False
        return True

        #collision detection
        for ship in self._ships:
            shipCoordinates = ship.getShipCoordinates()
            print(shipCoordinates)
            for coordinates in shipCoordinates:
                if not (self.noShipAtPlaceBut(coordinates[0], coordinates[1], ship.getShipId())):
                    return False
        return True






