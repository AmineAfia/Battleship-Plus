# parameters form (optional password input) and create button for next screen (witting)
import urwid
import traceback

from .join import Join
from common.GameController import GameController
from client.lobby import ClientLobbyController
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import GameOptions

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


class RoundTimePopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']

    def __init__(self, popup_launcher, button_with_pop_up):
        self.button_with_pop_up = button_with_pop_up
        self.round_time_choices = []
        self.popup_launcher = popup_launcher
        # buttons list with time rounds
        for i in range(25, 65, 5):
            self.round_time_choices.append(urwid.Button(str(i)))
        # connect each button to set_round_time() method
        for i in self.round_time_choices:
            urwid.connect_signal(i, 'click', lambda button: self.set_round_time(button.get_label()))

        pile = urwid.Pile(self.round_time_choices)
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))

    # set round time
    def set_round_time(self, label):
        # TODO: link label with a controller method
        self.button_with_pop_up.set_label(label)
        self.popup_launcher.set_roundtime(int(label))
        self._emit("close")


class RoundTimeButtonWithAPopUp(urwid.PopUpLauncher):
    def __init__(self):
        self.roundtime = 30
        self.b = urwid.Button("30")
        super().__init__(self.b)
        urwid.connect_signal(self.original_widget, 'click',
                             lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = RoundTimePopUpDialog(self, self.original_widget)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}

    def set_roundtime(self, roundtime):
        self.roundtime = roundtime

    def get_roundtime(self):
        return self.roundtime


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
        self.password = None
        self.round_time = RoundTimeButtonWithAPopUp()
        self.password_checkbox = None

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
        create_task = self.loop.create_task(self.game_controller.create_on_server(
                                                int(self.length.get_edit_text()), ship_numbers, int(self.round_time.get_roundtime()),
                                                GameOptions.PASSWORD if self.password_checkbox.state else 0,
                                                self.password.get_edit_text()))

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
        self.round_time_line = urwid.Columns([urwid.Text("Round time: "), self.round_time])
        self.password = urwid.Edit(caption='password: ', multiline=False, align='left', wrap='space', allow_tab=False)
        self.password_checkbox = urwid.CheckBox("Password")
        print(self.password_checkbox.state)
        self.carrier = urwid.Edit(caption='carrier: ', edit_text='1', multiline=False, align='left', wrap='space', allow_tab=False,)
        self.battleship = urwid.Edit(caption='battleship: ', edit_text='0', multiline=False, align='left', wrap='space', allow_tab=False)
        self.cruiser = urwid.Edit(caption='cruiser: ', edit_text='0', multiline=False, align='left', wrap='space', allow_tab=False)
        self.destroyer = urwid.Edit(caption='destroyer: ', edit_text='0', multiline=False, align='left', wrap='space', allow_tab=False)
        self.submarine = urwid.Edit(caption='submarine: ', edit_text='0', multiline=False, align='left', wrap='space', allow_tab=False)

        ships = [self.carrier.get_edit_text(), self.battleship.get_edit_text(), self.cruiser.get_edit_text(),
                 self.destroyer.get_edit_text(), self.submarine.get_edit_text()]

        # Screen Layout
        game_settings = urwid.LineBox(urwid.Pile([self.length, blank, self.round_time_line, blank, self.password_checkbox, self.password]), 'Game Settings')
        ships_columns = urwid.Columns([urwid.Pile([self.destroyer, blank, self.submarine]), urwid.Pile([self.carrier, blank, self.battleship, blank, self.cruiser])])
        ships_edit_box = urwid.LineBox(ships_columns, 'Ships')
        ships_form = urwid.Columns([game_settings, ships_edit_box])

        widget_list = [
            # urwid.Padding(urwid.Text("Create Game"), left=2, right=0, min_width=20),
            blank,
            ships_form,
            blank,
            urwid.Columns([urwid.LineBox(urwid.Button('Create', on_press=self.forward_waiting_room)), urwid.Text("")])
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
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop), pop_ups=True).run()
