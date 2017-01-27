from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from .constants import Orientation, Direction

#Controller for Battleship+
class GameController:

    def __init__(self):
        self._turn_counter = 0
        self._game_started = False


    #create a new battlefield
    def createBattlefield(self, length, ships):
        return Battlefield(length, ships)

    #move your own ship on your battlefield
    def move(self, battlefield, ship_id, direction):
        if (battlefield.move(ship_id, direction)):
            print("ship:{} moved to:{}".format(ship_id, direction))
        else:
            print("error - ship not moved")

    #strike at the coordinates on the enemy battlefield
    def strike(self, battlefield, x_pos, y_pos):
        print("strike at x={},y={}".format(x_pos, y_pos))
        if (battlefield.strike(x_pos, y_pos)):
            print("got it!")
        else:
            print("fail!")

    def startGame(self, battlefield):
        if (battlefield.placementFinished()):
            print("game started")
        else:
            print("placement not finished")



    #run the game controller
    #first: create all ships with unique index
    #second: create a new battlefield with a fixed length and ships
    #third: ship placement
    #forth: start game
    #sixth: shoot or move until game is finished
    def run(self):
        print("creating battlefield with ships...")

        #size = 5x5
        length = 5
        #added a Battleship ship_id=1, x=1, y=1, orientation = 0(north) or 1(east)
        #ships.append(Battleship(0,0,0,1))
        #ships.append(Cruiser(1,0,0,1))
        #ships.append(Destroyer(2,0,0,1))
        #ships.append(Submarine(3,0,0,1))
        ships = []

        ships.append(AircraftCarrier(4, 0, 0,Orientation.EAST))
        ships.append(AircraftCarrier(5, 0, 0, Orientation.EAST))

        battlefield = self.createBattlefield(length, ships)
        #placed flag
        battlefield.place(4, 0, 0, Orientation.EAST)
        battlefield.place(5, 0, 2, Orientation.EAST)

        #if all ships are places
        self.startGame(battlefield)


        self.move(battlefield, 4, Direction.EAST)

        #self.strike(battlefield, 0, 0)
        #self.strike(battlefield,10,10)
        #self.strike(battlefield,0,0)

