# ships: carrier, battleship, cruiser, destroyer, submarine
import urwid

from .waitting import Waiting
from common.GameController import GameController


class ShipsList:
    ships_list = []
    ships = (2, 0, 1, 0, 1)
    info_pile = None

    @staticmethod
    def get_ships():
        ShipsList.ships_list.append(urwid.Button(("carrier {}".format(ShipsList.ships[0]))))
        ShipsList.ships_list.append(urwid.Button(('battleship {}'.format(ShipsList.ships[1]))))
        ShipsList.ships_list.append(urwid.Button(('cruiser {}'.format(ShipsList.ships[2]))))
        ShipsList.ships_list.append(urwid.Button(('destroyer {}'.format(ShipsList.ships[3]))))
        ShipsList.ships_list.append(urwid.Button(('submarine {}'.format(ShipsList.ships[4]))))
        ShipsList.info_pile = urwid.Pile(ShipsList.ships_list)


class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with North, South, West and East buttons """
    signals = ['close']

    def __init__(self):
        self.h_button = urwid.Button("Horizontal")
        v_button = urwid.Button("Vertical")

        urwid.connect_signal(self.h_button, 'click',
                             lambda button: self._emit("close"))
        direction_pile = urwid.LineBox(urwid.Pile([urwid.Columns([self.h_button, v_button], 2)]), 'Direction')
        ships_pile = urwid.LineBox(ShipsList.info_pile, 'Ships')
        pile = urwid.Pile([direction_pile, ships_pile])
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
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 8}


class Join:
    def __init__(self):
        self.field_offset = 10
        ShipsList.get_ships()
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

            urwid.Columns([
                ship_pile,
                urwid.LineBox(ShipsList.info_pile, 'Available Ships')
            ], 2),
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
