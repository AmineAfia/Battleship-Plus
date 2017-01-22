class Ship:

    #ship_type = ship type
    #x_pos = fixed point at x position
    #y_pos = fixed point at y position
    #x_length = x length of ship
    #y_length = y length of ship
    def __init__(self, ship_id, ship_type, x_pos, y_pos, x_length, y_length, orientation):
        self._ship_id = ship_id
        self._ship_type = ship_type
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._x_length = x_length
        self._y_length = y_length
        self._orientation = orientation
        self._hit_counter = 0
        self._hitMap = [[0 for x in range(x_length)] for y in range(y_length)]
        print("Created Ship: {} with ship_id: {}".format(self._ship_type, self._ship_id))
        print("Fixed at x={}, y={}, orientation={}".format(x_pos, y_pos,orientation))
        print("Size = {}x{}".format(x_pos, y_pos))

    #can not move it hit
    def move(self, x_pos, y_pos):
        print("move {} at x={},y={}".format(self._ship_id, x_pos, y_pos))

    #return if enemy get a score
    def hit(self, x_pos, y_pos):
        hit = False

        if (hit):
            self._hit_counter = self._hit_counter + 1
            print("im hurt")
        else:
            print("easy peasy")
        return hit

    def alive(self):
        alive = True
        if(self._hit_counter == self._x_length * self._y_length):
            alive = False
        return alive






