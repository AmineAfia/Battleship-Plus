"""
    Module for waitting screen. 
    We couldn't use the StaticScreen Module in common because we need to handle the STARTGAME Message here
"""
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
    """ Main class for Waiting. renders the waiting screen and handles STARTGAME when it comes """
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

    def handle_start_game(self):
        self.screen_finished.set()

    def dummy_function_for_cancel(self, foo):
        
        self.lobby_controller.is_cancelling_game = True
        self.screen_finished.set()

    def cancel_game(self, key):
        if key == "esc":
            login_task = self.loop.create_task(self.lobby_controller.send_cancel())
            login_task.add_done_callback(self.dummy_function_for_cancel)

    def waiting_main(self, foo):
        placeholder = urwid.SolidFill()
        loop = urwid.MainLoop(placeholder, self.palette, unhandled_input=self.cancel_game, pop_ups=True,
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

        cancel_mesage = urwid.Text("press 'esc' to cancel the game and go back to the lobby", align='center')
        for item in [cancel_mesage, outside, inside, streak, inside, outside]:
            pile.contents.append((item, pile.options()))

        self.loop.create_task(self.end_screen())
        loop.run()

    async def end_screen(self):
        await self.screen_finished.wait()
        self.lobby_controller.clear_callback(ProtocolMessageType.STARTGAME)
        raise urwid.ExitMainLoop()
