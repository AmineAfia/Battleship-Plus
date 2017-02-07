import urwid
import asyncio

from .lobby import Lobby
from common.GameController import GameController
from client.lobby import ClientLobbyController
from common.states import ClientConnectionState
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode


class Login:
    def __init__(self, game_controller, lobby_controller, loop):
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.loop = loop
        self.username = urwid.Edit("Username: ")

    def forward_lobby(self, key):
        if key == 'enter':
            login_task = self.loop.create_task(self.lobby_controller.try_login(self.username.get_edit_text()))
            login_task.add_done_callback(self.login_result)

    def login_result(self, future):
        # check if there is an error message to display
        e = future.exception()
        if type(e) is BattleshipError:
            if e.error_code == ErrorCode.PARAMETER_INVALID_USERNAME:
                # TODO: popup
                print("username cannot be empty")
            elif e.error_code == ErrorCode.PARAMETER_USERNAME_ALREADY_EXISTS:
                # TODO: popup
                print("username already exists")
        # and check if we are really logged in
        elif not self.lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
            # ok, we are logged in
            raise urwid.ExitMainLoop()
        else:
            # TODO: popup
            print("some other weird login error")

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
