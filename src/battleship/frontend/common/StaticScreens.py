import urwid
from pyfiglet import Figlet


class Screen:
    def __init__(self, text):
        self.wlcm = Figlet(font='big')
        self.text = text

        self.palette =[
                ('banner', '', '', '', '#ffa', '#60a'),
                ('streak', '', '', '', 'g50', '#60a'),
                ('inside', '', '', '', 'g38', '#808'),
                ('outside', '', '', '', 'g27', '#a06'),
                ('bg', '', '', '', 'g7', '#d06'),]

    @staticmethod
    def exit_on_q(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def show(self, foo):
        placeholder = urwid.SolidFill()
        loop = urwid.MainLoop(placeholder, self.palette, unhandled_input=self.exit_on_q, pop_ups=True)
        loop.screen.set_terminal_properties(colors=256)
        loop.widget = urwid.AttrMap(placeholder, 'bg')
        loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

        div = urwid.Divider()
        outside = urwid.AttrMap(div, 'outside')
        inside = urwid.AttrMap(div, 'inside')

        # TODO game result to be received from controller in the battle screen to lunch the forward here
        txt = urwid.Text(('banner', self.wlcm.renderText(self.text)), align='center')
        streak = urwid.AttrMap(txt, 'streak')
        pile = loop.widget.base_widget
        for item in [outside, inside, streak, inside, outside]:
            pile.contents.append((item, pile.options()))

        loop.run()
