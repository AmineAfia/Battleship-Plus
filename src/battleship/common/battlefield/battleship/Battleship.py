from .Ship import Ship
""" class Battleship
    The subclass Battleship inherits the class Ship.
    It contains the name, width and length of this type of ship.
"""


class Battleship(Ship):

    def __init__(self, ship_id, x_pos, y_pos, orientation):
        self._ship_type = "battleship"
        self._x_length = 5
        self._y_length = 1
        Ship.__init__(self, ship_id, self._ship_type, x_pos, y_pos, self._x_length, self._y_length, orientation)