import urwid

from .waitting import Waiting
from common.GameController import GameController
from common.constants import Orientation
from client.lobby import ClientLobbyController
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode


# common variables to place ships
class ShipsList:
    # parameters to place a ship
    ship_id = None
    ship_type = None
    ship_length = None
    ship_orientation = None
    ship_x_pos = None
    ship_y_pos = None

    # Variables for UI
    ships_list = []
    ships = [0, 0, 0, 0, 0]
    info_pile = None
    # pile of ships typs with how much we have (shown in Available Ships)
    info_pile_2 = None
    # pile to be shown in the popup for placing ships
    info_pile_3 = None
    ships_info_length_list = []
    # button show in the ships placing popup
    ships_categories_place = []
    # Dictionary to get chips length
    length_dictionary = {"carrier": 5, "battleship": 5, "cruiser":  4, "destroyer":  3, "submarine": 2}
    buttons_list = {}
    list_of_placed_cells = []

    @staticmethod
    def get_ships():
        # ShipsList.ships_list.append(urwid.Button(("carrier {}".format(ShipsList.ships[0]))))
        # ShipsList.ships_list.append(urwid.Button(('battleship {}'.format(ShipsList.ships[1]))))
        # ShipsList.ships_list.append(urwid.Button(('cruiser {}'.format(ShipsList.ships[2]))))
        # ShipsList.ships_list.append(urwid.Button(('destroyer {}'.format(ShipsList.ships[3]))))
        # ShipsList.ships_list.append(urwid.Button(('submarine {}'.format(ShipsList.ships[4]))))
        # ShipsList.info_pile = urwid.Pile(ShipsList.ships_list)
        i = 0

        for k, v in ShipsList.length_dictionary.items():
            ShipsList.ships_info_length_list.append(urwid.Button(("You have {} {} with length {}".format(ShipsList.ships[i], k, v))))
            ShipsList.ships_categories_place.append(urwid.Button(k))
            i += 1

        ShipsList.info_pile_2 = urwid.Pile(ShipsList.ships_info_length_list)
        ShipsList.info_pile_3 = urwid.Pile(ShipsList.ships_categories_place)

    @staticmethod
    def get_remaining_ships():
        ShipsList.ships_info_length_list.clear()
        ShipsList.info_pile_2.contents.clear()
        i = 0
        for k, v in ShipsList.length_dictionary.items():
            ShipsList.ships_info_length_list.append(urwid.Button(("You have {} {} with length {}".format(ShipsList.ships[i], k, v))))
            i += 1

        ShipsList.info_pile_2.contents.append((urwid.Pile(ShipsList.ships_info_length_list),ShipsList.info_pile_2.options()))


class PopUpDialog(urwid.WidgetWrap):
    """Popup for each cell in the matrix """
    signals = ['close']

    def __init__(self, button_with_pop_up, x_pos, y_pos):
        # self.game_controller = game_controller
        self.button_with_pop_up = button_with_pop_up
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.h_button = urwid.Button("East")
        self.v_button = urwid.Button("North")
        self.self_exit_button = urwid.Button("Exit")

        # connect direction buttons to set the orientation
        urwid.connect_signal(self.self_exit_button, 'click',
                             lambda button: self._emit("close"))

        urwid.connect_signal(self.h_button, 'click',
                             lambda button: self.set_ship_position(Orientation.EAST))

        urwid.connect_signal(self.v_button, 'click',
                             lambda button: self.set_ship_position(Orientation.NORTH))

        orientation_pile = urwid.LineBox(urwid.Pile([self.self_exit_button, urwid.Columns([self.h_button, self.v_button], 2)]), 'Direction')
        # TODO: change buttons to radio buttons
        ships_pile = urwid.LineBox(ShipsList.info_pile_3, 'Ships')

        for ship_type_button in ShipsList.ships_categories_place:
            urwid.connect_signal(ship_type_button, 'click', lambda ship: self.set_ship_type_to_place(ship.get_label()))

        pile = urwid.Pile([ships_pile, orientation_pile])
        fill = urwid.Filler(pile)
        super().__init__(urwid.AttrWrap(fill, 'popbg'))

    @staticmethod
    def set_ship_type_to_place(ship_type_button):
        ShipsList.ship_type = ship_type_button
        ShipsList.ship_length = ShipsList.length_dictionary[ship_type_button]

    def set_ship_position(self, orientation):
        ShipsList.ship_orientation = orientation
        ShipsList.ship_id = self.button_with_pop_up.game_controller.get_next_ship_id_by_type_to_place(ShipsList.ship_type)
        ShipsList.ship_x_pos = self.x_pos
        ShipsList.ship_y_pos = self.y_pos
        self.button_with_pop_up.place_ship_in_position(orientation, ShipsList.ship_length, ShipsList.ship_type)
        self.button_with_pop_up.game_controller.place_ship(ShipsList.ship_id, ShipsList.ship_x_pos, ShipsList.ship_y_pos, orientation)

        for ship_type_button in ShipsList.ships_categories_place:
            urwid.connect_signal(ship_type_button, 'click', lambda ship: self.set_ship_type_to_place(ship.get_label()))

        ShipsList.ships = self.button_with_pop_up.game_controller.ships
        ShipsList.get_remaining_ships()
        self._emit("close")


# structuring one cell
class ButtonWithAPopUp(urwid.PopUpLauncher):
    def __init__(self, x_pos, y_pos, game_controller):
        self.game_controller = game_controller
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.b = urwid.Button("_")
        super().__init__(self.b)
        urwid.connect_signal(self.original_widget, 'click',
                             lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog(self, self.x_pos, self.y_pos)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def place_ship_in_position(self, orientation, length, ship_type):
        # self.b.set_label("X")
        for i in range(length):
                if orientation == Orientation.NORTH:
                    ShipsList.buttons_list[(self.x_pos, self.y_pos + i)].b.set_label("X")
                    # fake list of Xs coordinations to forward to join
                    ShipsList.list_of_placed_cells.append((self.x_pos, self.y_pos + i))
                elif orientation == Orientation.EAST:
                    ShipsList.buttons_list[(self.x_pos + i, self.y_pos)].b.set_label("X")
                    # fake list of Xs coordinations to forward to join
                    ShipsList.list_of_placed_cells.append((self.x_pos + i, self.y_pos))

        if ship_type == "carrier":
            for i in range(length):
                    if orientation == Orientation.NORTH:
                        ShipsList.buttons_list[(self.x_pos+1, self.y_pos + i)].b.set_label("X")
                        # fake list of Xs coordinations to forward to join
                        ShipsList.list_of_placed_cells.append((self.x_pos+1, self.y_pos + i))
                    elif orientation == Orientation.EAST:
                        ShipsList.buttons_list[(self.x_pos + i, self.y_pos + 1)].b.set_label("X")
                        # fake list of Xs coordinations to forward to join
                        ShipsList.list_of_placed_cells.append((self.x_pos + i, self.y_pos + 1))

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 8}


# Main class to place ships
class Join:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller

        # get ships from controller
        ShipsList.ships = game_controller.ships
        self.field_offset = game_controller.length
        ShipsList.get_ships()

        self.palette = [
            ('hit', 'black', 'light gray', 'bold'),
            ('miss', 'black', 'black', ''),
            ('untouched', 'white', 'black', ''),
            ('body', 'white', 'black', 'standout'),
            ('reverse', 'light gray', 'black'),
            ('header', 'white', 'dark red', 'bold'),
            ('important', 'dark blue', 'light gray', ('standout', 'underline')),
            ('editfc', 'white', 'dark blue', 'bold'),
            ('editbx', 'light gray', 'dark blue'),
            ('editcp', 'black', 'light gray', 'standout'),
            ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
            ('buttn', 'white', 'black'),
            ('buttnf', 'white', 'dark blue', 'bold'),
            ('popbg', 'white', 'dark gray')
        ]
        self.blank = urwid.Divider()

    def forward_next(self, foo):
        # TODO: somehow tell the main client the difference between this and unhandled
        # Why should the client know about unhandlded? it is just for testing purposes, to exit the game at this time
        # It can be used as and exit for players as well but needs a warning + communication termination for an appropriate exit

        # TODO: check if all ships are placed to start the game and go to the next screen
        place_task = self.loop.create_task(self.lobby_controller.send_place())
        place_task.add_done_callback(self.place_result)

    def place_result(self, future):
        # check if there is an error message to display
        e = future.exception()
        if type(e) is BattleshipError:
            if e.error_code == ErrorCode.SYNTAX_INVALID_PARAMETER:
                # TODO: popup
                print("orientation parameter has invalid value")
            elif e.error_code == ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS:
                # TODO: popup
                print("position out of bounds")
            elif e.error_code == ErrorCode.PARAMETER_OVERLAPPING_SHIPS:
                print("overlapping ships")
            elif e.error_code == ErrorCode.PARAMETER_WRONG_NUMBER_OF_SHIPS:
                print("wrong number of ships")
            else:
                print("other battleship error")
        elif e is not None:
            if type(e) is ConnectionRefusedError:
                print("Server not reachable")
            else:
                raise e
        # the ships are placed, we know this only when a WAIT or YOUSTART arrives
        # TODO.
        else:
            # ok, we are ready
            self.game_controller.start_game()
            raise urwid.ExitMainLoop()

    def unhandled(self, key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def join_main(self):
        # Constructing ships field
        ship_button_list = []
        ship_f = []
        for y_pos in range(self.field_offset):
            for x_pos in range(self.field_offset):
                ship_cell = ButtonWithAPopUp(x_pos, y_pos, self.game_controller)
                ship_button_list.append(ship_cell)
                ShipsList.buttons_list[(x_pos, y_pos)] = ship_cell
            ship_zeil = urwid.GridFlow(ship_button_list, 1, 1, 0, 'center')
            ship_f.append(ship_zeil)
            ship_button_list.clear()

        forward_button = urwid.Button('Next', on_press=self.forward_next)
        ship_pile = urwid.Pile(ship_f)

        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Ship positioning"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("")]),
            ], 2),
            self.blank,

            urwid.Columns([
                ship_pile,
                urwid.LineBox(ShipsList.info_pile_2, 'Ships')
            ], 2),
            self.blank,
            forward_button,
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

        loop = urwid.MainLoop(frame, self.palette,
                              unhandled_input=self.unhandled, pop_ups=True,
                              event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()
