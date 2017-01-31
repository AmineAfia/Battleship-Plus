from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from .constants import Orientation, Direction, ErrorCode
from .errorHandler.BattleshipError import BattleshipError
from common.protocol import ProtocolMessage, ProtocolMessageType

# Controller for Battleship
class GameController:

    def __init__(self, game_id):
        self._battlefield = object
        self._turn_counter = 0
        self._game_started = False
        self._game_id = game_id

        self._round_time = 0
        self._options = 0
        self._username = ""
        self._password = ""

    @property
    def ships(self):
        return self._battlefield.ships

    @property
    def length(self):
        return self._battlefield.length

    # create a new battlefield
    def create_battlefield(self, length, ships_table):
        if 9 < length < 27:
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
            self._battlefield = Battlefield(length, ships, ships_table)
            print("Battlefield {}x{} created.".format(length, length))
            if length * length * 0.3 > self._battlefield.calc_filled():
                return True
            else:
                return False
        else:
            return False

    def place_ship(self, ship_id, x_pos, y_pos, orientation):
        if self._battlefield.place(ship_id, x_pos, y_pos, orientation):
            return True
        else:
            return False

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
            if self._battlefield.ship_is_moveable(ship_id):
                x_pos, y_pos = self._battlefield.get_ship_coordinate(ship_id)
                if self._battlefield.no_ship_at_place_but(x_pos, y_pos , ship_id):
                    x_pos, y_pos = self._battlefield.get_move_coordinate(ship_id, direction)
                    if self._battlefield.no_border_crossing(x_pos, y_pos):
                        if self._battlefield.move(ship_id, direction):
                            print("ship:{} moved to:{}".format(ship_id, direction))
                            return True
                        else:
                            print("error - ship not moved")
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    # strike at the coordinates on the enemy battlefield
    def strike(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                print("strike at x={},y={}".format(x_pos, y_pos))
                if self._battlefield.strike(x_pos, y_pos):
                    print("got it!")
                else:
                    print("fail!")
            else:
                return False
        else:
            return False

    # shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                print("shoot at x={}, y={}".format(x_pos, y_pos))
                self._battlefield.shoot(x_pos, y_pos)
            else:
                return False
        else:
            return False

    def abort(self):
        print("Game: {} aborted!".format(self._game_id))
        self = None

    # interface to client
    def run(self, msg: ProtocolMessage):

        if msg.type == ProtocolMessageType.CREATE_GAME:
            length = msg.parameters["board_size"]
            ships_table = msg.parameters["num_ships"]
            if 9 < length < 27:
                if self.create_battlefield(length, ships_table.numbers):
                    return True
                else:
                    return False
            else:
                raise BattleshipError(ErrorCode.SYNTAX_INVALID_BOARD_SIZE)

        #if cmd[0] == "place":
        if msg.type == ProtocolMessageType.PLACE:
            ship_positions = msg.parameters["ship_positions"]
            ship_id = 0
            if len(ship_positions.positions) == self._battlefield.count_ships():
                for ship_position in ship_positions.positions:
                    ship_id = ship_id + 1
                    x_pos = ship_position.position.horizontal
                    y_pos = ship_position.position.vertical
                    orientation = ship_position.orientation

                    if self._battlefield.no_border_crossing(x_pos, y_pos):
                        if self._battlefield.ship_id_exists(ship_id):
                            if self._battlefield.no_ship_at_place(x_pos, y_pos):
                                try:
                                    orientation = Orientation(orientation)
                                except ValueError:
                                    raise BattleshipError(ErrorCode.SYNTAX_INVALID_PARAMETER)
                                self.place_ship(ship_id, x_pos, y_pos, orientation)
                            else:
                                raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
                        else:
                            raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
                    else:
                        raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_WRONG_NUMBER_OF_SHIPS)

        #if msg.type == ProtocolMessageType.START_GAME:
            #self.start_game()

        # todo: not the clients turn and turn counter invalid
        #if cmd[0] == "move":
        if msg.type == ProtocolMessageType.MOVE:
            ship_id = msg.parameters["ship_id"]
            direction = msg.parameters["direction"]
            if self._game_started:
                if self._battlefield.ship_id_exists(ship_id):
                    if self._battlefield.ship_is_moveable(ship_id):
                        x_pos, y_pos = self._battlefield.get_ship_coordinate(ship_id)
                        if self._battlefield.no_ship_at_place_but(x_pos, y_pos, ship_id):
                            x_pos, y_pos = self._battlefield.get_move_coordinate(ship_id, direction)
                            if self._battlefield.no_border_crossing(x_pos, y_pos):
                                try:
                                    direction = Direction(direction)
                                except ValueError:
                                    raise BattleshipError(ErrorCode.SYNTAX_INVALID_PARAMETER)
                                if self.move(ship_id, direction):
                                    return True
                                else:
                                    return False
                            else:
                                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
                        else:
                            raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
                    else:
                        raise BattleshipError(ErrorCode.PARAMETER_SHIP_IMMOVABLE)
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
            else:
                print("game not started")

        # todo: not the clients turn and turn counter invalid
        #if cmd[0] == "strike":
        if msg.type == ProtocolMessageType.SHOOT:
            x_pos = msg.parameters["ship_position"].position.horizontal
            y_pos = msg.parameters["ship_position"].position.vertical
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                self.strike(x_pos, y_pos)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

        #if cmd[0] == "shoot":
        #if msg.type == ProtocolMessageType.SHOOT:
            #x_pos = cmd[1]
            #y_pos = cmd[2]
            #if self._battlefield.no_border_crossing(x_pos, y_pos):
                #self.shoot(x_pos, y_pos)
            #else:
                #raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

        #if cmd[0] == "abort":
        if msg.type == ProtocolMessageType.ABORT:
            self.abort()

