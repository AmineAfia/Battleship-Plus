# import urwid
# import asyncio
#
# from .lobby import Lobby
# from common.GameController import GameController
# from client.lobby import ClientLobbyController
# from common.states import ClientConnectionState
# from common.errorHandler.BattleshipError import BattleshipError
# from common.constants import ErrorCode
#
#
# class Login:
#     def __init__(self, game_controller, lobby_controller, loop):
#         self.game_controller = game_controller
#         self.lobby_controller = lobby_controller
#         self.loop = loop
#         self.username = urwid.Edit("Username: ")
#
#     def forward_lobby(self, key):
#         if key == 'enter':
#             login_task = self.loop.create_task(self.lobby_controller.try_login(self.username.get_edit_text()))
#             login_task.add_done_callback(self.login_result)
#
#     def login_result(self, future):
#         # check if there is an error message to display
#         e = future.exception()
#         if type(e) is BattleshipError:
#             if e.error_code == ErrorCode.PARAMETER_INVALID_USERNAME:
#                 # TODO: popup
#                 print("username cannot be empty")
#             elif e.error_code == ErrorCode.PARAMETER_USERNAME_ALREADY_EXISTS:
#                 # TODO: popup
#                 print("username already exists")
#         # and check if we are really logged in
#         elif not self.lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
#             # ok, we are logged in
#             raise urwid.ExitMainLoop()
#         else:
#             # TODO: popup
#             print("some other weird login error")
#
#     def login_main(self):
#         dialog = urwid.Columns([
#                     urwid.Text(""),
#                     urwid.LineBox(urwid.Pile([self.username]), 'Login'),
#                     urwid.Text("")
#                     ], 2)
#         f = urwid.Filler(dialog)
#         # f.render((1, 1))
#         urwid.MainLoop(f, unhandled_input=self.forward_lobby,
#                        event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()

import subprocess
import urwid
import os
import sys

factor_me = 362923067964327863989661926737477737673859044111968554257667
run_me = os.path.join(os.path.dirname(sys.argv[0]), 'subproc2.py')

output_widget = urwid.Text("Factors of %d:\n" % factor_me)
edit_widget = urwid.Edit("Type anything or press enter to exit:")
frame_widget = urwid.Frame(
    header=edit_widget,
    body=urwid.Filler(output_widget, valign='bottom'),
    focus_part='header')

def exit_on_enter(key):
    if key == 'enter': raise urwid.ExitMainLoop()

loop = urwid.MainLoop(frame_widget, unhandled_input=exit_on_enter)

def received_output(data):
    output_widget.set_text(output_widget.text + data)

write_fd = loop.watch_pipe(received_output)
proc = subprocess.Popen(
    ['python', '-u', run_me, str(factor_me)],
    stdout=write_fd,
    close_fds=True)

loop.run()
proc.kill()
