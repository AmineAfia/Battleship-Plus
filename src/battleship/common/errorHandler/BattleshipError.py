from ..constants import ErrorCode

class BattleshipError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code

    def __str__(self):
        return repr(self.error_code)

