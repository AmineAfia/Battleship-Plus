import urwid

from .create import CreateGame
from common.GameController import GameController
from common.protocol import ProtocolMessageType
from client.lobby import ClientLobbyController
from .join import Join
from ..common.Chat import Chat

class Lobby(urwid.GridFlow):
    # create game method (switch screen)
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.blank = urwid.Divider()
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.lobby_controller.set_callback(ProtocolMessageType.GAME, self.game_callback)
        self.lobby_controller.set_callback(ProtocolMessageType.DELETE_GAME, self.delete_game_callback)
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
        # TODO: build kind of a table
        #self.games = [str(game) for game in lobby_controller.games.values()]
        #self.game_ids = [game_id for game_id in lobby_controller.games.keys()]
        self.params_as_list = [game.params_as_list() for game in lobby_controller.games.values()]
        # self.game_ids1 = [str(game_id) for game_id, game in lobby_controller.games.items()]
        self.games_list = []
        self.chat = Chat(self.loop, self.lobby_controller)
        self.games_pile = None
        self.games_pile_gridflow = None

    @staticmethod
    def unhandled(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def forward_create(self, foo):
        raise urwid.ExitMainLoop()

    def go_to_join_the_game(self, foo, game):
        join_task = self.loop.create_task(self.lobby_controller.send_join(game[0], ""))
        join_task.add_done_callback(self.init_controller_to_join_game(game))

    def init_controller_to_join_game(self, game):
        self.game_controller.game_id = game[0]
        self.game_controller.create_battlefield(int(game[1]), game[2])
        self.lobby_controller.is_joining_game = True
        raise urwid.ExitMainLoop()

    def get_games(self):
        for g in self.params_as_list:
            # TODO: this should forward to join, with the appropriate game_id
            self.games_list.append(urwid.Button(str(g), on_press=self.go_to_join_the_game, user_data=g))
        return self.games_list

    def game_callback(self, game):
        try:
            self.games_pile_gridflow.contents.append((urwid.Button(str(game.params_as_list()), on_press=self.go_to_join_the_game), self.games_pile_gridflow.options()))
            self.game_ids.append(game.game_id)
        except Exception as e:
            print(type(e))
            print(e)

    def delete_game_callback(self, game_id):
        try:
            for i, gid in enumerate(self.game_ids):
                if gid == game_id:
                    del self.games_pile_gridflow.contents[i]
                    del self.game_ids[i]
                    break
        except Exception as e:
            print(type(e))
            print(e)

    def lobby_main(self):
        # TODO: make some kind of table with columns and GridFlows or whatever
        self.games_pile_gridflow = urwid.GridFlow(self.get_games(), 60, 1, 1, 'center')
        self.games_pile = urwid.LineBox(self.games_pile_gridflow, title='Games List')

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

        urwid.MainLoop(frame, self.palette,
                       unhandled_input=self.unhandled, pop_ups=True,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()
