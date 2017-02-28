import urwid
import logging
import asyncio

from .create import CreateGame
from common.GameController import GameController
from common.protocol import ProtocolMessageType
from client.lobby import ClientLobbyController
from .join import Join
from ..common.Chat import Chat


class PasswordPopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']
    def __init__(self, password_popup):
        self.password_popup = password_popup
        self.password = urwid.Edit(caption='password: ', multiline=False, align='left', wrap='space', allow_tab=False, mask="*")
        join_button = urwid.Button("Join")

        urwid.connect_signal(join_button, 'click',
                             lambda button: self.go_to_join_the_game(self.password_popup.g, self.password.get_edit_text()))

        pile = urwid.Pile([urwid.Text("Enter password"), self.password, join_button])
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))

    def go_to_join_the_game(self, game, password):
        join_task = self.password_popup.loop.create_task(self.password_popup.lobby_controller.send_join(game[0], password))
        join_task.add_done_callback(self.password_popup.init_controller_to_join_game(game))
        self._emit("close")

# Popup launcher with password support as a popup
class PasswordPopUp(urwid.PopUpLauncher):
    def __init__(self, g, loop, lobby_controller, game_controller):
        self.g = g
        self.loop = loop
        self.lobby_controller = lobby_controller
        self.game_controller = game_controller

        if self.g[3] == 1:
            tmp_string = str("(Password) Game {}: board size {} & {} ships".format(self.g[0], self.g[1], self.g[2]))
        else:
            tmp_string = str("Game {}: board size {} & {} ships".format(self.g[0], self.g[1], self.g[2]))
        
        self.game_button = urwid.Button(tmp_string)
        self.__super.__init__(self.game_button)

        if self.g[3] == 0:
            urwid.connect_signal(self.original_widget, 'click',
                                 lambda button: self.go_to_join_the_game(self.g))
        else:
            urwid.connect_signal(self.original_widget, 'click',
                                 lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PasswordPopUpDialog(self)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}

    def go_to_join_the_game(self, game):
        join_task = self.loop.create_task(self.lobby_controller.send_join(game[0], ""))
        join_task.add_done_callback(self.init_controller_to_join_game(game))

    def init_controller_to_join_game(self, game):
        # TODO: handle exceptions
        self.game_controller.game_id = game[0]
        self.game_controller.create_battlefield(int(game[1]), game[2])
        self.lobby_controller.is_joining_game = True
        raise urwid.ExitMainLoop()


class Lobby:
    # create game method (switch screen)
    def __init__(self, game_controller, lobby_controller, loop):
        self.blank = urwid.Divider()
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.loop = loop
        self.lobby_controller.set_callback(ProtocolMessageType.GAME, self.game_callback)
        self.lobby_controller.set_callback(ProtocolMessageType.DELETE_GAME, self.delete_game_callback)
        # self.lobby_controller.set_callback(ProtocolMessageType.GAMES, self.handle_games)

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
            ('turn', 'light cyan', 'black'),
            ('notturn', 'dark red', 'black'),
        ]
        self.games_list = {}
        self.chat = Chat(self.loop, self.lobby_controller)
        self.games_pile = None
        self.games_pile_gridflow = urwid.GridFlow([], 60, 1, 1, 'center')

        # self.game_ids = [game_id for game_id in lobby_controller.games.keys()]
        self.params_as_list = [game.params_as_list() for game in self.lobby_controller.games.values()]
        #logging.debug("params______: {}".format(self.params_as_list))
        # self.params_as_list = []

        # try:
        #     get_games_task = loop.create_task(lobby_controller.send_get_games())
        # except Exception as e:
        #     logging.debug("get_games_task: {}".format(str(type(e))))
            
        #     get_games_task.add_done_callback(self.get_games())

        # self.get_games()
        self.games_pile_gridflow = urwid.GridFlow(self.games_list.values(), 60, 1, 1, 'center')

    def handle_games(self):
        self.screen_finished.set()

    @staticmethod
    def unhandled(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def forward_create(self, foo):
        raise urwid.ExitMainLoop()

    def get_games(self):
        self.params_as_list = [game.params_as_list() for game in self.lobby_controller.games.values()]
        for g in self.params_as_list:
            self.games_list[g[0]] = PasswordPopUp(g, self.loop, self.lobby_controller, self.game_controller)
            # self.games_pile_gridflow.contents.clear()
            # self.games_pile_gridflow.contents.append((self.games_list[g[0]], self.games_pile_gridflow.options()))
        return self.games_list.values()

    def games_callback(self, games):
        try:
            logging.debug("__________games_callback_______ {}".format(games))
            self.games_list = {}
            self.get_games()
            self.games_pile_gridflow = urwid.GridFlow(self.get_games(), 60, 1, 1, 'center')
            # self.games_list[game.game_id] = PasswordPopUp(game.params_as_list(), self.loop, self.lobby_controller, self.game_controller)
            # self.games_pile_gridflow.contents.clear()
            # self.games_pile_gridflow.contents.append((self.games_list[game.game_id], self.games_pile_gridflow.options()))
        except Exception as e:
            logging.error(str(type(e)))
            logging.error(str(e))

    def game_callback(self, game):
        try:
            self.games_list[game.game_id] = PasswordPopUp(game.params_as_list(), self.loop, self.lobby_controller, self.game_controller)
            self.games_pile_gridflow.contents.append((self.games_list[game.game_id], self.games_pile_gridflow.options()))
        except Exception as e:
            logging.error(str(type(e)))
            logging.error(str(e))

    def delete_game_callback(self, game_id):
        try:
            self.games_pile_gridflow.contents.remove((self.games_list[game_id], self.games_pile_gridflow.options()))
        except Exception as e:
            logging.error("delete handler: {}".format(type(e)))
            logging.error("delete handler: {}".format(str(e)))

        # try:
        #     get_games_task = self.loop.create_task(self.lobby_controller.send_get_games())
        #     get_games_task.add_done_callback(self.get_games())
        #     self.lobby_controller.set_callback(ProtocolMessageType.GAMES, self.games_callback)
        # except Exception as e:
        #     logging.debug("get_games_task: {}".format(str(type(e))))

    def lobby_main(self):
        # TODO: make some kind of table with columns and GridFlows or whatever
        # Get GAMES each time we render the lobby screen
        
        self.games_pile_gridflow = urwid.GridFlow(self.get_games(), 60, 1, 1, 'center')

        # self.get_games()
        self.games_pile = urwid.LineBox(self.games_pile_gridflow, title='Games List')
        self.games_pile_gridflow.render((1,))
        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Games"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("Chat")]),
            ], 2),
            self.blank,

            urwid.Columns([
                self.games_pile,
                self.chat.render_chat(),
            ], 2),
            self.blank,
            urwid.Columns([
                urwid.LineBox(urwid.GridFlow([urwid.Button('Create Game', on_press=self.forward_create)], 15, -10, -10, 'center'), title=''),
                urwid.Text(''),
            ], 2),
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)
        
        self.loop.create_task(self.end_screen())
        urwid.MainLoop(frame, self.palette,
                       unhandled_input=self.unhandled, pop_ups=True,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()

    async def end_screen(self):
        await self.screen_finished.wait()

        self.get_games()
        self.games_pile_gridflow = urwid.GridFlow(self.get_games(), 60, 1, 1, 'center')

        self.lobby_controller.clear_callback(ProtocolMessageType.GAME)
        # self.lobby_controller.clear_callback(ProtocolMessageType.GAMES)
        self.lobby_controller.clear_callback(ProtocolMessageType.DELETE_GAME)
        # raise urwid.ExitMainLoop()
