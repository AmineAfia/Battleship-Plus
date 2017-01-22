from battlefield.Battlefield import Battlefield
from battlefield.battleship.AircraftCarrier import AircraftCarrier
from battlefield.battleship.Battleship import Battleship
from battlefield.battleship.Cruiser import Cruiser
from battlefield.battleship.Destroyer import Destroyer
from battlefield.battleship.Submarine import Submarine

#Controller for Battleship+
class GameController:
    game_name = "Battleship+"
    ships = []

    turn_counter = 0

    #create a new battlefield
    def createGame(length, ships):
        return Battlefield(length, ships)

    #move your own ship on your battlefield
    def move(battlefield, ship_id, direction):
        if (battlefield.move(ship_id, direction)):
            print("moved ship")
        else:
            print("error - ship not moved")

    #strike at the coordinates on the enemy battlefield
    def strike(battlefield, x_pos, y_pos):
        print("strike at x={},y={}".format(x_pos, y_pos))
        if (battlefield.strike(x_pos, y_pos)):
            print("got it!")
        else:
            print("fail!")



    #here we go
    if __name__ == "__main__":

        print("creating battlefield with ships...")

        #size = 5x5
        length = 5
        #added a Battleship ship_id=1, x=1, y=1, orientation = 0(north) or 1(east)
        #ships.append(Battleship(0,0,0,1))
        #ships.append(Cruiser(1,0,0,1))
        #ships.append(Destroyer(2,0,0,1))
        ships.append(Submarine(3,0,0,1))
        #ships.append(AircraftCarrier(4,0,0,1))

        battlefield = createGame(length, ships)

        move(battlefield,3,2)

        strike(battlefield,0,0)
        strike(battlefield,0,1)
        strike(battlefield,1,1)

