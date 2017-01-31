import urwid
from pyfiglet import Figlet

from ..game.battle import Battle
from common.GameController import GameController


class Waiting:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.wlcm = Figlet(font='big')

        self.palette =[
                ('banner', '', '', '', '#ffa', '#60a'),
                ('streak', '', '', '', 'g50', '#60a'),
                ('inside', '', '', '', 'g38', '#808'),
                ('outside', '', '', '', 'g27', '#a06'),
                ('bg', '', '', '', 'g7', '#d06')]

    def exit_on_q(self, key):
        if key == 'enter':
            battle_sessions = Battle(self.game_controller)
            battle_sessions.battle_main()
            raise urwid.ExitMainLoop()

    def waiting_main(self, foo):
        placeholder = urwid.SolidFill()
        loop = urwid.MainLoop(placeholder, self.palette, unhandled_input=self.exit_on_q, pop_ups=True)
        loop.screen.set_terminal_properties(colors=256)
        loop.widget = urwid.AttrMap(placeholder, 'bg')
        loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

        div = urwid.Divider()
        outside = urwid.AttrMap(div, 'outside')
        inside = urwid.AttrMap(div, 'inside')

        # TODO game result to be received from client/server in the battle screen to lunch the forward here
        result = 'win'
        if result == 'win':
            txt = urwid.Text(('banner', self.wlcm.renderText('Waiting !')), align='center')
            streak = urwid.AttrMap(txt, 'streak')
            pile = loop.widget.base_widget
            for item in [outside, inside, streak, inside, outside]:
                pile.contents.append((item, pile.options()))

        loop.run()
