import urwid
import asyncio
from pyfiglet import Figlet
import logging

from ..game.battle import Battle
from common.GameController import GameController
from client.lobby import ClientLobbyController
from common.protocol import ProtocolMessageType
from ..common.StaticScreens import Screen


class Waiting:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.wlcm = Figlet(font='big')

        self.lobby_controller.set_callback(ProtocolMessageType.STARTGAME, self.handle_start_game)
        self.screen_finished: asyncio.Event = asyncio.Event()

        self.palette =[
                ('banner', '', '', '', '#ffa', '#60a'),
                ('streak', '', '', '', 'g50', '#60a'),
                ('inside', '', '', '', 'g38', '#808'),
                ('outside', '', '', '', 'g27', '#a06'),
                ('bg', '', '', '', 'g7', '#d06')]

    #
    # def forward_to_join(self, msg):
    #     logging.info("You can start!!!!")
    #     raise urwid.ExitMainLoop()

    def exit_on_q(self, key):
        if key == 'esc':
            self.screen_finished.set()
            #raise urwid.ExitMainLoop()

    def handle_start_game(self):
        self.screen_finished.set()

    def dummy_function_for_cancel(self, foo):
        self.lobby_controller.is_cancelling_game = True
        self.screen_finished.set()

    def cancel_game(self, foo):
        login_task = self.loop.create_task(self.lobby_controller.send_cancel())
        login_task.add_done_callback(self.dummy_function_for_cancel)

    def waiting_main(self, foo):
        placeholder = urwid.SolidFill()
        loop = urwid.MainLoop(placeholder, self.palette, unhandled_input=self.exit_on_q, pop_ups=True,
                              event_loop=urwid.AsyncioEventLoop(loop=self.loop))
        loop.screen.set_terminal_properties(colors=256)
        loop.widget = urwid.AttrMap(placeholder, 'bg')
        loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

        div = urwid.Divider()
        outside = urwid.AttrMap(div, 'outside')
        inside = urwid.AttrMap(div, 'inside')

        # TODO game result to be received from client/server in the battle screen to lunch the forward here
        txt = urwid.Text(('banner', self.wlcm.renderText('Waiting !')), align='center')
        streak = urwid.AttrMap(txt, 'streak')
        pile = loop.widget.base_widget

        cancel_button = urwid.Button("Cancel", on_press=self.cancel_game)
        for item in [cancel_button, outside, inside, streak, inside, outside]:
            pile.contents.append((item, pile.options()))

        self.loop.create_task(self.end_screen())
        loop.run()

    async def end_screen(self):
        await self.screen_finished.wait()
        self.lobby_controller.clear_callback(ProtocolMessageType.STARTGAME)
        raise urwid.ExitMainLoop()
