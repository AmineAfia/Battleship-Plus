# import urwid
#
# palette = [('I say', 'default,bold', 'default', 'bold'),]
# ask = urwid.Edit(('I say', u"What is your name?\n"))
# reply = urwid.Text(u"")
# button = urwid.Button(u'Exit')
# div = urwid.Divider()
# pile = urwid.Pile([ask, div, reply, div, button])
# top = urwid.Filler(pile, valign='top')
#
# def on_ask_change(edit, new_edit_text):
#     reply.set_text(('I say', u"Nice to meet you, %s" % new_edit_text))
#
# def on_exit_clicked(button):
#     raise urwid.ExitMainLoop()
#
# urwid.connect_signal(ask, 'change', on_ask_change)
# urwid.connect_signal(button, 'click', on_exit_clicked)
#
# urwid.MainLoop(top, palette).run()

# ----------------------------------------------------

import urwid

class FibonacciWalker(urwid.ListWalker):
    """ListWalker-compatible class for browsing fibonacci set.
    positions returned are (value at position-1, value at position) tuples.
    """
    def __init__(self):
        self.focus = (0, 1)
        self.numeric_layout = NumericLayout()

    def _get_at_pos(self, pos):
        """Return a widget and the position passed."""
        return urwid.Text("%d"%pos[1], layout=self.numeric_layout), pos

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        a, b = start_from
        focus = b, a+b
        return self._get_at_pos(focus)

    def get_prev(self, start_from):
        a, b = start_from
        focus = b-a, a
        return self._get_at_pos(focus)

def main():
    palette = [
        ('body','black','dark cyan', 'standout'),
        ('foot','light gray', 'black'),
        ('key','light cyan', 'black', 'underline'),
        ('title', 'white', 'black',),
        ]

    footer_text = [
        ('title', "Fibonacci Set Viewer"), "    ",
        ('key', "UP"), ", ", ('key', "DOWN"), ", ",
        ('key', "PAGE UP"), " and ", ('key', "PAGE DOWN"),
        " move view  ",
        ('key', "Q"), " exits",
        ]

    def exit_on_q(input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    listbox = urwid.ListBox(FibonacciWalker())
    footer = urwid.AttrMap(urwid.Text(footer_text), 'foot')
    view = urwid.Frame(urwid.AttrWrap(listbox, 'body'), footer=footer)
    loop = urwid.MainLoop(view, palette, unhandled_input=exit_on_q)
    loop.run()


class NumericLayout(urwid.TextLayout):
    """
    TextLayout class for bottom-right aligned numbers
    """
    def layout( self, text, width, align, wrap ):
        """
        Return layout structure for right justified numbers.
        """
        lt = len(text)
        r = lt % width # remaining segment not full width wide
        if r:
            linestarts = range( r, lt, width )
            return [
                # right-align the remaining segment on 1st line
                [(width-r,None),(r, 0, r)]
                # fill the rest of the lines
                ] + [[(width, x, x+width)] for x in linestarts]
        else:
            linestarts = range( 0, lt, width )
            return [[(width, x, x+width)] for x in linestarts]


if __name__=="__main__":
    main()
