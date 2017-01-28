import urwid
import urwid.raw_display
import urwid.web_display
from pyfiglet import Figlet

from result import Result


def unhandled(key):
    if key == 'q':
        raise urwid.ExitMainLoop()

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
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))


class ButtonWithAPopUp(urwid.PopUpLauncher):
    def __init__(self):
        self.__super.__init__(urwid.Button("_"))
        urwid.connect_signal(self.original_widget, 'click',
                             lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog()
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}


class Battle():
    def __init__(self):
        self._my_attribute = 0
        self.win = Result().show_winner

    def main(self):
        ''' Variables region'''
        shoots = [(1, 1), (2, 2), (3, 5), (1, 2), (2, 1), (1, 3), (3, 1), (1, 4)]
        field_offset = 10
        text_button_list = {}
        '''End of region'''

        '''Functions region'''

        def button_press(self):
            frame.footer = urwid.AttrWrap(urwid.Text(
                [u"Pressed: ", self.get_label()]), 'header')

        # function to shoot the opponents field
        def shoot(self):
            self.set_label('X')

        # function to move ships
        def move(self):
            if self.get_label() == 'North':
                self.set_label('N')
            elif self.get_label() == 'South':
                self.set_label('S')
            elif self.get_label() == 'West':
                self.set_label('W')
            elif self.get_label() == 'East':
                self.set_label('E')

        # def forward_win():
        #     Result.show_winner()
        '''End of region'''

        '''Rendering region'''
        # Constructing shooting field
        button_list = []
        f = []
        for x in range(field_offset):
            for i in range(field_offset):
                cell = urwid.AttrWrap(urwid.Button('.', on_press=shoot), 'buttn', 'buttnf')
                button_list.append(cell)
            zeil = urwid.GridFlow(button_list, 1, 1, 0, 'center')
            f.append(zeil)
            button_list.clear()

        # Constructing ships field
        ship_button_list = []
        ship_f = []
        for x in range(field_offset):
            for i in range(field_offset):
                ship_cell = ButtonWithAPopUp()
                ship_button_list.append(ship_cell)

            ship_zeil = urwid.GridFlow(ship_button_list, 1, 1, 0, 'center')
            ship_f.append(ship_zeil)
            ship_button_list.clear()

        # insert the matrix in piles
        shooting_pile = urwid.Pile(f)
        ship_pile = urwid.Pile(ship_f)

        # The rendered layout
        blank = urwid.Divider()
        widget_list = [
            urwid.Columns([
                urwid.Padding(urwid.Text("Opponent field"), left=2, right=0, min_width=20),
                urwid.Pile([urwid.Text("Your field")]),
            ], 2),
            blank,

            urwid.Columns([
                shooting_pile,
                ship_pile,
            ], 2),
            blank,
            urwid.Columns([
                urwid.Button('WIN', on_press=self.win),
            ], 2),
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)
        '''End of region'''

        palette = [
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

        # use appropriate Screen class
        if urwid.web_display.is_web_request():
            screen = urwid.web_display.Screen()
        else:
            screen = urwid.raw_display.Screen()

        urwid.MainLoop(frame, palette, screen,
                       unhandled_input=unhandled, pop_ups=True).run()

    def setup(self):
        urwid.web_display.set_preferences("Urwid Tour")
        # try to handle short web requests quickly
        if urwid.web_display.handle_short_request():
            return

        self.main()


if '__main__' == __name__ or urwid.web_display.is_web_request():
    battle = Battle()
    battle.setup()
