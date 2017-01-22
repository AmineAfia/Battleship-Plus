from battlefield.Battlefield import Battlefield
from battlefield.battleship.AircraftCarrier import AircraftCarrier
from battlefield.battleship.Battleship import Battleship
from battlefield.battleship.Cruiser import Cruiser
from battlefield.battleship.Destroyer import Destroyer
from battlefield.battleship.Submarine import Submarine

#Controller for Battleship+
class GameController:
    battlefield = {}
    game_name = {}
    ships = {}

    #create a new battlefield
    def createGame(length, ships):
        game_name = "Battleship+"
        battlefield = Battlefield(length, ships)

    #move your own ship on your battlefield
    def move(battlefield, ship_id, x_pos, y_pos):
        battlefield.move(battlefield, ship_id, x_pos, y_pos)
        #print("move {} at x=={},y={}".format(ship_id, x_pos, y_pos))

    #shoot at the coordinates on the enemy battlefield
    def shoot(x_pos, y_pos):
        print("shoot at x={},y={}".format(x_pos, y_pos))

    #here we go
    if __name__ == "__main__":

        print("creating battlefield with ships...")

        #size = 5x5
        length = 5
        #added a Battleship ship_id=1, x=1, y=1, orientation = 0(north) or 1(east)
        ships = Battleship(1,1,1,1)


        createGame(length, ships)




