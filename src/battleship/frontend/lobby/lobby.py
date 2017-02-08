import urwid

from .create import CreateGame
from common.GameController import GameController
from client.lobby import ClientLobbyController


class GamesList:
    # Games list
    def __init__(self):
        self.game_1 = urwid.Text('Game 1')


class Chat:
    messages = urwid.Text("SHIIT")
    write_message = urwid.Edit("YOU")

    chat_pile = urwid.LineBox(urwid.Pile([messages, write_message]), title='Chat')

    @staticmethod
    def send_chat_message(text_edit):
        Chat.messages.set_text(text_edit)

    # TODO implement when server sends messages
    @staticmethod
    def receive_messages():
        pass


# class ChatDialog(urwid.Filler):
#     def keypress(self, size, key):
#         if key != 'enter':
#             return super(ChatDialog, self).keypress(size, key)
#         self.original_widget = urwid.Text(
#             u"Nice to meet you,\n%s.\n\nPress Q to exit." %
#             edit.edit_text)

class Lobby(urwid.GridFlow):
    # create game method (switch screen)
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.blank = urwid.Divider()
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
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
        self.games_list = []

    @staticmethod
    def unhandled(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def forward_create(self, foo):
        raise urwid.ExitMainLoop()

    def get_games(self):
        for g in self.games:
            # TODO: this should forward to join, with the appropriate game_id
            self.games_list.append(urwid.Button(g, on_press=self.forward_create))
        return self.games_list

    def begin_chat(self):
        # Chat.send_chat_message()
        urwid.connect_signal(Chat.messages, 'change', Chat.receive_messages())
        urwid.connect_signal(Chat.write_message, 'change', Chat.send_chat_message())

        return Chat.chat_pile

    def lobby_main(self):
        games_pile = urwid.LineBox(urwid.GridFlow(self.get_games(), 60, 1, 1, 'center'), title='Games List')
        edit = urwid.Edit(u"What is your name?\n")
        # chat_pile = ChatDialog(edit)

        chat_pile = urwid.LineBox(urwid.Pile([urwid.Text("message 1"), urwid.Text("message 2"), urwid.Text("message 3")]), 'Chat')

        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Games"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("Chat")]),
            ], 2),
            self.blank,

            urwid.Columns([
                games_pile,
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
