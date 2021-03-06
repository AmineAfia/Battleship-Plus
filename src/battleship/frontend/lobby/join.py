""" This module include all functionalities to join a game """
import urwid
import logging
import asyncio

from .waitting import Waiting
from common.GameController import GameController
from common.constants import Orientation
from client.lobby import ClientLobbyController
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode
from common.protocol import ProtocolMessageType
from ..common.StaticScreens import Screen


# Common variables to place ships
class ShipsList:
    """ A static class that holds the shares variables between the module classes """
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
    info_pile_2 = []
    # pile to be shown in the popup for placing ships
    info_pile_3 = None
    ships_info_length_list = []
    # button show in the ships placing popup
    ships_categories_place = []
    # Dictionary to get chips length
    length_dictionary = {"carrier": 5, "battleship": 5, "cruiser":  4, "destroyer":  3, "submarine": 2}
    buttons_list = {}
    list_of_placed_cells = []

    # buttons in the popup dailog, they need to be refreshed when we use asyncio to switche the screens
    orientation_buttons = urwid.Pile([])

    placement_notification = urwid.Pile([urwid.Text("")])

    @staticmethod
    def get_ships():
        i = 0
        ShipsList.ships_info_length_list.clear()
        ShipsList.ships_categories_place.clear()
        for k, v in ShipsList.length_dictionary.items():
            ShipsList.ships_info_length_list.append(urwid.Button(("You have {} {} with length {}".format(ShipsList.ships[i], k, v))))
            # ShipsList.ships_categories_place.append(urwid.RadioButton(ShipsList.bgroup, k))
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
    """Popup for each cell in the matrix. it contains button to place the ships"""
    signals = ['close']

    def __init__(self, button_with_pop_up, x_pos, y_pos):
        # self.game_controller = game_controller
        self.button_with_pop_up = button_with_pop_up
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.east_button = urwid.Button("East")
        self.north_button = urwid.Button("North")
        self.self_exit_button = urwid.Button("Exit")

        # connect direction buttons to set the orientation
        urwid.connect_signal(self.self_exit_button, 'click',
                             lambda button: self._emit("close"))

        urwid.connect_signal(self.east_button, 'click',
                             lambda button: self.set_ship_position(Orientation.EAST))

        urwid.connect_signal(self.north_button, 'click',
                             lambda button: self.set_ship_position(Orientation.NORTH))
        
        orientation_pile = urwid.LineBox(urwid.Pile([self.self_exit_button, urwid.Columns([self.east_button, self.north_button], 2)]), 'Direction')
        # TODO: change buttons to radio buttons
        ships_pile = urwid.LineBox(ShipsList.info_pile_3, 'Ships')

        for ship_type_button in ShipsList.ships_categories_place:
            # urwid.connect_signal(ship_type_button, 'change', lambda ship, foo: self.set_ship_type_to_place(ship.get_label(), foo))
            urwid.connect_signal(ship_type_button, 'click', lambda ship: self.set_ship_type_to_place(ship.get_label()))

        pile = urwid.Pile([ships_pile, orientation_pile])
        fill = urwid.Filler(pile)
        super().__init__(urwid.AttrWrap(fill, 'popbg'))

    def set_ship_type_to_place(self, ship_type_button):
        logging.debug("{}".format(ship_type_button))
        ShipsList.ship_type = ship_type_button
        ShipsList.ship_length = ShipsList.length_dictionary[ship_type_button]

    def set_ship_position(self, orientation):
        try:
            ShipsList.ship_orientation = orientation
            ShipsList.ship_id = self.button_with_pop_up.game_controller.get_next_ship_id_by_type_to_place(ShipsList.ship_type)
            ShipsList.ship_x_pos = self.x_pos
            ShipsList.ship_y_pos = self.y_pos
            # switched x an y to follow the RFC
            self.button_with_pop_up.game_controller.place_ship(ShipsList.ship_id, ShipsList.ship_x_pos, ShipsList.ship_y_pos, orientation)
            self.button_with_pop_up.place_ship_in_position(orientation, ShipsList.ship_length, ShipsList.ship_type)
        except Exception as e:
            ShipsList.placement_notification.contents.clear()
            ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "You have no more ships to place or your ships are overlaping/touching")), ShipsList.placement_notification.options()))
            logging.debug(str(e))

        for ship_type_button in ShipsList.ships_categories_place:
            # urwid.connect_signal(ship_type_button, 'change', lambda ship, foo: self.set_ship_type_to_place(ship.get_label(), foo))
            urwid.connect_signal(ship_type_button, 'click', lambda ship: self.set_ship_type_to_place(ship.get_label()))

        ShipsList.ships = self.button_with_pop_up.game_controller.ships
        ShipsList.get_remaining_ships()
        self._emit("close")


class ButtonWithAPopUp(urwid.PopUpLauncher):
    """ a popup launcher that represent cells in the field """
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


class Join:
    """ Main class to join a game. it renders the join screen, send PLACE message and handles the STARTGAME, ENDGAME and PLACED messages """
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller

        # get ships from controller
        ShipsList.ships = game_controller.ships
        self.field_offset = game_controller.length
        ShipsList.get_ships()
        
        ShipsList.placement_notification.contents.clear()

        # in this case the STARTGAME is not handled by the Waiting screen
        if self.lobby_controller.is_joining_game:
            self.lobby_controller.set_callback(ProtocolMessageType.STARTGAME, self.handle_start_game)
        self.lobby_controller.set_callback(ProtocolMessageType.ENDGAME, self.handle_canceled_game)
        self.lobby_controller.set_callback(ProtocolMessageType.PLACED, self.handle_placed)

        self.screen_finished: asyncio.Event = asyncio.Event()

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
            ('popbg', 'white', 'dark gray'),
            ('turn', 'dark blue', 'black'),
            ('notturn', 'dark red', 'black'),
        ]
        self.blank = urwid.Divider()

    def handle_start_game(self):
        # nothing to do here, we just need a callback
        pass

    def handle_placed(self):
        ShipsList.placement_notification.contents.clear()
        ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "Opponent placed his ships")), ShipsList.placement_notification.options()))

    def handle_canceled_game(self, foo):
        try:
            the_screen = Screen("OPPONENT LEFT").show()
            del the_screen
            self.lobby_controller.received_cancel = True
            self.screen_finished.set()
        except Exception as e:
            logging.debug(e)

    def forward_next(self, foo):
        place_task = self.loop.create_task(self.lobby_controller.send_place())
        place_task.add_done_callback(self.place_result)

    def place_result(self, future):
        # check if there is an error message to display
        e = future.exception()
        if type(e) is BattleshipError:
            if e.error_code == ErrorCode.SYNTAX_INVALID_PARAMETER:
                ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "orientation parameter has invalid value")), ShipsList.placement_notification.options()))
                logging.warning("orientation parameter has invalid value")
            elif e.error_code == ErrorCode.PARAMETER_POSITION_OUT_OF_BOUNDS:
                ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "position out of bounds")), ShipsList.placement_notification.options()))
                logging.warning("position out of bounds")
            elif e.error_code == ErrorCode.PARAMETER_OVERLAPPING_SHIPS:
                ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "overlapping ships")), ShipsList.placement_notification.options()))
                logging.warning("overlapping ships")
            elif e.error_code == ErrorCode.PARAMETER_WRONG_NUMBER_OF_SHIPS:
                ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "wrong number of ships")), ShipsList.placement_notification.options()))
                logging.warning("wrong number of ships")
            else:
                ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "other battleship error")), ShipsList.placement_notification.options()))
                logging.warning("other battleship error")
        elif e is not None:
            if type(e) is ConnectionRefusedError:
                ShipsList.placement_notification.contents.append((urwid.Text(('notturn', "Server not reachable")), ShipsList.placement_notification.options()))
                logging.error("Server not reachable")
            else:
                raise e
        # the ships are placed, we know this only when a WAIT or YOUSTART arrives
        else:
            # ok, we are ready
            self.lobby_controller.received_cancel = False
            self.game_controller.start_game()
            raise urwid.ExitMainLoop()
        ShipsList.placement_notification.contents.clear()

    def unhandled(self, key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def dummy_function_for_cancel(self, foo):
        self.lobby_controller.is_cancelling_game = True
        raise urwid.ExitMainLoop()

    def cancel_game(self, foo):
        login_task = self.loop.create_task(self.lobby_controller.send_abort())
        login_task.add_done_callback(self.dummy_function_for_cancel)

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

        cancel_button = urwid.Button("Cancel", on_press=self.cancel_game)
        forward_button = urwid.Button('Next', on_press=self.forward_next)
        ship_pile = urwid.Pile(ship_f)

        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Ship positioning"), left=2, right=0, min_width=20),
                ShipsList.placement_notification,
            ], 2),
            self.blank,

            urwid.Columns([
                ship_pile,
                urwid.LineBox(ShipsList.info_pile_2, 'Ships')
            ], 2),
            self.blank,
            urwid.Columns([
                forward_button,
                cancel_button
            ], 2),
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

        self.loop.create_task(self.end_screen())
        loop = urwid.MainLoop(frame, self.palette,
                              unhandled_input=self.unhandled, pop_ups=True,
                              event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()

    async def end_screen(self):
        await self.screen_finished.wait()
        ShipsList.info_pile_2.contents.clear()
        ShipsList.placement_notification.contents.clear()
        self.lobby_controller.clear_callback(ProtocolMessageType.ENDGAME)
        self.lobby_controller.clear_callback(ProtocolMessageType.PLACED)
        raise urwid.ExitMainLoop()
