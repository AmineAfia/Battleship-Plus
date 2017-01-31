# parameters form (optional password input) and create button for next screen (witting)
import urwid

from .join import Join
from common.GameController import GameController


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


class CreateGame:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.length = None
        self.carrier = None
        self.battleship = None
        self.cruiser = None
        self.destroyer = None
        self.submarine = None

    def forward_waiting_room(self, foo):
        # read the contents of the text fields
        ship_numbers = [int(_) for _ in [self.carrier.get_edit_text(), self.battleship.get_edit_text(),
                                         self.cruiser.get_edit_text(), self.destroyer.get_edit_text(),
                                         self.submarine.get_edit_text()]]
        # TODO: handle exception in case user didn't enter numbers into the fields
        self.game_controller.create_battlefield(int(self.length.get_edit_text()), ship_numbers)
        join_battle = Join(self.game_controller)
        join_battle.join_main()
        raise urwid.ExitMainLoop()

    def create_game(self):
        # The rendered layout
        blank = urwid.Divider()

        # Form fields
        self.length = urwid.Edit(caption='Field size: ', edit_text='10', multiline=False, align='left', wrap='space', allow_tab=False,)
        self.carrier = urwid.Edit(caption='carrier: ', edit_text='1', multiline=False, align='left', wrap='space', allow_tab=False,)
        self.battleship = urwid.Edit(caption='battleship: ', edit_text='1', multiline=False, align='left', wrap='space', allow_tab=False)
        self.cruiser = urwid.Edit(caption='cruiser: ', edit_text='1', multiline=False, align='left', wrap='space', allow_tab=False)
        self.destroyer = urwid.Edit(caption='destroyer: ', edit_text='1', multiline=False, align='left', wrap='space', allow_tab=False)
        self.submarine = urwid.Edit(caption='submarine: ', edit_text='1', multiline=False, align='left', wrap='space', allow_tab=False)

        # TODO: import needed
        """
            Who forwards to whom: welcome->login->lobby->create->join->waiting->battle->result
        """

        ships = [self.carrier.get_edit_text(), self.battleship.get_edit_text(), self.cruiser.get_edit_text(),
                 self.destroyer.get_edit_text(), self.submarine.get_edit_text()]
        # TODO: handle exception in case user didn't enter numbers into the fields
        #self.game_controller.create_battlefield(int(length.get_edit_text()), [int(_) for _ in ships])

        ships_form = urwid.Pile([self.length, blank, self.carrier, blank, self.battleship, blank, self.cruiser, blank,
                                 self.destroyer, blank, self.submarine, urwid.Text(ships)])

        widget_list = [
            # urwid.Padding(urwid.Text("Create Game"), left=2, right=0, min_width=20),
            blank,
            ships_form,
            blank,
            urwid.Button('Create', on_press=self.forward_waiting_room)
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widget_list)), title='Create Game')
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

        # TODO: legnth = 10, ships = [0, 0, 0, 0, 1]
        def set_ships():
            pass

        def unhandled(key):
            if key == 'esc':
                raise urwid.ExitMainLoop()

        urwid.MainLoop(frame, palette,
                       unhandled_input=unhandled).run()


# if '__main__' == __name__:
#     lobby = CreateGame()
#     lobby.create_game()
