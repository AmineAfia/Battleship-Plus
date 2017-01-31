import urwid
import asyncio

from .lobby import Lobby
from common.GameController import GameController
from client.lobby import ClientLobbyController
from common.states import ClientConnectionState


class Login:
    def __init__(self, game_controller, lobby_controller, loop):
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.loop = loop
        self.username = urwid.Edit("Username: ")
        self.login_task = None

    def forward_lobby(self, key):
        if key == 'enter':
            self.login_task = asyncio.Task(self.lobby_controller.try_login(self.username.get_edit_text()),
                                           loop=self.lobby_controller.client.loop)
            self.login_task.add_done_callback(self.login_result)

    def login_result(self, _):
        if not self.lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
            raise urwid.ExitMainLoop()
        else:
            # TODO: some kind of feedback…
            raise urwid.ExitMainLoop()

    def login_main(self):

        dialog = urwid.Columns([
                    urwid.Text(""),
                    urwid.LineBox(urwid.Pile([self.username]), 'Login'),
                    urwid.Text("")
                    ], 2)

        f = urwid.Filler(dialog)
        # f.render((1, 1))
        urwid.MainLoop(f, unhandled_input=self.forward_lobby,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()
