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
        self._battlefield = object
        self._turn_counter = 0
        self._game_started = False


    #create a new battlefield
    def createBattlefield(self, length, ships):
        self._battlefield = Battlefield(length, ships)

    def placeShip(self, ship_id, x_pos, y_pos, orientation):
        self._battlefield.place(ship_id, x_pos, y_pos, orientation)

    def startGame(self):
        if (self._battlefield.placementFinished()):
            self._game_started = True
            print("All ships are well placed.")
            print("Game started!")
        else:
            self._game_started = False
            print("Placement not finished.")

    #move your own ship on your battlefield
    def move(self, ship_id, direction):
        if (self._game_started):
            if (self._battlefield.move(ship_id, direction)):
                print("ship:{} moved to:{}".format(ship_id, direction))
            else:
                print("error - ship not moved")

    #strike at the coordinates on the enemy battlefield
    def strike(self, x_pos, y_pos):
        if (self._game_started):
            print("strike at x={},y={}".format(x_pos, y_pos))
            if (self._battlefield.strike(x_pos, y_pos)):
                print("got it!")
            else:
                print("fail!")


    #run the game controller with parameter:
    #   battlefieldlength
    #   ships_table: carrier, battleship, cruiser, destroyer, submarine
    def run(self, length, ships_table):

        if len(ships_table) == 5:
            if (length < 27 or length > 9):

                #create ships
                id = 0
                ships = []
                for i in range(5):
                    shipCount = ships_table[i]
                    for _ in range(shipCount):
                        id = id + 1
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

                #create battlefield
                self.createBattlefield(length, ships)

            else:
                print("wrong length")
        else:
            print("wrong number of ships")


    def place(self, ship_id, x_pos, y_pos, orientation):
                self.placeShip(ship_id, x_pos, y_pos, orientation)

                #if all ships are places and the game starts
                self.startGame()



    def play(self):
            self.move(1, Direction.EAST)

            self.strike(0, 0)
            self.strike(1,0)
            self.strike(2,0)

#Commands: PLACE, MOVE, STRIKE, SHOOT,



