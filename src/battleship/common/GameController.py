from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from .constants import Orientation, Direction, ErrorCode
from .errorHandler.BattleshipError import BattleshipError
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType


# Controller for Battleship
class GameController:

    def __init__(self, game_id, client):
        self._battlefield = object
        self._turn_counter = 0
        self._game_started = False
        self._game_id = game_id

        self._round_time = 0
        self._options = 0
        self._username = ""
        self._opponent_name = ""
        self._password = ""

        self._client = client

    @property
    def ships(self):
        return self._battlefield.ships

    @property
    def length(self):
        return self._battlefield.length

    @property
    def ships_not_placed(self):
        return self._battlefield.ships_not_placed

    def get_ship_id_from_location(self, pos_x, pos_y):
        result = self._battlefield.get_ship_id_from_location(pos_x, pos_y)
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_NO_SHIP_AT_LOCATION)

    def get_next_ship_id_to_place(self):
        result = self._battlefield.get_next_ship_id_to_place()
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_NO_MORE_SHIP_TO_PLACE)

    def get_next_ship_id_by_type_to_place(self, ship_type):
        result = self._battlefield.get_next_ship_id_by_type_to_place(ship_type)
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_NO_MORE_SHIP_TO_PLACE_OF_TYPE)

    def get_ship_type_by_id(self, ship_id):
        result = self._battlefield.get_ship_type_by_id(ship_id)
        if result is not None:
            return result
        else:
            raise BattleshipError(ErrorCode.INTERN_SHIP_ID_DOES_NOT_EXIST)

    def get_ship_list_to_place(self):
        return

    # create a new battlefield
    def create_battlefield(self, length, ships_table):
        if 9 < length < 27:
            identification = 0
            ships = []
            for i in range(5):
                ship_count = ships_table[i]
                for _ in range(ship_count):
                    if i == 0:
                        ships.append(AircraftCarrier(identification, 0, 0, Orientation.EAST))
                    elif i == 1:
                        ships.append(Battleship(identification, 0, 0, Orientation.EAST))
                    elif i == 2:
                        ships.append(Cruiser(identification, 0, 0, Orientation.EAST))
                    elif i == 3:
                        ships.append(Destroyer(identification, 0, 0, Orientation.EAST))
                    elif i == 4:
                        ships.append(Submarine(identification, 0, 0, Orientation.EAST))
                    identification += 1
            self._battlefield = Battlefield(length, ships, ships_table)
            if length * length * 0.3 > self._battlefield.calc_filled():
                # needs to return the battlefield for the cmd-line downside
                return self._battlefield
            else:
                raise BattleshipError(ErrorCode.PARAMETER_TOO_MANY_SHIPS)
        else:
            raise BattleshipError(ErrorCode.SYNTAX_INVALID_BOARD_SIZE)

    def place_ship(self, ship_id, x_pos, y_pos, orientation):
        if self._battlefield.no_border_crossing(x_pos, y_pos):
            if self._battlefield.ship_id_exists(ship_id):
                if self._battlefield.no_ship_at_place(x_pos, y_pos):
                    try:
                        orientation = Orientation(orientation)
                    except ValueError:
                        # return False
                        raise BattleshipError(ErrorCode.SYNTAX_INVALID_PARAMETER)
                    if self._battlefield.place(ship_id, x_pos, y_pos, orientation):
                        return True
                    else:
                        return False
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
        else:
            raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)

    def start_game(self):
        if self._battlefield.placement_finished():
            self._game_started = True
            return True
        else:
            self._game_started = False
            return False

    # move your own ship on your battlefield
    def move(self, ship_id, direction):
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
                            self._battlefield.move(ship_id, direction)
                        else:
                            raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
                    else:
                        raise BattleshipError(ErrorCode.PARAMETER_OVERLAPPING_SHIPS)
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_SHIP_IMMOVABLE)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_INVALID_SHIP_ID)
        else:
            return False

    # strike at the coordinates on the enemy battlefield
    def strike(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                if self._battlefield.no_strike_at_place(x_pos, y_pos):
                    if self._battlefield.strike(x_pos, y_pos):
                        # todo call UI for a successful enemy strike(x,y)
                        pass
                    else:
                        # todo call UI for a missed enemy strike(x,y)
                        pass
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_ALREADY_HIT_POSITION)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
        else:
            return False

    # shoot at enemy battlefield
    def shoot(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                if self._battlefield.no_hit_at_place(x_pos, y_pos):
                    if self._battlefield.shoot(x_pos, y_pos):
                        return True
                    else:
                        return False
                else:
                    raise BattleshipError(ErrorCode.PARAMETER_ALREADY_HIT_POSITION)
            else:
                raise BattleshipError(ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS)
        else:
            return False

    def all_ships_sunk(self):
        return self._battlefield.all_ships_sunk()

    def get_all_ship_states(self):
        return self._battlefield.get_all_ship_states()

    def increase_turn_counter(self):
        if self._turn_counter >= 256:
            self._turn_counter = 0
        else:
            self._turn_counter += 1

    def abort(self):
        #self = None
        return True

    # interface to client and server
    def run(self, msg: ProtocolMessage):

        # CLIENT -> SERVER
        # CLIENT MESSAGES: CREATE_GAME, PLACE, MOVE, SHOOT, ABORT
        if msg.type == ProtocolMessageType.CREATE_GAME:
            length = msg.parameters["board_size"]
            ships_table = msg.parameters["num_ships"].numbers
            opponent_name = msg.parameters["opponent_name"]
            round_time = msg.parameters["round_time"]
            password = msg.parameters["password"]
            self._battlefield = self.create_battlefield(length, ships_table)
            self._round_time = round_time
            self._password = password
            self._opponent_name = opponent_name

        # Sends the server a list of ship placements. The list MUST be ordered by ship type as specified in the instruction.
        elif msg.type == ProtocolMessageType.PLACE:
            ship_positions = msg.parameters["ship_positions"]
            ship_id = 0
            if len(ship_positions.positions) == self._battlefield.count_ships():
                for ship_position in ship_positions.positions:
                    x_pos = ship_position.position.horizontal
                    y_pos = ship_position.position.vertical
                    orientation = ship_position.orientation
                    self.place_ship(ship_id, x_pos, y_pos, orientation)
                    ship_id += 1
            else:
                raise BattleshipError(ErrorCode.PARAMETER_WRONG_NUMBER_OF_SHIPS)

        # Moves a ship
        elif msg.type == ProtocolMessageType.MOVE:
            ship_id = msg.parameters["ship_id"]
            direction = msg.parameters["direction"]
            turn_counter = msg.parameters["turn_counter"]
            self.move(ship_id, direction)

        # Shoots the specified position of the opponents board.
        elif msg.type == ProtocolMessageType.SHOOT:
            x_pos = msg.parameters["ship_position"].position.horizontal
            y_pos = msg.parameters["ship_position"].position.vertical
            turn_counter = msg.parameters["turn_counter"]
            if self.strike(x_pos, y_pos):
                # todo HIT
                # todo call UI for HIT(x,y)
                return True
            else:
                # todo FAIL
                # todo call UI for FAIL(x,y)
                return False

        # This message tells the server that the client wants to abort the game. The user may communicate via the chat.
        elif msg.type == ProtocolMessageType.ABORT:
            turn_counter = msg.parameters["turn_counter"]
            self.abort()

        # SERVER -> CLIENTS
        # SERVER MESSAGES: STARTGAME, PLACED, YOUSTART, WAIT, HIT, FAIL, MOVED, TIMEOUT, ENDGAME

        # Initial message to start the game. The message MUST be sent to both clients
        elif msg.type == ProtocolMessageType.STARTGAME:
            self._length = msg.parameters["board_size"]
            self._ships_table = msg.parameters["num_ships"]
            self._opponent_name = msg.parameters["opponent_name"]
            self._round_time = msg.parameters["round_time"]

        # This message MUST be sent to the client who has the first turn. It is sent only once after the STARTGAME message.
        elif msg.type == ProtocolMessageType.YOUSTART:
            pass

        # This message MUST be sent to the client who hast to wait for the opponent's first turn. It is sent only once after the STARTGAME message
        elif msg.type == ProtocolMessageType.WAIT:
            pass

        # This message is sent to both clients
        elif msg.type == ProtocolMessageType.HIT:
            sunk = msg.parameters["sunk"]
            position = msg.parameters["position"]
            self.increase_turn_counter()

        # The last shot was unsuccessful. This message is sent to both clients.
        elif msg.type == ProtocolMessageType.FAIL:
            position = msg.parameters["position"]
            self.increase_turn_counter()

        # A ship was moved. If the ship was moved to already shot fields, these fields are mentioned in the positions. This message is sent to both clients.
        elif msg.type == ProtocolMessageType.MOVED:
            self.increase_turn_counter()

        # The current turn ended because of a timeout. This message is sent to both clients.
        elif msg.type == ProtocolMessageType.TIMEOUT:
            self.increase_turn_counter()

        # The opponent placed ships
        elif msg.type == ProtocolMessageType.PLACED:
            pass

        # The current game ended because of a known reason. This message is sent to both clients
        elif msg.type == ProtocolMessageType.ENDGAME:
            reason = msg.parameters["reason"]
            self.abort()

        # unknown command
        else:
            raise BattleshipError(ErrorCode.UNKNOWN)