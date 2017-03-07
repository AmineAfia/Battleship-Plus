from .Ship import Ship
""" class Submarine
    The subclass Submarine inherits the class Ship.
    It contains the name, width and length of this type of ship.
"""


class Submarine(Ship):

    def __init__(self, ship_id, x_pos, y_pos, orientation):
        self._ship_type = "submarine"
        self._x_length = 2
        self._y_length = 1
        Ship.__init__(self, ship_id, self._ship_type, x_pos, y_pos, self._x_length, self._y_length, orientation)