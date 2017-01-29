from .battleship import Ship
from ..constants import Orientation, Direction, ErrorCode
from ..errorHandler.BattleshipError import BattleshipError

class Battlefield:

    # length = battlefield length <length> x <length>
    # ships = linked list of ships
    # _my_battlefield = my battlefield
    # _enemy_battlefield = enemy battlefield matrix, 0=hidden, 1=hit, 2=miss
    def __init__(self, length, ships):
        self._length = length
        self._ships = ships
        self._my_battlefield = [[0 for x in range(self._length - 1)] for y in range(self._length - 1)]
        self._enemy_battlefield = [[0 for x in range(self._length - 1)] for y in range(self._length - 1)]

    # move a ship one position further
    def move(self, ship_id, direction):
        for ship in self._ships:
            if ship._ship_id == ship_id:

                ship_coordinates = ship.get_ship_coordinates()
                x_pos = ship_coordinates[0][0]
                y_pos = ship_coordinates[0][1]

                if direction == Direction.EAST:
                    x_pos = x_pos + 1
                if direction == Direction.SOUTH:
                    y_pos = y_pos + 1
                if direction == Direction.WEST:
                    x_pos = x_pos - 1
                if direction == Direction.NORTH:
                    y_pos = y_pos - 1

                if self.no_border_crossing(x_pos, y_pos):
                    if not ship.is_hit():
                        if self.no_ship_at_place_but(x_pos, y_pos, ship.get_ship_id()):
                            #if self.no_strike_at_place(x_pos, y_pos):
                            if ship.move(direction):
                                print("Ship: {} moved to: {}".format(ship._ship_id, ship._ship_state))
                                return True
                            else:
                                return False
                            #else:
                                #raise BattleshipError(ErrorCode.PARAMETER_OPTION_NOT_SUPPORTED)
                        else:
                            raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
                    else:
                        raise BattleshipError(ErrorCode.PARAMETER_SHIP_IMMOVABLE)
        return False

    # enemy strike
    # check if already shot at this place
    def strike(self, x_pos, y_pos):
        if self.no_border_crossing(x_pos, y_pos):
            if self._my_battlefield[x_pos][y_pos] == 1:
                print("already shot at this part of a ship")
                return False
            elif self._my_battlefield[x_pos][y_pos] == 2:
                print("already missed at this place")
                return False
            #shoot at hidden place
            elif self._my_battlefield[x_pos][y_pos] == 0:
                self._my_battlefield[x_pos][y_pos] = 2
                for ship in self._ships:
                    if ship.is_ship_at_location(x_pos, y_pos):
                        ship.strike(x_pos, y_pos)
                        self._my_battlefield[x_pos][y_pos] = 1
                        return True
        # no ship was hit
        return False

    # shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if (x_pos * y_pos) >= len(self._enemy_battlefield):
            #shoot at hidden field
            if self._enemy_battlefield[x_pos][y_pos] == 0:
                return True
            #shoot at already damaged ship
            elif self._enemy_battlefield[x_pos][y_pos] == 1:
                return True
            #shoot at missed field again
            elif self._enemy_battlefield[x_pos][y_pos] == 2:
                return True
            else:
                return False
        return False

    # place the ship
    def place(self, ship_id, x_pos, y_pos, orientation):
        for ship in self._ships:
            if ship.get_ship_id() == ship_id:
                if self.no_ship_at_place(x_pos, y_pos):
                    if ship.place(x_pos, y_pos, orientation):
                        print("Ship: {} placed: {}".format(ship._ship_id, ship._ship_state))
                else:
                    print("error a ship is already at this place")


    def no_ship_at_place(self, x_pos, y_pos):
        for ship in self._ships:
            if ship.is_ship_at_location(x_pos, y_pos):
                return False
        return True

    def no_ship_at_place_but(self, x_pos, y_pos, ship_id):
        for ship in self._ships:
            if (ship.is_ship_at_location(x_pos, y_pos)):
                if not ship.get_ship_id() == ship_id:
                    return False
        return True

    def no_strike_at_place(self, x_pos, y_pos):
        if self._my_battlefield[x_pos][y_pos] == 0:
            return True
        else:
            return False

    def no_border_crossing(self, x_pos, y_pos):
        if x_pos < self._length and y_pos < self._length and x_pos >= 0 and y_pos >= 0:
            return True
        else:
            return False

    def placement_finished(self):
        for ship in self._ships:
            if not ship.is_placed():
                return False
        return True

    def ship_is_moveable(self, ship_id):
        for ship in self._ships:
            if ship._ship_id == ship_id:
                return not ship.is_hit()
        return False

    def ship_id_exists(self, ship_id):
        for ship in self._ships:
            if ship._ship_id == ship_id:
                return True
        return False

    








