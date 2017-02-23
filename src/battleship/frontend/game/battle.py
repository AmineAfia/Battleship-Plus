import urwid
import urwid.raw_display
import urwid.web_display
import threading
import time
import functools

from ..common.StaticScreens import Screen
from ..common.Chat import Chat
from .result import Result
from common.GameController import GameController
from common.constants import Orientation, EndGameReason, Direction
from common.protocol import ProtocolMessageType, Position
from common.states import GameState
from common.errorHandler.BattleshipError import BattleshipError


class ShipsList:
    # list of ships from each type
    ships = [0, 0, 0, 0, 0]
    # Dictionary to get chips length
    length_dictionary = {"carrier": 5, "battleship": 5, "cruiser":  4, "destroyer":  3, "submarine": 2}

    # List of buttons to be loaded in the pile
    ships_info_length_list = []
    # pile of ships typs with how much we have (shown in Available Ships)
    info_pile_2 = None

    # distionary with all cells and positions
    ship_buttons_dic = {}

    # Variables for UI
    ships_list = []
    info_pile = None
    # pile to be shown in the popup for placing ships
    info_pile_3 = None
    # button show in the ships placing popup
    ships_categories_place = []
    buttons_list = {}
    list_of_placed_cells = []
    # Dictionary with all buttons that can move ships
    movement_popups_dic = {}

    # Dictionary of shhoting feld matrix
    shoot_matrix__buttons_dic = {}

    # For testing perposes
    all_ships_coordinates = []
    test_refs = urwid.Button("")
    test_refs_pile = urwid.Pile([test_refs])

    # variable to allow players to shoot and move fro the UI
    your_turn = 0

    @staticmethod
    def get_ships():
        ShipsList.ships_info_length_list.append(urwid.Button(("{}".format(ShipsList.ships))))




class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with North, South, West and East buttons """
    signals = ['close']

    def __init__(self, button_with_pop_up, x_pos, y_pos, game_controller, lobby_controller, loop):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.button_with_pop_up = button_with_pop_up
        self.n_button = urwid.Button("North")
        self.s_button = urwid.Button("South")
        self.w_button = urwid.Button("West")
        self.e_button = urwid.Button("East")
        self.exit_button = urwid.Button("Exit")
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.loop = loop

        urwid.connect_signal(self.exit_button, 'click',
                             lambda button: self._emit("close"))

        urwid.connect_signal(self.n_button, 'click',
                             lambda button: self.move_ship(Direction.NORTH))

        urwid.connect_signal(self.s_button, 'click',
                             lambda button: self.move_ship(Direction.SOUTH))

        urwid.connect_signal(self.e_button, 'click',
                             lambda button: self.move_ship(Direction.EAST))

        urwid.connect_signal(self.w_button, 'click',
                             lambda button: self.move_ship(Direction.WEST))

        self.coordinates = urwid.Text("({}, {})".format(self.x_pos, self.y_pos))

        pile = urwid.Pile([self.coordinates, self.exit_button, self.n_button, urwid.Columns([self.w_button, self.e_button], 2), self.s_button])
        fill = urwid.Filler(pile)
        super().__init__(urwid.AttrWrap(fill, 'popbg'))

    def move_ship(self, direction):
        if ShipsList.your_turn == 1:
            self.ship_id = self.game_controller.get_ship_id_from_location(self.x_pos, self.y_pos)
            self.ship_type = self.game_controller.get_ship_type_by_id(self.ship_id)
            self.ship_orientation = self.game_controller.get_ship_orientation_by_id(self.ship_id)
            self.ship_length = ShipsList.length_dictionary[self.ship_type]

            try:
                self.game_controller.move(self.ship_id, direction)

                # For testing purposes
                ShipsList.test_refs = urwid.Button(str("UI: ({}, {}) cont: {}".format(self.x_pos, self.y_pos, self.game_controller.get_all_ships_coordinates())))
                ShipsList.test_refs_pile.contents.append((ShipsList.test_refs, ShipsList.test_refs_pile.options()))

                self._emit("close")

                self.button_with_pop_up.move_ship_in_position(self.ship_orientation, self.ship_length, self.ship_type, direction)
                move_task = self.loop.create_task(self.lobby_controller.send_move(self.ship_id, direction))
                move_task.add_done_callback(self.passing_callback)
            except Exception as e:
                # TODO show a clear message of the failed shoot
                #print("shoot sagt: {}".format(type(e)))
                print("moving: {}".format(e))
                self._emit("close")
        else:
            self._emit("close")

    def passing_callback(self, foo):
        self._emit("close")


class ButtonWithAPopUp(urwid.PopUpLauncher):
    def __init__(self, x_pos, y_pos, game_controller, lobby_controller, loop):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.loop = loop
        #self.cell = urwid.Button("({}, {})".format(self.x_pos, y_pos))
        self.cell = urwid.Button("_")
        ShipsList.movement_popups_dic[(self.x_pos, self.y_pos)] = self.cell
        super().__init__(self.cell)
        self.x_pos_move = 0
        self.y_pos_move = 0

        # if (x_pos, y_pos) in self.game_controller.get_all_ships_coordinates():
        urwid.connect_signal(ShipsList.movement_popups_dic[self.x_pos + self.x_pos_move, self.y_pos + self.y_pos_move], 'click',
                             lambda button: self.open_pop_up())

    # def connect_reference(self):
    #     urwid.connect_signal(ShipsList.movement_popups_dic[self.x_pos + self.x_pos_move, self.y_pos + self.y_pos_move], 'click',
    #                          lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog(self, self.x_pos, self.y_pos, self.game_controller, self.lobby_controller, self.loop)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}

    def move_ship_in_position(self, orientation, length, ship_type, direction):

        if direction == Direction.EAST:
            self.x_pos_move = 1
            self.y_pos_move = 0
        elif direction == Direction.NORTH:
            self.x_pos_move = 0
            self.y_pos_move = -1
        elif direction == Direction.WEST:
            self.x_pos_move = -1
            self.y_pos_move = 0
        elif direction == Direction.SOUTH:
            self.x_pos_move = 0
            self.y_pos_move = 1

        # new_coordinates = self.game_controller.get_ship_coordinates_by_id(self.game_controller.get_ship_id_from_location(self.x_pos, self.y_pos))
        #
        # for cord in new_coordinates:
        #     if orientation == Orientation.NORTH:
        #         ShipsList.ship_buttons_dic[cord].cell.set_label("@")
        #     elif orientation == Orientation.EAST:
        #         ShipsList.ship_buttons_dic[cord].cell.set_label("@")
        #

        for i in range(length):
                if orientation == Orientation.NORTH:
                    # take ship out of matrix
                    ShipsList.ship_buttons_dic[(self.x_pos, self.y_pos + i)].cell.set_label("_")
                    # draw new ship
                    ShipsList.ship_buttons_dic[(self.x_pos + self.x_pos_move, self.y_pos + i + self.y_pos_move)].cell.set_label("@")
                elif orientation == Orientation.EAST:
                    # take ship out of matrix
                    ShipsList.ship_buttons_dic[(self.x_pos + i, self.y_pos)].cell.set_label("_")
                    # draw new ship
                    ShipsList.ship_buttons_dic[(self.x_pos + i + self.x_pos_move, self.y_pos + self.y_pos_move)].cell.set_label("@")

        if ship_type == "carrier":
            for i in range(length):
                    if orientation == Orientation.NORTH:
                        # take ship out of matrix
                        #ShipsList.ship_buttons_dic[(self.x_pos+1, self.y_pos + i)].cell.set_label("_")
                        # draw new ship
                        ShipsList.ship_buttons_dic[(self.x_pos+1 + self.x_pos_move, self.y_pos + i + self.y_pos_move)].cell.set_label("@")
                    elif orientation == Orientation.EAST:
                        # take ship out of matrix
                        #ShipsList.ship_buttons_dic[(self.x_pos + i, self.y_pos+1)].cell.set_label("_")
                        # draw new ship
                        ShipsList.ship_buttons_dic[(self.x_pos + i + self.x_pos_move, self.y_pos+1 + self.y_pos_move)].cell.set_label("@")


class ShootingCell(urwid.PopUpLauncher):
    def __init__(self, x_pos, y_pos, game_controller, lobby_controller, loop):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.loop = loop
        self.cell = urwid.Button(".")
        super().__init__(self.cell)
        #super().__init__(urwid.Button("({}, {})".format(self.x_pos, self.y_pos)))
        urwid.connect_signal(self.original_widget, 'click', lambda button: self.shoot(button))

    def shoot(self, button):
        if ShipsList.your_turn == 1:
            #print("({}, {})".format(self.x_pos, self.y_pos))
            try:
                self.game_controller.shoot(self.x_pos, self.y_pos)
            except Exception as e:
                # TODO show a clear message of the illegale shoot
                #print("shoot sagt: {}".format(type(e)))
                print(e)
            try:
                shoot_task = self.loop.create_task(self.lobby_controller.send_shoot(self.x_pos, self.y_pos))
                # shoot_task.add_done_callback(self.set_label_after_shoot(button))
                shoot_task.add_done_callback(functools.partial(self.set_label_after_shoot, button))
            except Exception as e:
                # TODO show a clear message of the failed shoot
                #print("shoot sagt: {}".format(type(e)))
                print(e)
        else:
            button.set_label(".")


    def set_label_after_shoot(self, button, future):
        e = future.exception()
        if e is not None:
            raise e
        #print(e)
        #print(type(e))
        button.set_label("X")


class Battle:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.win = Screen("YOU LOOSE").show
        self.p1 = None
        self.p2 = None
        self.cells_dictionary = {}
        self.shoot_button_list = []
        self.chat = Chat(self.loop, self.lobby_controller)
        self.placed_ships = game_controller.get_all_ships_coordinates()

        # Registrering callbacks
        self.lobby_controller.set_callback(ProtocolMessageType.WAIT, self.you_wait)
        self.lobby_controller.set_callback(ProtocolMessageType.YOUSTART, self.you_play)
        self.lobby_controller.set_callback(ProtocolMessageType.TIMEOUT, self.change_player)
        self.lobby_controller.set_callback(ProtocolMessageType.FAIL, self.show_fail_position)
        self.lobby_controller.set_callback(ProtocolMessageType.HIT, self.hit_strike)
        self.lobby_controller.set_callback(ProtocolMessageType.ENDGAME, self.handle_endgame)
        self.lobby_controller.set_callback(ProtocolMessageType.MOVED, self.handle_moved)

        self.turn = urwid.Pile([urwid.Text("Opponent placing ships")])

        #setting round_time
        self.round_time = game_controller.get_round_time()
        self.round_time_pile = urwid.Pile([urwid.Button("0.0")])

        # Testing purposes
        ShipsList.test_refs = urwid.Button(str(game_controller.get_all_ships_coordinates()))
        ShipsList.test_refs_pile.contents.append((ShipsList.test_refs, ShipsList.test_refs_pile.options()))

        ShipsList.all_ships_coordinates = game_controller.get_all_ship_states()
        ShipsList.all_ships_coordinates_button = urwid.Button(str(ShipsList.all_ships_coordinates))
        ShipsList.test_refs_pile.contents.append((ShipsList.all_ships_coordinates_button, ShipsList.test_refs_pile.options()))

    def you_wait(self):
        self.turn.contents.clear()
        self.turn.contents.append((urwid.AttrWrap(urwid.LineBox(urwid.Text('Opponent Turn')), 'notturn'), self.turn.options()))
        self.periodic_round_time_getter()

    def you_play(self):
        self.turn.contents.clear()
        self.turn.contents.append((urwid.AttrWrap(urwid.LineBox(urwid.Text('Your Turn')), 'turn'), self.turn.options()))
        self.periodic_round_time_getter()
        ShipsList.your_turn = 1

    def change_player(self):
        # TODO controller should switch the time counter
        if self.game_controller.game_state == GameState.YOUR_TURN:
            self.you_play()
        elif self.game_controller.game_state == GameState.OPPONENTS_TURN:
            self.you_wait()
        print("Changed player")

    def handle_moved(self, positions):
        try:
            # TODO controller should switch the time counter
            if self.game_controller.game_state == GameState.YOUR_TURN:
                self.you_play()
                for position in positions["positions"].positions:
                    ShipsList.shoot_matrix__buttons_dic[(position.horizontal, position.vertical)].cell.set_label("|")
                    #print("({}, {})".format(position.horizontal, position.vertical))
            elif self.game_controller.game_state == GameState.OPPONENTS_TURN:
                self.you_wait()

        except Exception as e:
            print(e)

    def periodic_round_time_getter(self):
        self.round_time_pile.contents.clear()
        self.round_time_pile.contents.append((urwid.Text("Time: {}".format(str(self.game_controller.get_round_time()))), self.round_time_pile.options()))
        threading.Timer(2, self.periodic_round_time_getter).start()

    def hit_strike(self, sunk: bool, position: Position):
        # print("in hit strike")
        # self.game_controller.strike(position.horizontal, position.vertical)
        if self.game_controller.game_state == GameState.OPPONENTS_TURN:
            ShipsList.ship_buttons_dic[position.horizontal, position.vertical].cell.set_label("X")

    def fail_strike(self, position: Position):
        print("in fail strike")
        if self.game_controller.game_state == GameState.YOUR_TURN:
            ShipsList.ship_buttons_dic[position.horizontal, position.vertical].cell.set_label("X")

    def show_fail_position(self, position: Position):
        self.fail_strike(position)
        self.change_player()

    def unhandled(self, key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def abort(self, foo):
        abort_task = self.loop.create_task(self.lobby_controller.send_abort())
        abort_task.add_done_callback(self.abort_result)

    def abort_result(self, future):
        e = future.exception()
        if type(e) is BattleshipError:
            print(e.error_code)
        elif e is not None:
            raise e
        else:
            self.win()
            raise urwid.ExitMainLoop()

    def handle_endgame(self, reason: EndGameReason):
        if reason == EndGameReason.YOU_WON:
            Screen("YOU WON").show()
        elif reason == EndGameReason.OPPONENT_WON:
            Screen("YOU LOST").show()
        elif reason == EndGameReason.OPPONENT_ABORT:
            Screen("THEY ABORTED").show()
        elif reason == EndGameReason.OPPONENT_TIMEOUT:
            Screen("THEY TIMED OUT").show()
        elif reason == EndGameReason.SERVER_CLOSED_CONNECTION:
            Screen("SERVER CLOSED").show()
        else:
            Screen("ENDED. WHYEVER.").show()
        raise urwid.ExitMainLoop()

    def battle_main(self):
        field_offset = self.game_controller.length

        # Constructing shooting field
        shooting_line = []
        f = []
        for y_pos in range(field_offset):
            for x_pos in range(field_offset):
                ship_cell = ShootingCell(x_pos, y_pos, self.game_controller, self.lobby_controller, self.loop)
                shooting_line.append(ship_cell)
                self.shoot_button_list.append(ship_cell)
                ShipsList.shoot_matrix__buttons_dic[(x_pos, y_pos)] = ship_cell
            ship_zeil = urwid.GridFlow(shooting_line, 1, 1, 0, 'center')
            f.append(ship_zeil)
            shooting_line.clear()

        # Constructing ships field
        ship_button_list = []
        ship_f = []
        for y_pos in range(field_offset):
            for x_pos in range(field_offset):
                ship_cell = ButtonWithAPopUp(x_pos, y_pos, self.game_controller, self.lobby_controller, self.loop)
                # if (y_pos, x_pos) in self.placed_ships:
                #     ship_cell.cell.set_label("@")
                # else:
                #     ship_cell = urwid.Button("_")
                ship_button_list.append(ship_cell)
                # Dictionary with all cells
                ShipsList.ship_buttons_dic[(x_pos, y_pos)] = ship_cell

            ship_zeil = urwid.GridFlow(ship_button_list, 1, 1, 0, 'center')
            ship_f.append(ship_zeil)
            ship_button_list.clear()

        # Draw ships on the field
        for x_pos_1 in range(field_offset):
            for y_pos_2 in range(field_offset):
                if (x_pos_1, y_pos_2) in self.placed_ships:
                    ship_id = self.game_controller.get_ship_id_from_location(x_pos_1, y_pos_2)
                    ship_type = self.game_controller.get_ship_type_by_id(ship_id)

                    if self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.NORTH:
                        for s in range(ShipsList.length_dictionary[ship_type]):
                            ShipsList.ship_buttons_dic[(x_pos_1, y_pos_2+s)].cell.set_label("@")

                    elif self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.EAST:
                        for s in range(ShipsList.length_dictionary[ship_type]):
                            ShipsList.ship_buttons_dic[(x_pos_1+s, y_pos_2)].cell.set_label("@")

                    if ship_type == "carrier":
                        if self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.NORTH:
                            for s in range(ShipsList.length_dictionary[ship_type]):
                                ShipsList.ship_buttons_dic[(x_pos_1+1, y_pos_2+s)].cell.set_label("@")
                        elif self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.EAST:
                            for s in range(ShipsList.length_dictionary[ship_type]):
                                ShipsList.ship_buttons_dic[(x_pos_1+s, y_pos_2+1)].cell.set_label("@")

        # insert the matrix in piles
        shooting_pile = urwid.Pile(f)
        ship_pile = urwid.Pile(ship_f)

        # The rendered layout
        blank = urwid.Divider()
        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Opponent field"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("Your field")]),
                self.turn,
            ], 2),
            blank,
            urwid.Columns([
                shooting_pile,
                ship_pile,
                self.chat.render_chat(),
            ], 2),
            blank,
            urwid.Columns([
                urwid.Text(""),
                urwid.Text(""),
                urwid.LineBox(urwid.Button('Abort', on_press=self.abort)),
            ], 2),
            blank,
            #urwid.Button(str(self.placed_ships)),
            ShipsList.test_refs_pile,
            blank,
            self.round_time_pile
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

        palette = [
            ('ref', 'dark red', 'dark red', ''),
            ('miss', 'black', 'black', ''),
            ('untouched', 'white', 'black', ''),
            ('body', 'white', 'black', 'standout'),
            ('turn', 'dark blue', 'black'),
            ('notturn', 'dark red', 'black'),
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

        # use appropriate Screen class
        if urwid.web_display.is_web_request():
            screen = urwid.web_display.Screen()
        else:
            screen = urwid.raw_display.Screen()

        urwid.MainLoop(frame, palette, screen,
                       unhandled_input=self.unhandled, pop_ups=True,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()
