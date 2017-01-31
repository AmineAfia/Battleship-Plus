from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from .constants import Orientation, Direction, ErrorCode
from .errorHandler.BattleshipError import BattleshipError
from common.network import BattleshipClient


# Controller for Battleship
class GameController:

    def __init__(self, game_id, client):
        self._battlefield = object
        self._turn_counter = 0
        self._game_started = False
        self._game_id = game_id
        self._client = client

    @property
    def ships(self):
        return self._battlefield.ships

    @property
    def length(self):
        return self._battlefield.length

    # create a new battlefield
    def create_battlefield(self, length, ships):
        self._battlefield = Battlefield(length, ships)
        print("Battlefield {}x{} created.".format(length, length))

    def place_ship(self, ship_id, x_pos, y_pos, orientation):
        self._battlefield.place(ship_id, x_pos, y_pos, orientation)

    def start_game(self):
        if self._battlefield.placement_finished():
            self._game_started = True
            print("All ships are well placed. Game: {} started!".format(self._game_id))
            return True
        else:
            self._game_started = False
            print("Placement not finished.")
            return False

    # move your own ship on your battlefield
    def move(self, ship_id, direction):
        if self._game_started:
            if self._battlefield.move(ship_id, direction):
                print("ship:{} moved to:{}".format(ship_id, direction))
            else:
                print("error - ship not moved")

    # strike at the coordinates on the enemy battlefield
    def strike(self, x_pos, y_pos):
        if self._game_started:
            print("strike at x={},y={}".format(x_pos, y_pos))
            if self._battlefield.strike(x_pos, y_pos):
                print("got it!")
            else:
                print("fail!")

    # shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                print("shoot at x={}, y={}".format(x_pos, y_pos))
                self._battlefield.shoot(x_pos, y_pos)

    def abort(self):
        print("Game: {} aborted!".format(self._game_id))
        self = None

    # run the game controller with parameter:
    def run(self, cmd):

        if cmd[0] == "create":
            length = cmd[1]
            ships_table = cmd[2]
            if len(ships_table) == 5:
                if length < 27 and length > 9:
                    # create ships
                    id = 0
                    ships = []
                    for i in range(5):
                        shipCount = ships_table[i]
                        for _ in range(shipCount):
                            id = id + 1
                            if i == 0:
                                ships.append(AircraftCarrier(id, 0, 0, Orientation.EAST))
                            if i == 1:
                                ships.append(Battleship(id, 0, 0, Orientation.EAST))
                            if i == 2:
                                ships.append(Cruiser(id, 0, 0, Orientation.EAST))
                            if i == 3:
                                ships.append(Destroyer(id, 0, 0, Orientation.EAST))
                            if i == 4:
                                ships.append(Submarine(id, 0, 0, Orientation.EAST))
                    # create battlefield
                    self.create_battlefield(length, ships)
                else:
                    raise BattleshipError(ErrorCode.SYNTAX_INVALID_BOARD_SIZE)
            else:
                pass

        # def place(self, ship_id, x_pos, y_pos, orientation):
        if cmd[0] == "place":
            ship_id = cmd[1]
            x_pos = cmd[2]
            y_pos = cmd[3]
            orientation = cmd[4]
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                if self._battlefield.ship_id_exists(ship_id):
                    self.place_ship(ship_id, x_pos, y_pos, orientation)
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

        # def start_game()
        if cmd[0] == "start":
            self.start_game()

        # def move(self, ship_id, direction)
        if cmd[0] == "move":
            ship_id = cmd[1]
            direction = cmd[2]
            if self._battlefield.ship_is_moveable(ship_id):
                if self._battlefield.ship_id_exists(ship_id):
                    self.move(ship_id, direction)
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_SHIP_IMMOVABLE)

        # def strike(self, x_pos, y_pos)
        if cmd[0] == "strike":
            x_pos = cmd[1]
            y_pos = cmd[2]
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                self.strike(x_pos, y_pos)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

        if cmd[0] == "shoot":
            x_pos = cmd[1]
            y_pos = cmd[2]
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                self.shoot(x_pos, y_pos)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

        if cmd[0] == "abort":
            self.abort()

