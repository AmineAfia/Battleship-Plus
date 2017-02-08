from common.constants import GameOptions

class GameLobbyData:
    def __init__(self, game_id, username="", board_size=0, num_ships=[], round_time=0, options=0):
        self._game_id = game_id
        self._round_time = round_time
        self._options = options
        self._username = username
        self._board_size = board_size
        self._num_ships = num_ships

    def __str__(self):
        return "#{} from '{}', size {}, {}s, ships {}, {}".format(self._game_id, self._username, self._board_size, self._round_time, self._num_ships, "passwd" if self._options == GameOptions.PASSWORD else "")
