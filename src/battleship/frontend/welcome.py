import urwid
from pyfiglet import Figlet

from .lobby.login import Login
from common.GameController import GameController
from client.lobby import ClientLobbyController


class Welcome:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.wlcm = Figlet(font='big')
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.palette = [
            ('banner', '', '', '', '#ffa', '#60a'),
            ('streak', '', '', '', 'g50', '#60a'),
            ('inside', '', '', '', 'g38', '#808'),
            ('outside', '', '', '', 'g27', '#a06'),
            ('bg', '', '', '', 'g7', '#d06')]

    def exit_on_q(self, key):
        if key == "enter":
            raise urwid.ExitMainLoop()

    def main_welcome(self):
        placeholder = urwid.SolidFill()
        loop = urwid.MainLoop(placeholder, self.palette, unhandled_input=self.exit_on_q,
                                    event_loop=urwid.AsyncioEventLoop(loop=self.loop))
        loop.screen.set_terminal_properties(colors=256)
        loop.widget = urwid.AttrMap(placeholder, 'bg')
        loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

        div = urwid.Divider()
        outside = urwid.AttrMap(div, 'outside')
        inside = urwid.AttrMap(div, 'inside')
        txt = urwid.Text(('banner', self.wlcm.renderText('Battleship+')), align='center')
        streak = urwid.AttrMap(txt, 'streak')
        pile = loop.widget.base_widget
        for item in [outside, inside, streak, inside, outside]:
            pile.contents.append((item, pile.options()))

        loop.run()
