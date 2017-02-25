import logging
from common.constants import GameOptions, ErrorCode
from common.errorHandler.BattleshipError import BattleshipError
from common.states import GameState

class GameLobbyData:
    def __init__(self, game_id, username="", board_size=0, num_ships=[], round_time=0, options=0):
        self._game_id = game_id
        self._round_time = round_time
        self._options = options
        self._username = username
        self._board_size = board_size
        self._num_ships = num_ships
        self._state = GameState.IN_LOBBY
        # TODO: merge some of this with GameController

    def reset_for_client(self):
        self._state = GameState.IN_LOBBY

    def __str__(self):
        return "#{} from '{}', size {}, {}s, ships {}, {}".format(self._game_id, self._username, self._board_size, self._round_time, self._num_ships, "passwd" if self._options == GameOptions.PASSWORD else "")

    def params_as_list(self):
        password = 0
        if self.options != 0:
            password = 1

        return [self._game_id, self._board_size, self._num_ships.numbers, password]

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        # TODO: check if it's a valid state
        self._state = state

    @property
    def game_id(self):
        return self._game_id

    @game_id.setter
    def game_id(self, game_id):
        self._game_id = game_id

    @property
    def board_size(self):
        return self._board_size

    @board_size.setter
    def board_size(self, board_size):
        if board_size not in range(10, 27):
            raise BattleshipError(ErrorCode.SYNTAX_INVALID_BOARD_SIZE)
        else:
            self._board_size = board_size

    # TODO property and setter for num_ships

    @property
    def round_time(self):
        return self._round_time

    @property
    def num_ships(self):
        return self._num_ships

    @round_time.setter
    def round_time(self, round_time):
        if round_time not in range(25, 65, 5):
            raise BattleshipError(ErrorCode.SYNTAX_INVALID_PARAMETER)
        else:
            self._round_time = round_time

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        if options not in [0, GameOptions.PASSWORD]:
            raise BattleshipError(ErrorCode.PARAMETER_OPTION_NOT_SUPPORTED)
        else:
            self._options = options
