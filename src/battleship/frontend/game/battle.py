import urwid
import urwid.raw_display
import urwid.web_display
import threading
import time
import functools
import asyncio
import logging

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

    # For testing purposes
    # all_ships_coordinates = []
    # test_refs = urwid.Button("")
    # test_refs_pile = urwid.Pile([test_refs])

    # Dictionary to keep track of ships movement 
    ships_dictionary = {}

    # variable to allow players to shoot and move fro the UI
    your_turn = 0

    immovable_coordinates = []
    # notifications for illegal shoots/ fail - hit notifications
    battle_notifications = urwid.Pile([urwid.Text("Opponent field")])

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


        if (self.x_pos , self.y_pos) in ShipsList.immovable_coordinates:
            pile = urwid.Pile([self.exit_button, urwid.Text("This ship is immovable!")])
        else:
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
            except Exception as e:
                # TODO show a clear message of the failed shoot
                #logging.debug("shoot sagt: {}".format(type(e)))
                logging.debug("moving: {}".format(e))
                self._emit("close")

            try:
                self._emit("close")

                self.button_with_pop_up.move_ship_in_position(self.ship_orientation, self.ship_length, self.ship_type, direction, self.ship_id)
                move_task = self.loop.create_task(self.lobby_controller.send_move(self.ship_id, direction))
                move_task.add_done_callback(self.passing_callback)
            except Exception as e:
                # TODO show a clear message of the failed shoot
                #logging.debug("shoot sagt: {}".format(type(e)))
                logging.debug("moving: {}".format(e))
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
                             lambda button: self.dummy_pop_up_opener())

    def dummy_pop_up_opener(self):
        self.open_pop_up()

    def create_pop_up(self):
        pop_up = PopUpDialog(self, self.x_pos, self.y_pos, self.game_controller, self.lobby_controller, self.loop)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}

    def move_ship_in_position(self, orientation, length, ship_type, direction, ship_id):

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

        for ship_cell_k, ship_cell_v in ShipsList.ships_dictionary.items():
            if ship_cell_k == ship_id:
                ship_cell_v_copy = list(ship_cell_v)
                # take the existing ship out of the board
                for (ship_cell_x, ship_cell_y) in ship_cell_v_copy:
                    if orientation == Orientation.NORTH:
                        ShipsList.ship_buttons_dic[(ship_cell_x, ship_cell_y)].cell.set_label("_")
                    elif orientation == Orientation.EAST:
                        ShipsList.ship_buttons_dic[(ship_cell_x, ship_cell_y)].cell.set_label("_")

                # draw new ship
                for (ship_cell_x, ship_cell_y) in ship_cell_v_copy:
                    if orientation == Orientation.NORTH:
                        ShipsList.ship_buttons_dic[(ship_cell_x + self.x_pos_move, ship_cell_y + self.y_pos_move)].cell.set_label("@")
                    elif orientation == Orientation.EAST:
                        ShipsList.ship_buttons_dic[(ship_cell_x + self.x_pos_move, ship_cell_y + self.y_pos_move)].cell.set_label("@")
                    ShipsList.ships_dictionary[ship_id].remove((ship_cell_x, ship_cell_y))
                    ShipsList.ships_dictionary[ship_id].append((ship_cell_x + self.x_pos_move, ship_cell_y + self.y_pos_move))
                    
                # DEBUGING: showing the new ships position
                # ShipsList.all_ships_coordinates_button = urwid.Button(str(ShipsList.ships_dictionary))
                # ShipsList.test_refs_pile.contents.append((ShipsList.all_ships_coordinates_button, ShipsList.test_refs_pile.options()))


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
        allowed_shoot_bool = False
        if ShipsList.your_turn == 1:
            #logging.debug("({}, {})".format(self.x_pos, self.y_pos))
            try:
                self.game_controller.shoot(self.x_pos, self.y_pos)
                allowed_shoot_bool = True
            except Exception as e:
                allowed_shoot_bool = False
                ShipsList.battle_notifications.contents.clear()
                ShipsList.battle_notifications.contents.append((urwid.Text("Opponent field!"), ShipsList.battle_notifications.options()))
                ShipsList.battle_notifications.contents.append((urwid.Text(('notturn', "Try another time! you already have a hit in that field")), ShipsList.battle_notifications.options()))
                logging.error(str(e))
            try:
                if allowed_shoot_bool is True:
                    shoot_task = self.loop.create_task(self.lobby_controller.send_shoot(self.x_pos, self.y_pos))
                    # shoot_task.add_done_callback(self.set_label_after_shoot(button))
                    shoot_task.add_done_callback(functools.partial(self.set_label_after_shoot, button))
            except Exception as e:
                ShipsList.battle_notifications.contents.clear()
                ShipsList.battle_notifications.contents.append((urwid.Text("Opponent field!"), ShipsList.battle_notifications.options()))
                ShipsList.battle_notifications.contents.append((urwid.Text(('notturn', "Try another time! you already have a hit in that field")), ShipsList.battle_notifications.options()))
                logging.error(str(e))


    def set_label_after_shoot(self, button, future):
        e = future.exception()
        if e is not None:
            raise e
        #logging.error(str(e))
        #logging.error(str(type(e)))
        button.set_label("X")


class Battle:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
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

        self.screen_finished: asyncio.Event = asyncio.Event()

        self.turn = urwid.Pile([urwid.Text("Opponent placing ships")])

        #setting round_time
        self.round_time = game_controller.get_round_time()
        self.round_time_pile = urwid.Pile([urwid.Button("0.0")])

        # For testing purposes
        # ShipsList.test_refs = urwid.Button(str(game_controller.get_all_ships_coordinates()))
        # ShipsList.test_refs_pile.contents.append((ShipsList.test_refs, ShipsList.test_refs_pile.options()))

    def you_wait(self):
        self.turn.contents.clear()
        self.turn.contents.append((urwid.AttrWrap(urwid.LineBox(urwid.Text('Opponent Turn')), 'notturn'), self.turn.options()))
        self.periodic_round_time_getter()
        ShipsList.your_turn = 0

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
        logging.info("Changed player")

    def handle_moved(self, positions):
        try:
            # TODO controller should switch the time counter
            if self.game_controller.game_state == GameState.YOUR_TURN:
                self.you_play()
                for position in positions["positions"].positions:
                    ShipsList.shoot_matrix__buttons_dic[(position.horizontal, position.vertical)].cell.set_label("|")
                    #logging.debug("({}, {})".format(position.horizontal, position.vertical))
            elif self.game_controller.game_state == GameState.OPPONENTS_TURN:
                self.you_wait()

        except Exception as e:
            logging.error(str(e))

    def periodic_round_time_getter(self):
        self.round_time_pile.contents.clear()
        self.round_time_pile.contents.append((urwid.Text("Time: {}".format(str(self.game_controller.get_round_time()))), self.round_time_pile.options()))
        threading.Timer(2, self.periodic_round_time_getter).start()

    def hit_strike(self, sunk: bool, position: Position):
        # logging.debug("in hit strike")
        # self.game_controller.strike(position.horizontal, position.vertical)
        if self.game_controller.game_state == GameState.OPPONENTS_TURN:
            ShipsList.ship_buttons_dic[position.horizontal, position.vertical].cell.set_label(('notturn', "@"))
            hited_ship_id = self.game_controller.get_ship_id_from_location(position.horizontal, position.vertical)
            # Disconnect the hited ship popup signal so the user can't move it
            for ship_k, ship_v in ShipsList.ships_dictionary.items():
                if ship_k == hited_ship_id:
                    ship_v_copy = list(ship_v)
                    for (ship_x, ship_y) in ship_v_copy:
                        try:
                            ShipsList.immovable_coordinates.append((ship_x, ship_y))
                            # urwid.disconnect_signal(ShipsList.ship_buttons_dic[ship_x, ship_y], 'click', ButtonWithAPopUp.open_pop_up(ShipsList.ship_buttons_dic[ship_x, ship_y].cell))
                            # urwid.disconnect_signal(ShipsList.movement_popups_dic[ship_x, ship_y], 'click', getattr(ShipsList.ship_buttons_dic[ship_x, ship_y], 'dummy_pop_up_opener'))

                        except Exception as e:
                            logging.debug("_____hit____: {} / {}".format(e, type(e)))
        else:
            ShipsList.shoot_matrix__buttons_dic[(position.horizontal, position.vertical)].cell.set_label(('hit', "X"))
            ShipsList.battle_notifications.contents.clear()
            ShipsList.battle_notifications.contents.append((urwid.Text("Opponent field!"), ShipsList.battle_notifications.options()))
            ShipsList.battle_notifications.contents.append((urwid.Text(('hit', "HIT!")), ShipsList.battle_notifications.options()))

    def fail_strike(self, position: Position):
        logging.debug("in fail strike")
        if self.game_controller.game_state == GameState.YOUR_TURN:
            ShipsList.ship_buttons_dic[position.horizontal, position.vertical].cell.set_label("X")
        else:
            ShipsList.battle_notifications.contents.clear()
            ShipsList.battle_notifications.contents.append((urwid.Text("Opponent field"), ShipsList.battle_notifications.options()))
            ShipsList.battle_notifications.contents.append((urwid.Text(('notturn', "FAIL!")), ShipsList.battle_notifications.options()))

    def show_fail_position(self, position: Position):
        self.change_player()
        self.fail_strike(position)

    def unhandled(self, key):
        if key == 'esc':
            self.screen_finished.set()

    def abort(self, foo):
        abort_task = self.loop.create_task(self.lobby_controller.send_abort())
        abort_task.add_done_callback(self.abort_result)

    def abort_result(self, future):
        e = future.exception()
        if type(e) is BattleshipError:
            logging.error(str(e.error_code))
        elif e is not None:
            raise e
        else:
            the_screen = Screen("YOU LOOSE").show()
            del the_screen
            self.screen_finished.set()

    def handle_endgame(self, reason: EndGameReason):
        the_screen = None
        if reason == EndGameReason.YOU_WON:
            the_screen = Screen("YOU WON").show()
        elif reason == EndGameReason.OPPONENT_WON:
            the_screen = Screen("YOU LOST").show()
        elif reason == EndGameReason.OPPONENT_ABORT:
            the_screen = Screen("THEY ABORTED").show()
        elif reason == EndGameReason.OPPONENT_TIMEOUT:
            the_screen = Screen("THEY TIMED OUT").show()
        elif reason == EndGameReason.SERVER_CLOSED_CONNECTION:
            the_screen = Screen("SERVER CLOSED").show()
        else:
            the_screen = Screen("ENDED. WHYEVER.").show()
        del the_screen
        self.screen_finished.set()

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

                    tmp_ship_list = []
                    if self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.NORTH:
                        for s in range(ShipsList.length_dictionary[ship_type]):
                            ShipsList.ship_buttons_dic[(x_pos_1, y_pos_2+s)].cell.set_label("@")
                            tmp_ship_list.append((x_pos_1, y_pos_2+s))
                        ShipsList.ships_dictionary[ship_id] = tmp_ship_list
                        tmp_ship_list = []

                    elif self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.EAST:
                        for s in range(ShipsList.length_dictionary[ship_type]):
                            ShipsList.ship_buttons_dic[(x_pos_1+s, y_pos_2)].cell.set_label("@")
                            tmp_ship_list.append((x_pos_1+s, y_pos_2))
                        ShipsList.ships_dictionary[ship_id] = tmp_ship_list
                        tmp_ship_list = []

                    if ship_type == "carrier":
                        if self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.NORTH:
                            for s in range(ShipsList.length_dictionary[ship_type]):
                                ShipsList.ship_buttons_dic[(x_pos_1+1, y_pos_2+s)].cell.set_label("@")
                                tmp_ship_list.append((x_pos_1+1, y_pos_2+s))
                            tmp_cords = ShipsList.ships_dictionary.get(ship_id)
                            for tmp_ship in tmp_ship_list:
                                tmp_cords.append(tmp_ship)
                            ShipsList.ships_dictionary[ship_id] = tmp_cords
                            tmp_ship_list = []
                        elif self.game_controller.get_ship_orientation_by_id(ship_id) == Orientation.EAST:
                            for s in range(ShipsList.length_dictionary[ship_type]):
                                ShipsList.ship_buttons_dic[(x_pos_1+s, y_pos_2+1)].cell.set_label("@")
                                tmp_ship_list.append((x_pos_1+s, y_pos_2+1))
                            tmp_cords = ShipsList.ships_dictionary.get(ship_id)
                            for tmp_ship in tmp_ship_list:
                                tmp_cords.append(tmp_ship)
                            ShipsList.ships_dictionary[ship_id] = tmp_cords
                            tmp_ship_list = []

        # insert the matrix in piles
        shooting_pile = urwid.Pile(f)
        ship_pile = urwid.Pile(ship_f)

        # ShipsList.all_ships_coordinates_button = urwid.Button(str(ShipsList.ships_dictionary))
        # ShipsList.test_refs_pile.contents.append((ShipsList.all_ships_coordinates_button, ShipsList.test_refs_pile.options()))

        # The rendered layout
        blank = urwid.Divider()
        widget_list = [
            urwid.Columns([
                ShipsList.battle_notifications,
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
            # ShipsList.test_refs_pile,
            # blank,
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
            ('hit', 'dark green', 'black'),
            ('notturn', 'dark red', 'black'),
            ('header', 'white', 'dark red', 'bold'),
            ('important', 'dark blue', 'light gray', ('standout', 'underline')),
            ('editfc', 'white', 'dark blue', 'bold'),
            ('editbx', 'light gray', 'dark blue'),
            ('editcp', 'black', 'light gray', 'standout'),
            ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
            ('buttn', 'white', 'black'),
            ('buttnf', 'white', 'dark blue', 'bold'),
            ('popbg', 'white', 'dark gray'),
        ]

        # use appropriate Screen class
        if urwid.web_display.is_web_request():
            screen = urwid.web_display.Screen()
        else:
            screen = urwid.raw_display.Screen()

        self.loop.create_task(self.end_screen())
        urwid.MainLoop(frame, palette, screen,
                       unhandled_input=self.unhandled, pop_ups=True,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()

    async def end_screen(self):
        await self.screen_finished.wait()
        # reset variables
        ShipsList.battle_notifications.contents.clear()
        ShipsList.battle_notifications.contents.append((urwid.Text("Opponent field"), ShipsList.battle_notifications.options()))
        # TODO: kill all registered callbacks
        self.lobby_controller.clear_callback(ProtocolMessageType.STARTGAME)
        self.lobby_controller.clear_callback(ProtocolMessageType.WAIT)
        self.lobby_controller.clear_callback(ProtocolMessageType.YOUSTART)
        self.lobby_controller.clear_callback(ProtocolMessageType.TIMEOUT)
        self.lobby_controller.clear_callback(ProtocolMessageType.FAIL)
        self.lobby_controller.clear_callback(ProtocolMessageType.HIT)
        self.lobby_controller.clear_callback(ProtocolMessageType.ENDGAME)
        self.lobby_controller.clear_callback(ProtocolMessageType.MOVED)
        raise urwid.ExitMainLoop()
