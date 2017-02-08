# ships: carrier, battleship, cruiser, destroyer, submarine
import urwid

from .waitting import Waiting
from common.GameController import GameController
from common.constants import Orientation
from client.lobby import ClientLobbyController


class ShipsList:
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
    length_dictionary = {"carrier": 5, "battleship": 5, "cruiser":  4, "destroyer":  3, "submarine": 2}
    buttons_list = {}

    @staticmethod
    def get_ships():
        ShipsList.ships_list.append(urwid.Button(("carrier {}".format(ShipsList.ships[0]))))
        ShipsList.ships_list.append(urwid.Button(('battleship {}'.format(ShipsList.ships[1]))))
        ShipsList.ships_list.append(urwid.Button(('cruiser {}'.format(ShipsList.ships[2]))))
        ShipsList.ships_list.append(urwid.Button(('destroyer {}'.format(ShipsList.ships[3]))))
        ShipsList.ships_list.append(urwid.Button(('submarine {}'.format(ShipsList.ships[4]))))
        ShipsList.info_pile = urwid.Pile(ShipsList.ships_list)
        i = 0
        for k, v in ShipsList.length_dictionary.items():
            ShipsList.ships_info_length_list.append(urwid.Button(("You have {} {} with length {}".format(ShipsList.ships[i], k, v))))
            ShipsList.ships_categories_place.append(urwid.Button(k))
            i += 1

        ShipsList.info_pile_2 = urwid.Pile(ShipsList.ships_info_length_list)
        ShipsList.info_pile_3 = urwid.Pile(ShipsList.ships_categories_place)


class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with North, South, West and East buttons """
    signals = ['close']

    def __init__(self, button_with_pop_up, x_pos, y_pos):
        # self.game_controller = game_controller
        self.button_with_pop_up = button_with_pop_up
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.h_button = urwid.Button("Horizontal")
        self.v_button = urwid.Button("Vertical")
        self.self_exit_button = urwid.Button("Exit")

        urwid.connect_signal(self.self_exit_button, 'click',
                             lambda button: self._emit("close"))

        urwid.connect_signal(self.h_button, 'click',
                             lambda button: self.set_orientation(Orientation.EAST, 3))

        urwid.connect_signal(self.v_button, 'click',
                             lambda button: self.set_orientation(Orientation.NORTH, 3))

        # function to shoot the opponents field
        # def place(self):
        #     self.set_label('X')

        orientation_pile = urwid.LineBox(urwid.Pile([self.self_exit_button, urwid.Columns([self.h_button, self.v_button], 2)]), 'Direction')
        ships_pile = urwid.LineBox(ShipsList.info_pile_3, 'Ships')
        pile = urwid.Pile([ships_pile, orientation_pile])
        fill = urwid.Filler(pile)
        super().__init__(urwid.AttrWrap(fill, 'popbg'))

    def set_orientation(self, orientation, length):
        self.button_with_pop_up.place_ship_in_position(orientation, length)
        self.button_with_pop_up.game_controller.place_ship(4, self.x_pos, self.y_pos, orientation)
        print(orientation)
        self._emit("close")


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

    def place_ship_in_position(self, orientation, length):
        # self.b.set_label("X")
        for i in range(length):
                if orientation == Orientation.NORTH:
                    ShipsList.buttons_list[(self.x_pos, self.y_pos + i)].b.set_label("X")
                elif orientation == Orientation.EAST:
                    ShipsList.buttons_list[(self.x_pos + i, self.y_pos)].b.set_label("X")
                # else:
                    # ShipsList.buttons_list[(self.x_pos, self.y_pos)].b.set_label("X")
    # def get_pop_up_coordinations(self):
    #     return self.x, self.y

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 8}


class Join:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
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
                urwid.LineBox(ShipsList.info_pile_2, 'Available Ships')
            ], 2),
            self.blank,
            forward_button,
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

        urwid.MainLoop(frame, self.palette,
                       unhandled_input=self.unhandled, pop_ups=True,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()

if '__main__' == __name__:
    battle = Join()
    battle.join_main()
