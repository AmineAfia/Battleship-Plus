""" This File implement the a game session (Battlefields, win, lose) """
from operator import itemgetter
from itertools import cycle
from pyfiglet import Figlet


class Player(object):

    """Player object with some actions (just move for now)."""

    def __init__(self):
        """Initialize coordinates."""
        # self.x = 5
        # self.y = 4

        self.positions = [(5,4), (2,2), (1,1), (10,10)]
        self.sortedPositions = sorted(self.positions, key=itemgetter(1), reverse=True)

    def shoot(self, shootX, shootY):
        # self.x = shootX
        # self.y = shootY
        self.sortedPositions.append((shootX,shootY))
        self.sortedPositions = sorted(self.sortedPositions, key=itemgetter(1), reverse=True)



class GameMap(object):

    """GameMap that shows where the player is."""

    """This will the field size"""
    X_OFFSET = 10
    Y_OFFSET = 10

    def render(self, player):
        """Render map and player position."""
        def render_empty_row():
            """Render row in which there is no player."""
            print(' . ' * (self.X_OFFSET))

        # # ASCII Art
        # f = Figlet(font='big')
        # print(f.renderText('Battleship+'))

        for _ in range(self.Y_OFFSET - player.sortedPositions[0][1]):
            render_empty_row()

        for i in range(len(player.sortedPositions)):
            element = player.sortedPositions[i]

            if i < (len(player.sortedPositions) - 1):
                nextElement = player.sortedPositions[i+1]
            else:
                nextElement = (0,0)

            if element[1] == nextElement[1]:
                print('{} X {} X {}'
                      .format(' . ' * (element[0] - 1),
                              ' . ' * (nextElement[0] - element[0] - 1),
                              ' . ' * int((self.X_OFFSET - nextElement[0]))))
            elif element[1] != nextElement[1]:
                print('{} X {}'
                      .format(' . ' * (element[0] - 1),
                              ' . ' * int((self.X_OFFSET - element[0]))))

            for _ in range(element[1] - nextElement[1] - 1):
                render_empty_row()

        # for _ in range(y - 1):
        #     render_empty_row()


class Command(object):

    """Command reader from stdin."""

    # Map text command to player movement
    CMD_TO_MOVE = {
        'u': (0, -1),
        'up': (0, -1),
        'd': (0, 1),
        'down': (0, 1),
        'l': (-1, 0),
        'left': (-1, 0),
        'r': (1, 0),
        'right': (1, 0),
    }

    CMD_TO_SHOOT = {}

    # Default value for unknown command
    NO_MOVE = (0, 0)

    def read(self):
        """Read command (up, down, left, right) from stdin.

        The command is converted to a movement for the player using the same
        coordinate system.

        :returns: Player movement
        :rtype: tuple(int, int)

        """
        command_str = input('position > ')
        return self.CMD_TO_MOVE.get(command_str, self.NO_MOVE)

    def readShoot(self):
        command_x = int(input('x position >'))
        command_y = int(input('y position >'))

        return (command_x, command_y)


class Game(object):

    """Game object to keep state and read command for next turn."""

    def __init__(self):
        """Get all the objects needed to run the game."""
        self.player = Player()
        self.game_map = GameMap()
        self.command = Command()

    def run(self):
        """Render map and read next command from stdin."""
        while True:
            self.game_map.render(self.player)
            self.player.shoot(*self.command.readShoot())

if __name__ == "__main__":
    game = Game()
    game.run()
