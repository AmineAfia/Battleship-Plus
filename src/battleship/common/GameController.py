import time
import asyncio
from typing import Callable
from .battlefield.Battlefield import Battlefield
from .battlefield.battleship.AircraftCarrier import AircraftCarrier
from .battlefield.battleship.Battleship import Battleship
from .battlefield.battleship.Cruiser import Cruiser
from .battlefield.battleship.Destroyer import Destroyer
from .battlefield.battleship.Submarine import Submarine
from common.constants import Orientation, Direction, ErrorCode, GameOptions
from .errorHandler.BattleshipError import BattleshipError
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType, NumShips, ShipPositions
from common.game import GameLobbyData
from common.states import GameState


# Controller for Battleship
class GameController(GameLobbyData):

    def __init__(self, game_id, client, loop):
        super().__init__(game_id)
        self.loop = loop
        self._battlefield = object
        self._turn_counter: int = 0
        self._start_time = time.time()
        self._game_started: bool = False
        self._opponent_name: str = ""
        self._password: str = ""
        self.timeout_counter: int = 0
        self._timeout_handle: asyncio.Handle = None
        self.client = client

    @classmethod
    async def create_from_msg(cls, game_id, client, loop, msg: ProtocolMessage, username):
        controller = cls(game_id, client, loop)

        controller.username = username

        params = msg.parameters

        board_size, num_ships = params["board_size"], params["num_ships"].numbers

        try:
            controller.round_time, controller.options = params["round_time"], params["options"]
        except BattleshipError as e:
            if e.error_code in [ErrorCode.PARAMETER_OPTION_NOT_SUPPORTED, ErrorCode.SYNTAX_INVALID_PARAMETER]:
                answer = ProtocolMessage.create_error(e.error_code)
                await client.send(answer)
                return None

        if controller.options == GameOptions.PASSWORD:
            try:
                controller.password = msg.parameters["password"]
            except KeyError:
                # If it is set, the password field MUST NOT be empty, otherwise the server replies with an ERROR code 10 message.
                answer = ProtocolMessage.create_error(ErrorCode.SYNTAX_MISSING_OR_UNKNOWN_PARAMETER)
                await client.send(answer)
                return None
            except BattleshipError as e:
                if e.error_code in [ErrorCode.SYNTAX_PASSWORD_TOO_LONG, ErrorCode.SYNTAX_MISSING_OR_UNKNOWN_PARAMETER]:
                    answer = ProtocolMessage.create_error(e.error_code)
                    await client.send(answer)
                    return None

        try:
            controller._battlefield = controller.create_battlefield(board_size, num_ships)
        except BattleshipError as e:
            if e.error_code in [ErrorCode.PARAMETER_TOO_MANY_SHIPS, ErrorCode.SYNTAX_INVALID_BOARD_SIZE]:
                answer = ProtocolMessage.create_error(e.error_code)
                await client.send(answer)
                return None

        # answer client OK
        return controller

    @classmethod
    def create_from_existing_for_opponent(cls, other_ctrl, client):
        new_ctrl = cls(other_ctrl.game_id, client, other_ctrl.loop)

        new_ctrl.username = client.username
        new_ctrl.opponent_name = other_ctrl.username
        new_ctrl.round_time = other_ctrl.round_time
        new_ctrl.options = other_ctrl.options
        new_ctrl.password = other_ctrl.password
        new_ctrl._battlefield = new_ctrl.create_battlefield(other_ctrl.length, other_ctrl.ships)

        return new_ctrl

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if len(password) > 255:
            raise BattleshipError(ErrorCode.SYNTAX_PASSWORD_TOO_LONG)
        elif self.options == GameOptions.PASSWORD and len(password) == 0:
            raise BattleshipError(ErrorCode.SYNTAX_MISSING_OR_UNKNOWN_PARAMETER)
        else:
            self._password = password

    @property
    def opponent_name(self):
        return self._opponent_name

    @opponent_name.setter
    def opponent_name(self, opponent_name):
        self._opponent_name = opponent_name

    @property
    def ships(self):
        return self._battlefield.ships

    @property
    def length(self):
        return self._battlefield.length

    @property
    def ships_not_placed(self):
        return self._battlefield.ships_not_placed

    @property
    def game_state(self):
        return self._state

    @property
    def turn_counter(self):
        return self._turn_counter

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

    # todo: ich verbesser das nochmal
    def get_ship_orientation_by_id(self, ship_id):
        for ship in self._battlefield._ships:
            if ship.get_ship_id() == ship_id:
                return ship._orientation

    async def create_on_server(self, board_size, num_ships, round_time, options, password):
        self.round_time = round_time
        self.options = options
        self.password = password
        self._battlefield = self.create_battlefield(board_size, num_ships)

        # if we reach this point, no exception was raised on we can try
        # to send this game to the server
        await self.client.send_and_wait_for_answer(self.to_create_game_msg())

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    def get_ship_state_with_type(self, ship_type):
        return self._battlefield.get_ship_state_with_type(ship_type)

    def start_round_time(self):
        self._start_time = time.time()

    def get_round_time(self):
        if self._round_time > time.time() - self._start_time:
            return round(self._round_time - time.time() - self._start_time, 0)
        else:
            return 0

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
                            # todo differentiate if called from UI -> SEND MSG TO SERVER AND WAIT FOR ANSWER -> Set new state
                            # todo if called from CLIENT -> set new state and answer to Client OK
                            # TODO: does this never return False after our checks above?
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

    # strike at the coordinates on my own battlefield
    def strike(self, x_pos, y_pos):
        if self._game_started:
            if self._battlefield.no_border_crossing(x_pos, y_pos):
                if self._battlefield.no_strike_at_place(x_pos, y_pos):
                    if self._battlefield.strike(x_pos, y_pos):
                        # todo call UI for a successful enemy strike(x,y)
                        return True
                    else:
                        # todo call UI for a missed enemy strike(x,y)
                        return False
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

    def ship_sunk_at_pos(self, x_pos, y_pos):
        return self._battlefield.get_ship_from_location(x_pos, y_pos).is_sunk()

    def get_all_ship_states(self):
        return self._battlefield.get_all_ship_states()

    def get_all_ships_coordinates(self):
        return self._battlefield.get_all_ships_coordinates()

    def increase_turn_counter(self):
        if self._turn_counter >= 256:
            self._turn_counter = 0
        else:
            self._turn_counter += 1

    def get_placed_ships(self):
        ship_positions = []
        for ship in self._battlefield._ships:
            ship_positions.append(ship.get_ship_position())
        return ship_positions

    def abort(self):
        self = None
        return True

    # interface to client and server
    def run(self, msg: ProtocolMessage):

        # CLIENT -> SERVER
        # CLIENT MESSAGES: CREATE_GAME, PLACE, MOVE, SHOOT, ABORT
        # if msg.type == ProtocolMessageType.CREATE_GAME:
            # length = msg.parameters["board_size"]
            # ships_table = msg.parameters["num_ships"].numbers
            # self._round_time = msg.parameters["round_time"]
            # self._password = msg.parameters["password"]
            # try:
                # self._battlefield = self.create_battlefield(length, ships_table)
            # except BattleshipError as e:
                # answer client the error
                # print("{}".format(e))
            # answer client OK

        # Sends the server a list of ship placements. The list MUST be ordered by ship type as specified in the instruction.
        if msg.type == ProtocolMessageType.PLACE:
            ship_positions = msg.parameters["ship_positions"]
            ship_id = 0
            if len(ship_positions.positions) == self._battlefield.count_ships():
                for ship_position in ship_positions.positions:
                    x_pos = ship_position.position.horizontal
                    y_pos = ship_position.position.vertical
                    orientation = ship_position.orientation
                    self.place_ship(ship_id, x_pos, y_pos, orientation)
                    ship_id += 1
                # if we reach this, the ships have all been successfully placed
                self.state = GameState.WAITING
            else:
                raise BattleshipError(ErrorCode.PARAMETER_WRONG_NUMBER_OF_SHIPS)

        # Moves a ship
        elif msg.type == ProtocolMessageType.MOVE:
            if not self.state == GameState.YOUR_TURN:
                raise BattleshipError(ErrorCode.ILLEGAL_STATE_NOT_YOUR_TURN)
            ship_id = msg.parameters["ship_id"]
            direction = msg.parameters["direction"]
            turn_counter = msg.parameters["turn_counter"]
            self.move(ship_id, direction)

        # Shoots the specified position of the opponents board.
        elif msg.type == ProtocolMessageType.SHOOT:
            if not self.state == GameState.OPPONENTS_TURN:
                raise BattleshipError(ErrorCode.ILLEGAL_STATE_NOT_YOUR_TURN)
            x_pos = msg.parameters["ship_position"].position.horizontal
            y_pos = msg.parameters["ship_position"].position.vertical
            turn_counter = msg.parameters["turn_counter"]
            if self.strike(x_pos, y_pos):
                # todo HIT
                return True
            else:
                # todo FAIL
                return False

        # This message tells the server that the client wants to abort the game. The user may communicate via the chat.
        elif msg.type == ProtocolMessageType.ABORT:
            turn_counter = msg.parameters["turn_counter"]
            self.abort()

        # SERVER -> CLIENTS
        # SERVER MESSAGES: STARTGAME, PLACED, YOUSTART, WAIT, HIT, FAIL, MOVED, TIMEOUT, ENDGAME

        # Initial message to start the game. The message MUST be sent to both clients
        elif msg.type == ProtocolMessageType.STARTGAME:
            self._state = GameState.PLACE_SHIPS
            length = msg.parameters["board_size"]
            ships_table = msg.parameters["num_ships"].numbers
            self._opponent_name = msg.parameters["opponent_name"]
            self._round_time = msg.parameters["round_time"]
            self._battlefield = self.create_battlefield(length, ships_table)

        # This message MUST be sent to the client who has the first turn. It is sent only once after the STARTGAME message.
        elif msg.type == ProtocolMessageType.YOUSTART:
            self._state = GameState.YOUR_TURN
            self.start_round_time()
            pass

        # This message MUST be sent to the client who hast to wait for the opponent's first turn. It is sent only once after the STARTGAME message
        elif msg.type == ProtocolMessageType.WAIT:
            self._state = GameState.OPPONENTS_TURN
            self.start_round_time()
            pass

        # This message is sent to both clients
        elif msg.type == ProtocolMessageType.HIT:
            self.start_round_time()
            sunk = msg.parameters["sunk"]
            position = msg.parameters["position"]
            self.increase_turn_counter()

        # The last shot was unsuccessful. This message is sent to both clients.
        elif msg.type == ProtocolMessageType.FAIL:
            if (self._state == GameState.YOUR_TURN):
                self._state = GameState.OPPONENTS_TURN
            else:
                self._state = GameState.YOUR_TURN

            self.start_round_time()
            position = msg.parameters["position"]
            self.increase_turn_counter()

        # A ship was moved. If the ship was moved to already shot fields, these fields are mentioned in the positions. This message is sent to both clients.
        elif msg.type == ProtocolMessageType.MOVED:
            if (self._state == GameState.YOUR_TURN):
                self._state = GameState.OPPONENTS_TURN
            else:
                self._state = GameState.YOUR_TURN

            self.start_round_time()
            self.increase_turn_counter()

        # The current turn ended because of a timeout. This message is sent to both clients.
        elif msg.type == ProtocolMessageType.TIMEOUT:
            if (self._state == GameState.YOUR_TURN):
                self._state = GameState.OPPONENTS_TURN
            else:
                self._state = GameState.YOUR_TURN

            self.start_round_time()
            self.increase_turn_counter()

        # The opponent placed ships
        elif msg.type == ProtocolMessageType.PLACED:
            pass

        # The current game ended because of a known reason. This message is sent to both clients
        elif msg.type == ProtocolMessageType.ENDGAME:
            self._state = GameState.GAME_ENDED
            self.start_round_time()
            reason = msg.parameters["reason"]
            self.abort()

        # unknown command
        else:
            raise BattleshipError(ErrorCode.UNKNOWN)

    def start_timeout(self, callback: Callable):
        self._timeout_handle = self.loop.call_later(self.round_time, callback, self.client)

    def restart_timeout(self, callback: Callable):
        self.cancel_timeout()
        self.start_timeout(callback)

    def cancel_timeout(self):
        if self._timeout_handle is not None:
            self._timeout_handle.cancel()

    def to_create_game_msg(self):
        params = {"board_size": self.length, "num_ships": NumShips(self.ships), "round_time": self.round_time, "options": self.options}
        if self.options == GameOptions.PASSWORD:
            params["password"] = self.password
        msg = ProtocolMessage.create_single(ProtocolMessageType.CREATE_GAME, params)
        print("{}".format(msg))
        return msg

    def to_game_msg(self):
        params = {"game_id": self.game_id, "username": self.username, "board_size": self.length, "num_ships": NumShips(self.ships), "round_time": self.round_time, "options": self.options}
        return ProtocolMessage.create_single(ProtocolMessageType.GAME, params)

    def to_start_game_msg(self):
        params = {"opponent_name": self.opponent_name, "board_size": self.length, "num_ships": NumShips(self.ships), "round_time": self.round_time}
        return ProtocolMessage.create_single(ProtocolMessageType.STARTGAME, params)

    def get_place_msg(self):
        ship_positions = []
        for ship in self._battlefield._ships:
            ship_positions.append(ship.get_ship_position())
        return ProtocolMessage.create_single(ProtocolMessageType.PLACE, {"ship_positions": ShipPositions(ship_positions)})
