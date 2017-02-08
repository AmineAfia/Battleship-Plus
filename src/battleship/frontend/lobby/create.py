# parameters form (optional password input) and create button for next screen (witting)
import urwid
import traceback

from .join import Join
from common.GameController import GameController
from client.lobby import ClientLobbyController
from common.errorHandler.BattleshipError import BattleshipError

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
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.length = None
        self.carrier = None
        self.battleship = None
        self.cruiser = None
        self.destroyer = None
        self.submarine = None

    def forward_waiting_room(self, foo):
        # TODO: controller doesn't handle empty ships array
        # check the text fields content
        # if int(self.length.get_edit_text()):
        #     self.create_game()
        # else:
            # read the contents of the text fields
        ship_numbers = [int(_) for _ in [self.carrier.get_edit_text(), self.battleship.get_edit_text(),
                                        self.cruiser.get_edit_text(), self.destroyer.get_edit_text(),
                                        self.submarine.get_edit_text()]]
        #    # TODO: handle exception in case user didn't enter numbers into the fields
        #    try:
        #        self.game_controller.create_battlefield(int(self.length.get_edit_text()), ship_numbers)
        #        raise urwid.ExitMainLoop()
        #    except BattleshipError as e:
        #        print("{}".format(e))

        # ship_numbers = [int(_) for _ in [self.carrier.get_edit_text(), self.battleship.get_edit_text(),
        #                                  self.cruiser.get_edit_text(), self.destroyer.get_edit_text(),
        #                                  self.submarine.get_edit_text()]]
        # # TODO: handle exception in case user didn't enter numbers into the fields
        # self.game_controller.create_battlefield(int(self.length.get_edit_text()), ship_numbers)
        # raise urwid.ExitMainLoop()
        create_task = self.loop.create_task(self.game_controller.create_on_server(int(self.length.get_edit_text()), ship_numbers, 25, 0, ""))
        create_task.add_done_callback(self.create_result)

    def create_result(self, future):
        # check if there is an error message to display
        e = future.exception()
        if type(e) is BattleshipError:
            print(e.error_code)
        elif e is not None:
            raise e
        else:
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

        ships = [self.carrier.get_edit_text(), self.battleship.get_edit_text(), self.cruiser.get_edit_text(),
                 self.destroyer.get_edit_text(), self.submarine.get_edit_text()]

        ships_form = urwid.Columns([urwid.Pile([self.length, blank, self.carrier, blank, self.battleship, blank]), urwid.Pile([self.cruiser, blank,
                                    self.destroyer, blank, self.submarine])])

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
                # TODO: the main client needs to know if esc was pressed
                raise urwid.ExitMainLoop()

        urwid.MainLoop(frame, palette,
                       unhandled_input=unhandled,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()
