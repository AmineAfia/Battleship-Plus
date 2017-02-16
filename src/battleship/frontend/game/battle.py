import urwid
import urwid.raw_display
import urwid.web_display
from ..common.StaticScreens import Screen
from ..common.Chat import Chat
from .result import Result
from common.GameController import GameController


class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with North, South, West and East buttons """
    signals = ['close']
    def __init__(self):
        n_button = urwid.Button("North")
        s_button = urwid.Button("South")
        w_button = urwid.Button("West")
        e_button = urwid.Button("East")

        urwid.connect_signal(n_button, 'click',
                             lambda button: self._emit("close"))
        pile = urwid.Pile([n_button, urwid.Columns([w_button, e_button], 2), s_button])
        fill = urwid.Filler(pile)
        super().__init__(urwid.AttrWrap(fill, 'popbg'))


class ButtonWithAPopUp(urwid.PopUpLauncher):
    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
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


class ShootingCell(urwid.PopUpLauncher):
    def __init__(self, x_pos, y_pos, game_controller):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.game_controller = game_controller
        super().__init__(urwid.Button("."))
        urwid.connect_signal(self.original_widget, 'click', lambda button: self.shoot(button))

    def shoot(self, button):
        #print("({}, {})".format(self.x_pos, self.y_pos))
        try:
            self.game_controller.shoot(self.x_pos, self.y_pos)
            button.set_label("X")
        except Exception as e:
            # TODO show a clear message of the failed shoot
            print(e)


class Battle:
    def __init__(self, game_controller, lobby_controller, loop):
        self.loop = loop
        self.game_controller = game_controller
        self.lobby_controller = lobby_controller
        self.win = Screen("YOU LOSE").show
        self.p1 = None
        self.p2 = None
        self.cells_dictionary = {}
        self.shoot_button_list = []
        self.chat = Chat(self.loop, self.lobby_controller)

    def unhandled(self, key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def battle_main(self):
        field_offset = self.game_controller.length
        text_button_list = {}

        def foward_result(foo):
            try:
                self.game_controller.abort()
                self.win(foo)
                raise urwid.ExitMainLoop()
            except Exception as e:
                print(e)
            # self.setup()

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

        shooting_line = []
        f = []
        for y_pos in range(field_offset):
            for x_pos in range(field_offset):
                ship_cell = ShootingCell(x_pos, y_pos, self.game_controller)
                shooting_line.append(ship_cell)
                self.shoot_button_list.append(ship_cell)
            ship_zeil = urwid.GridFlow(shooting_line, 1, 1, 0, 'center')
            f.append(ship_zeil)
            shooting_line.clear()


        # Constructing ships field
        ship_button_list = []
        ship_f = []
        for x_pos in range(field_offset):
            for y_pos in range(field_offset):
                ship_cell = ButtonWithAPopUp(x_pos, y_pos)
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
                urwid.LineBox(urwid.Button('Abort', on_press=foward_result)),
            ], 2),
            blank,
            urwid.Columns([
                shooting_pile,
                ship_pile,
                self.chat.render_chat(),
            ], 2),
        ]

        header = urwid.AttrWrap(urwid.Text("Battleship+"), 'header')
        listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
        frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

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
                       unhandled_input=self.unhandled, pop_ups=True,
                       event_loop=urwid.AsyncioEventLoop(loop=self.loop)).run()
