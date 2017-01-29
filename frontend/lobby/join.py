# ships: carrier, battleship, cruiser, destroyer, submarine
import urwid

from .waitting import Waiting

class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with North, South, West and East buttons """
    signals = ['close']

    def __init__(self):
        # n_button = urwid.Padding(urwid.Button("North"), width=1)
        n_button = urwid.Button("North")
        s_button = urwid.Button("South")
        w_button = urwid.Button("West")
        e_button = urwid.Button("East")

        # w, align='left', width=('relative', 100), min_width=None, left=0, right=0)

        urwid.connect_signal(n_button, 'click',
                             lambda button: self._emit("close"))
        pile = urwid.Pile([n_button, urwid.Columns([w_button, e_button], 2), s_button])
        fill = urwid.Filler(pile)
        super().__init__(urwid.AttrWrap(fill, 'popbg'))


class ButtonWithAPopUp(urwid.PopUpLauncher):
    def __init__(self):
        super().__init__(urwid.Button("_"))
        urwid.connect_signal(self.original_widget, 'click',
                             lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog()
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}


class Join:
    def __init__(self):
        self.shit = None
        self.field_offset = 10
        self.palette = [
            ('hit', 'black', 'light gray', 'bold'),
            ('miss', 'black', 'black', ''),
            ('untouched', 'white', 'black', ''),
            ('body', 'white', 'black', 'standout'),
            ('reverse', 'light gray', 'black'),
            ('header', 'white', 'dark red', 'bold'),
            ('important', 'dark blue', 'light gray', ('standout', 'underline')),
            ('editfc', 'white', 'dark blue', 'bold'),
            ('editbx', 'light gray', 'dark blue'),
            ('editcp', 'black', 'light gray', 'standout'),
            ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
            ('buttn', 'white', 'black'),
            ('buttnf', 'white', 'dark blue', 'bold'),
            ('popbg', 'white', 'dark gray')
        ]
        self.blank = urwid.Divider()

    @staticmethod
    def forward_next(foo):
        go_to_game = Waiting()
        go_to_game.waiting_main(foo)
        raise urwid.ExitMainLoop()

    def unhandled(self, key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def join_main(self):
        # Constructing ships field
        ship_button_list = []
        ship_f = []
        for x in range(self.field_offset):
            for i in range(self.field_offset):
                ship_cell = ButtonWithAPopUp()
                ship_button_list.append(ship_cell)

            ship_zeil = urwid.GridFlow(ship_button_list, 1, 1, 0, 'center')
            ship_f.append(ship_zeil)
            ship_button_list.clear()

        forward_button = urwid.Button('Next', on_press=self.forward_next)
        ship_pile = urwid.Pile(ship_f)

        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Ship positioning"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("")]),
            ], 2),
            self.blank,

            ship_pile,
            self.blank,
            forward_button,
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

        urwid.MainLoop(frame, self.palette,
                       unhandled_input=self.unhandled, pop_ups=True).run()

if '__main__' == __name__:
    battle = Join()
    battle.join_main()
