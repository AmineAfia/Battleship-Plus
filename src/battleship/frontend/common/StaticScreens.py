""" This module is the colored screen to show states like: Welcome, Win, Lost... """
import urwid
from pyfiglet import Figlet


class Screen:
    """
        Main class to render the stats screen.
        :param text: text to be displayed
    """
    def __init__(self, text):
        self.wlcm = Figlet(font='big')
        self.text = text
        self.palette = [('banner', '', '', '', '#ffa', '#60a'),
                        ('streak', '', '', '', 'g50', '#60a'),
                        ('inside', '', '', '', 'g38', '#808'),
                        ('outside', '', '', '', 'g27', '#a06'),
                        ('bg', '', '', '', 'g7', '#d06'),]

    @staticmethod
    def exit_on_q(key):
        """ Method to exit the screen if esc or enter is pressed """
        if key == 'esc' or key == 'enter':
            raise urwid.ExitMainLoop()

    def show(self, foo=None):
        """ Render method """
        placeholder = urwid.SolidFill()
        loop = urwid.MainLoop(placeholder, self.palette, unhandled_input=self.exit_on_q, pop_ups=True)
        loop.screen.set_terminal_properties(colors=256)
        loop.widget = urwid.AttrMap(placeholder, 'bg')
        loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

        div = urwid.Divider()
        outside = urwid.AttrMap(div, 'outside')
        inside = urwid.AttrMap(div, 'inside')

        txt = urwid.Text(('banner', self.wlcm.renderText(self.text)), align='center')
        streak = urwid.AttrMap(txt, 'streak')
        pile = loop.widget.base_widget
        for item in [outside, inside, streak, inside, outside]:
            pile.contents.append((item, pile.options()))

        loop.run()
