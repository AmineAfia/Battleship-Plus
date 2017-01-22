from .battleship import Ship

class Battlefield:

    #length = battlefield length <length> x <length>
    #ships = linked list of ships
    def __init__(self, length, ships):
        self._length = length
        self._ships = ships
        print("New Battlefield created with size {}x{}".format(length, length))
        print(self._ships._ship_type)


    def move(self, ship_id, x_pos, y_pos):
        print("move {} at x={},y={}".format(ship_id, x_pos, y_pos))

    def shoot(self, x_pos, y_pos):
        hit = False
        print("shoot at x={},y={}".format(x_pos, y_pos))


        if(hit):
            print("boooooom!!!!!")
        else:
            print("fail!")
        return hit

    def hit(self, x_pos, y_pos):
        x = 0

