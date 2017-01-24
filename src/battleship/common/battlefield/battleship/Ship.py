from ...constants import Orientation, Direction

class Ship:

    #ship_type = ship type
    #x_pos = fixed point at x position
    #y_pos = fixed point at y position
    #x_length = x length of ship
    #y_length = y length of ship
    #orientation north=0, east=1
    #ship_state=[(x_pos, y_pos), state: 0=no damage, 1=damaged]
    def __init__(self, ship_id, ship_type, x_pos, y_pos, x_length, y_length, orientation):
        self._ship_id = ship_id
        self._ship_type = ship_type
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._x_length = x_length
        self._y_length = y_length
        self._orientation = orientation
        self._placed = False
        self._hit_counter = 0
        #self._ship_state = [[] for _ in range (x_length + y_length - 1)]

        self._ship_state = [[[] for _ in range (y_length)] for _ in range (x_length)]

        if (self._orientation == Orientation.NORTH):
            for i in range (self._x_length):
                for j in range (self._y_length):
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]


        elif (self._orientation == Orientation.EAST):
            for i in range (self._x_length):
                for j in range (self._y_length):
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]


        print (self._ship_state)


        print("Created Ship: {} with ship_id: {}".format(self._ship_type, self._ship_id))
        print("Fixed at x={}, y={}, orientation={}".format(x_pos, y_pos,orientation))
        print("Size = {}x{}".format(self._x_length, self._y_length))

    #move the ship to 0=north 1=east 2=south 3=west
    def move(self, direction):
        if (self._hit_counter == 0 and direction >= 0 and direction <=3):
            if (direction == Direction.NORTH):
                for i in range(self._x_length):
                    for j in range(self._y_length):
                        [(x,y), state] = self._ship_state[i][j]
                        self._ship_state[i][j] = [(x, y - 1), state]
                print(self._ship_state)
                #self._y_pos = self._y_pos - 1
            if (direction == Direction.EAST):
                for i in range(self._x_length):
                    for j in range(self._y_length):
                        [(x,y), state] = self._ship_state[i][j]
                        self._ship_state[i][j] = [(x + 1, y), state]
                print(self._ship_state)
                #self._x_pos = self._x_pos + 1
            if (direction == Direction.SOUTH):
                for i in range(self._x_length):
                    for j in range(self._y_length):
                        [(x,y), state] = self._ship_state[i][j]
                        self._ship_state[i][j] = [(x, y + 1), state]
                print(self._ship_state)
                #self._y_pos = self._y_pos + 1
            if (direction == Direction.WEST):
                for i in range(self._x_length):
                    for j in range(self._y_length):
                        [(x,y), state] = self._ship_state[i][j]
                        self._ship_state[i][j] = [(x - 1, y), state]
                print(self._ship_state)
                #self._x_pos = self._x_pos - 1
            #print("move ship={} to x={} y={}".format(self._ship_id, self._x_pos, self._y_pos))
            return True
        else:
            return False

    def alive(self):
        for i in range(self._x_length):
            for j in range(self._y_length):
                [(x, y), state] = self._ship_state[i][j]
                if (state == 0):
                    return True
        return False

    def strikeAtPosition(self, x_pos, y_pos):
        for i in range(self._x_length):
            for j in range(self._y_length):
                if (self._ship_state[i][j] == [(x_pos, y_pos), self._ship_state[i][j][1]]):
                    self._ship_state[i][j] = [(self._ship_state[i][j][0]), 1]
                    return True
        return False

    def getShipType(self):
        return self._ship_type

    def getShipId(self):
        return self._ship_id

    def getShipCoordinates(self):
        shipCoordinates = []
        for states in self._ship_state:
            for state in states:
                shipCoordinates.append(state[0])
        return shipCoordinates

    #boolean flag if placed already
    def isShipAtLocation(self, x_pos, y_pos):
        if (self._placed):
            for i in range(self._x_length):
                for j in range(self._y_length):
                    if (self._ship_state[i][j] == [(x_pos, y_pos), self._ship_state[i][j][1]]):
                        return True
        return False

    #rotate this ship
    def rotateShip(self):
        if (self._orientation == Orientation.NORTH):
            for i in range (self._x_length):
                for j in range (self._y_length):
                    self._ship_state[i][j] = [(j + self._y_pos, i + self._x_pos), (0)]


        elif (self._orientation == Orientation.EAST):
            for i in range (self._x_length):
                for j in range (self._y_length):
                    self._ship_state[i][j] = [(j + self._y_pos, i + self._x_pos), (0)]

    #replace this ship
    def place(self, x_pos, y_pos, orientation):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._orientation = orientation

        if (self._orientation == Orientation.NORTH):
            for i in range (self._x_length):
                for j in range (self._y_length):
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]


        elif (self._orientation == Orientation.EAST):
            for i in range (self._x_length):
                for j in range (self._y_length):
                    self._ship_state[i][j] = [(i + self._x_pos, j + self._y_pos), (0)]

        self._placed = True
        print(self._ship_state)

    def isPlaced(self):
        return self._placed




