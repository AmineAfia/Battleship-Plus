import urwid
import re

from .create import CreateGame
from common.GameController import GameController
from client.lobby import ClientLobbyController
from .join import Join

class Lobby(urwid.GridFlow):
    # create game method (switch screen)
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.blank = urwid.Divider()
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.lobby_controller.ui_game_callback = self.game_callback
        self.lobby_controller.ui_delete_game_callback = self.delete_game_callback
        self.lobby_controller.ui_chat_recv_callback = self.chat_recv_callback
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
        self.games = [str(game) for game_id, game in lobby_controller.games.items()]
        self.game_ids = [game_id for game_id, game in lobby_controller.games.items()]
        self.game_ids1 = [str(game_id) for game_id, game in lobby_controller.games.items()]
        self.games_list = []

        self.games_pile = None
        self.games_pile_gridflow = None
        self.chat_messages = None
        self.chat_message = None
        self.post_chat_message = None
        self.username = None
        self.message_without_username = None

    @staticmethod
    def unhandled(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def forward_create(self, foo):
        raise urwid.ExitMainLoop()

    def get_games(self):
        for g in self.game_ids1:
            # TODO: this should forward to join, with the appropriate game_id
            self.games_list.append(urwid.Button(g, on_press=self.go_to_join_the_game()))
        return self.games_list

    def go_to_join_the_game(self):
        # join_game = Join(self.game_controller, self.lobby_controller, self.loop)
        # join_game.join_main()
        # raise urwid.ExitMainLoop()
        pass

    def game_callback(self, game):
        try:
            self.games_pile_gridflow.contents.append((urwid.Button(str(game), on_press=self.forward_create), self.games_pile_gridflow.options()))
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

    def chat_recv_callback(self, sender, recipient, text):
        message_to_append = urwid.Text("")
        if recipient == "":
            message_to_append.set_text("{}: {}".format(sender, text))
        else:
            message_to_append.set_text("{}: @{} {}".format(sender, recipient, text))

        self.chat_messages.contents.append((message_to_append, self.chat_messages.options()))

    def append_message(self):

        if '@' in self.chat_message.get_edit_text():
            self.username = re.search('@(.+?) ', self.chat_message.get_edit_text()).group(1)
            # TODO: fix this double space thingy
            self.message_without_username = self.chat_message.get_edit_text().replace("@{} ".format(self.username), "")
        else:
            self.username = ""
            self.message_without_username = self.chat_message.get_edit_text()

        try:
            self.loop.create_task(self.lobby_controller.send_chat(self.username, self.message_without_username))
            message_to_append = urwid.Text("")
            message_to_append.set_text(self.chat_message.get_edit_text())
            self.chat_messages.contents.append((message_to_append, self.chat_messages.options()))
            self.chat_message.set_edit_text("")
        except Exception as e:
            print(e)

    def lobby_main(self):
        # TODO: make some kind of table with columns and GridFlows or whatever
        self.games_pile_gridflow = urwid.GridFlow(self.get_games(), 60, 1, 1, 'center')
        self.games_pile = urwid.LineBox(self.games_pile_gridflow, title='Games List')

        self.chat_messages = urwid.Pile([urwid.Text("Hello!"), urwid.Text("Hey sup"), urwid.Text("join my game")])
        self.chat_message = urwid.Edit("->", edit_text=" ")

        #setting send button TODO: use controller to send the message to the server
        self.post_chat_message = urwid.Button("Send")
        urwid.connect_signal(self.post_chat_message, 'click', lambda button: self.append_message())

        chat_messages_pile = urwid.LineBox(self.chat_messages, 'Chat')
        chat_message_pile = urwid.LineBox(urwid.Columns([self.chat_message, self.post_chat_message]), '')
        chat_pile = urwid.Pile([chat_messages_pile, chat_message_pile])
        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Games"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("Chat")]),
            ], 2),
            self.blank,

            urwid.Columns([
                self.games_pile,
                chat_pile,
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
