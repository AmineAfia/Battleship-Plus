from .Ship import Ship

class Submarine(Ship):

    def __init__(self, ship_id, x_pos, y_pos):
        self._ship_type = "Submarine"
        self._x_length = 2
        self._y_length = 1
        Ship.__init__(self, ship_id, self._ship_type, x_pos, y_pos, self._x_length, self._y_length)