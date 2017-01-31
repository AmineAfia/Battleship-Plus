from ...constants import Orientation, Direction

class Ship:

    # ship_type = ship type
    # x_pos = fixed point at x position
    # y_pos = fixed point at y position
    # x_length = x length of ship
    # y_length = y length of ship
    # orientation north=0, east=1
    # ship_state=[(x_pos, y_pos), state: 0=no damage, 1=damaged]
    def __init__(self, ship_id, ship_type, x_pos, y_pos, x_length, y_length, orientation):
        self._ship_id = ship_id
        self._ship_type = ship_type
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._x_length = x_length
        self._y_length = y_length
        self._orientation = orientation
        self._placed = False
        self._hit = False
        self._sunk = False
        self._ship_state = [[[] for _ in range (y_length)] for _ in range (x_length)]

        for i in range(self._x_length):
            for j in range(self._y_length):
                if self._orientation == Orientation.NORTH:
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]
                elif self._orientation == Orientation.EAST:
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]

        print("{} created. ship_id: {}. size = {}x{}. orientation={}".format(self._ship_type, self._ship_id, self._x_length, self._y_length, self._orientation))

    # move the ship to 0=north 1=east 2=south 3=west
    def move(self, direction):
        if direction >= 0 and direction <= 3:
            for i in range(self._x_length):
                for j in range(self._y_length):
                    [(x, y), state] = self._ship_state[i][j]

                    if direction == Direction.NORTH:
                        self._ship_state[i][j] = [(x, y - 1), state]
                        self._y_pos = self._y_pos - 1
                    elif direction == Direction.EAST:
                        self._ship_state[i][j] = [(x + 1, y), state]
                        self._x_pos = self._x_pos + 1
                    elif direction == Direction.SOUTH:
                        self._ship_state[i][j] = [(x, y + 1), state]
                        self._y_pos = self._y_pos + 1
                    elif direction == Direction.WEST:
                        self._ship_state[i][j] = [(x - 1, y), state]
                        self._x_pos = self._x_pos - 1
            return True
        else:
            return False

    def get_ship_type(self):
        return self._ship_type

    def get_ship_id(self):
        return self._ship_id

    def get_ship_coordinates(self):
        ship_coordinates = []
        for states in self._ship_state:
            for state in states:
                ship_coordinates.append(state[0])
        return ship_coordinates

    def is_ship_at_location(self, x_pos, y_pos):
        if self._placed:
            for i in range(self._x_length):
                for j in range(self._y_length):
                    if self._ship_state[i][j] == [(x_pos, y_pos), self._ship_state[i][j][1]]:
                        return True
        else:
            return False

    #rotate this ship
    def rotate_ship(self):
        if self._orientation == Orientation.NORTH:
            for i in range(self._x_length):
                for j in range(self._y_length):
                    self._ship_state[i][j] = [(j + self._y_pos, i + self._x_pos), (0)]
                    self._orientation = Orientation.EAST
            return True
        elif self._orientation == Orientation.EAST:
            for i in range(self._x_length):
                for j in range(self._y_length):
                    self._ship_state[i][j] = [(i + self._y_pos, j + self._x_pos), (0)]
                    self._orientation = Orientation.NORTH
            return True
        else:
            return False

    # replace this ship
    def place(self, x_pos, y_pos, orientation):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._orientation = orientation

        if self._orientation == Orientation.NORTH:
            for i in range(self._x_length):
                for j in range(self._y_length):
                    self._ship_state[i][j] = [(j + self._x_pos, i + self._y_pos), (0)]
            self._placed = True
            return True

        elif self._orientation == Orientation.EAST:
            for i in range(self._x_length):
                for j in range(self._y_length):
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]
            self._placed = True
            return True
        else:
            return False

    def is_placed(self):
        return self._placed

    def is_hit(self):
        return self._hit

    def is_sunk(self):
        return self._sunk

    def strike(self, x_pos, y_pos):
        hit_counter = 0
        for i in range(self._x_length):
            for j in range(self._y_length):
                [(x, y), state] = self._ship_state[i][j]

                if state == 1:
                    hit_counter = 1 + hit_counter

                if x == x_pos and y == y_pos:
                    self._ship_state[i][j] = [(x, y), (1)]
                    self._hit = True
                    hit_counter = 1 + hit_counter

        if hit_counter >= (self._x_length * self._y_length):
            self._sunk = True
            print("{} versenkt!".format(self._ship_type))

    def get_ship_length(self):
        return len(self._ship_state)

    def get_ship_coordinate(self):
        return self._x_pos, self._y_pos