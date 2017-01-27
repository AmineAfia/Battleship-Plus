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
        if (self._game_started):
            if (battlefield.move(ship_id, direction)):
                print("ship:{} moved to:{}".format(ship_id, direction))
            else:
                print("error - ship not moved")

    #strike at the coordinates on the enemy battlefield
    def strike(self, battlefield, x_pos, y_pos):
        if (self._game_started):
            print("strike at x={},y={}".format(x_pos, y_pos))
            if (battlefield.strike(x_pos, y_pos)):
                print("got it!")
            else:
                print("fail!")

    def startGame(self, battlefield):
        if (battlefield.placementFinished()):
            self._game_started = True
            print("game started")
        else:
            self._game_started = False
            print("placement not finished")



    #run the game controller with parameter:
    #   battlefieldlength
    #   ships_table: carrier, battleship, cruiser, destroyer, submarine
    def run(self, length, ships_table):

        if len(ships_table) == 5:
            if (length < 27 or length > 9):

                #create ships
                id = 1
                ships = []
                for i in range(5):
                    shipCount = ships_table[i]
                    for _ in range(shipCount):
                        if (i == 0):
                            ships.append(AircraftCarrier(id, 0, 0,Orientation.EAST))
                        if (i == 1):
                            ships.append(Battleship(id, 0, 0, Orientation.EAST))
                        if (i == 2):
                            ships.append(Cruiser(id, 0, 0,Orientation.EAST))
                        if (i == 3):
                            ships.append(Destroyer(id, 0, 0,Orientation.EAST))
                        if (i == 4):
                            ships.append(Submarine(id, 0, 0,Orientation.EAST))
                        id = id + 1

                #create battlefield
                battlefield = self.createBattlefield(length, ships)

                #ship placement
                battlefield.place(1, 0, 0, Orientation.EAST)
                battlefield.place(2, 0, 1, Orientation.EAST)

                ####################################################################################
                #if all ships are places and the game starts
                self.startGame(battlefield)


                self.move(battlefield, 1, Direction.EAST)

                self.strike(battlefield, 0, 0)
                self.strike(battlefield,1,0)
                self.strike(battlefield,2,0)

                #self.move(battlefield, 2, Direction.NORTH)

            else:
                print("wrong length")
        else:
            print("wrong number of ships")

