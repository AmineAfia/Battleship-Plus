# """this file is meant for testing purposes"""
# import random
# from cgi import log
# from tkinter import S
#
# import npyscreen
#
#
# class MyGrid(npyscreen.GridColTitles):
#     # You need to override custom_print_cell to manipulate how
#     # a cell is printed. In this example we change the color of the
#     # text depending on the string value of cell.
#     def custom_print_cell(self, actual_cell, cell_display_value):
#         if cell_display_value =='FAIL':
#            actual_cell.color = 'DANGER'
#         elif cell_display_value == 'PASS':
#            actual_cell.color = 'GOOD'
#         else:
#            actual_cell.color = 'DEFAULT'
#
# def myFunction(*args):
#     positions = [(2,3)]
#     # positions.append((shoot_x, shoot_y))
#     # making an example Form
#     F = npyscreen.Form(name='Battlesip+')
#     myFW = F.add(npyscreen.TitleText, name = 'positions', value = positions)
#     gd = F.add(MyGrid)
#
#     # Adding values to the Grid, this code just randomly
#     # fills a 2 x 4 grid with random PASS/FAIL strings.
#     fieldSize = 10
#     gd.values = []
#     # , (1,3), (1,1), (2,2)
#
#     for x in range(fieldSize):
#         row = []
#         for y in range(fieldSize):
#             if (x,y) in positions:
#                 row.append("X")
#             else:
#                 row.append(".")
#         gd.values.append(row)
#
#     # F.add(npyscreen.TitleText, name = "Text:", value = positions)
#     F.edit()
#
#     def handle_mouse_event(self, mouse_event):
#         mouse_id, rel_x, rel_y, z, bstate = self.interpret_mouse_event(mouse_event)
#         log.info(rel_x)
#
# if __name__ == '__main__':
#     npyscreen.wrapper_basic(myFunction)

# ------------------------------------------------------------------------------------------------------------
# import urwid
#
# class PopUpDialog(urwid.WidgetWrap):
#     """A dialog that appears with nothing but a close button """
#     signals = ['close']
#     def __init__(self):
#         close_button = urwid.Button("that's pretty cool")
#         urwid.connect_signal(close_button, 'click',
#             lambda button:self._emit("close"))
#         pile = urwid.Pile([urwid.Text(
#             "^^  I'm attached to the widget that opened me. "
#             "Try resizing the window!\n"), close_button])
#         fill = urwid.Filler(pile)
#         self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))
#
#
# class ThingWithAPopUp(urwid.PopUpLauncher):
#     def __init__(self):
#         self.__super.__init__(urwid.Button("click-me"))
#         urwid.connect_signal(self.original_widget, 'click',
#             lambda button: self.open_pop_up())
#
#     def create_pop_up(self):
#         pop_up = PopUpDialog()
#         urwid.connect_signal(pop_up, 'close',
#             lambda button: self.close_pop_up())
#         return pop_up
#
#     def get_pop_up_parameters(self):
#         return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}
#
#
# fill = urwid.Filler(urwid.Padding(ThingWithAPopUp(), 'center', 15))
# loop = urwid.MainLoop(
#     fill,
#     [('popbg', 'white', 'dark blue')],
#     pop_ups=True)
# loop.run()
#-----------------------------

import urwid

import math
import time

UPDATE_INTERVAL = 0.2

def sin100( x ):
    """
    A sin function that returns values between 0 and 100 and repeats
    after x == 100.
    """
    return 50 + 50 * math.sin( x * math.pi / 50 )

class GraphModel:
    """
    A class responsible for storing the data that will be displayed
    on the graph, and keeping track of which mode is enabled.
    """

    data_max_value = 100

    def __init__(self):
        data = [ ('Saw', list(range(0,100,2))*2),
            ('Square', [0]*30 + [100]*30),
            ('Sine 1', [sin100(x) for x in range(100)] ),
            ('Sine 2', [(sin100(x) + sin100(x*2))/2
                for x in range(100)] ),
            ('Sine 3', [(sin100(x) + sin100(x*3))/2
                for x in range(100)] ),
            ]
        self.modes = []
        self.data = {}
        for m, d in data:
            self.modes.append(m)
            self.data[m] = d

    def get_modes(self):
        return self.modes

    def set_mode(self, m):
        self.current_mode = m

    def get_data(self, offset, r):
        """
        Return the data in [offset:offset+r], the maximum value
        for items returned, and the offset at which the data
        repeats.
        """
        l = []
        d = self.data[self.current_mode]
        while r:
            offset = offset % len(d)
            segment = d[offset:offset+r]
            r -= len(segment)
            offset += len(segment)
            l += segment
        return l, self.data_max_value, len(d)


class GraphView(urwid.WidgetWrap):
    """
    A class responsible for providing the application's interface and
    graph display.
    """
    palette = [
        ('body',         'black',      'light gray', 'standout'),
        ('header',       'white',      'dark red',   'bold'),
        ('screen edge',  'light blue', 'dark cyan'),
        ('main shadow',  'dark gray',  'black'),
        ('line',         'black',      'light gray', 'standout'),
        ('bg background','light gray', 'black'),
        ('bg 1',         'black',      'dark blue', 'standout'),
        ('bg 1 smooth',  'dark blue',  'black'),
        ('bg 2',         'black',      'dark cyan', 'standout'),
        ('bg 2 smooth',  'dark cyan',  'black'),
        ('button normal','light gray', 'dark blue', 'standout'),
        ('button select','white',      'dark green'),
        ('line',         'black',      'light gray', 'standout'),
        ('pg normal',    'white',      'black', 'standout'),
        ('pg complete',  'white',      'dark magenta'),
        ('pg smooth',     'dark magenta','black')
        ]

    graph_samples_per_bar = 10
    graph_num_bars = 5
    graph_offset_per_second = 5

    def __init__(self, controller):
        self.controller = controller
        self.started = True
        self.start_time = None
        self.offset = 0
        self.last_offset = None
        urwid.WidgetWrap.__init__(self, self.main_window())

    def get_offset_now(self):
        if self.start_time is None:
            return 0
        if not self.started:
            return self.offset
        tdelta = time.time() - self.start_time
        return int(self.offset + (tdelta*self.graph_offset_per_second))

    def update_graph(self, force_update=False):
        o = self.get_offset_now()
        if o == self.last_offset and not force_update:
            return False
        self.last_offset = o
        gspb = self.graph_samples_per_bar
        r = gspb * self.graph_num_bars
        d, max_value, repeat = self.controller.get_data( o, r )
        l = []
        for n in range(self.graph_num_bars):
            value = sum(d[n*gspb:(n+1)*gspb])/gspb
            # toggle between two bar types
            if n & 1:
                l.append([0,value])
            else:
                l.append([value,0])
        self.graph.set_data(l,max_value)

        # also update progress
        if (o//repeat)&1:
            # show 100% for first half, 0 for second half
            if o%repeat > repeat//2:
                prog = 0
            else:
                prog = 1
        else:
            prog = float(o%repeat) / repeat
        self.animate_progress.set_completion( prog )
        return True

    def on_animate_button(self, button):
        """Toggle started state and button text."""
        if self.started: # stop animation
            button.set_label("Start")
            self.offset = self.get_offset_now()
            self.started = False
            self.controller.stop_animation()
        else:
            button.set_label("Stop")
            self.started = True
            self.start_time = time.time()
            self.controller.animate_graph()


    def on_reset_button(self, w):
        self.offset = 0
        self.start_time = time.time()
        self.update_graph(True)

    def on_mode_button(self, button, state):
        """Notify the controller of a new mode setting."""
        if state:
            # The new mode is the label of the button
            self.controller.set_mode( button.get_label() )
        self.last_offset = None

    def on_mode_change(self, m):
        """Handle external mode change by updating radio buttons."""
        for rb in self.mode_buttons:
            if rb.get_label() == m:
                rb.set_state(True, do_callback=False)
                break
        self.last_offset = None

    def on_unicode_checkbox(self, w, state):
        self.graph = self.bar_graph( state )
        self.graph_wrap._w = self.graph
        self.animate_progress = self.progress_bar( state )
        self.animate_progress_wrap._w = self.animate_progress
        self.update_graph( True )


    def main_shadow(self, w):
        """Wrap a shadow and background around widget w."""
        bg = urwid.AttrWrap(urwid.SolidFill(u"\u2592"), 'screen edge')
        shadow = urwid.AttrWrap(urwid.SolidFill(u" "), 'main shadow')

        bg = urwid.Overlay( shadow, bg,
            ('fixed left', 3), ('fixed right', 1),
            ('fixed top', 2), ('fixed bottom', 1))
        w = urwid.Overlay( w, bg,
            ('fixed left', 2), ('fixed right', 3),
            ('fixed top', 1), ('fixed bottom', 2))
        return w

    def bar_graph(self, smooth=False):
        satt = None
        if smooth:
            satt = {(1,0): 'bg 1 smooth', (2,0): 'bg 2 smooth'}
        w = urwid.BarGraph(['bg background','bg 1','bg 2'], satt=satt)
        return w

    def button(self, t, fn):
        w = urwid.Button(t, fn)
        w = urwid.AttrWrap(w, 'button normal', 'button select')
        return w

    def radio_button(self, g, l, fn):
        w = urwid.RadioButton(g, l, False, on_state_change=fn)
        w = urwid.AttrWrap(w, 'button normal', 'button select')
        return w

    def progress_bar(self, smooth=False):
        if smooth:
            return urwid.ProgressBar('pg normal', 'pg complete',
                0, 1, 'pg smooth')
        else:
            return urwid.ProgressBar('pg normal', 'pg complete',
                0, 1)

    def exit_program(self, w):
        raise urwid.ExitMainLoop()

    def graph_controls(self):
        modes = self.controller.get_modes()
        # setup mode radio buttons
        self.mode_buttons = []
        group = []
        for m in modes:
            rb = self.radio_button( group, m, self.on_mode_button )
            self.mode_buttons.append( rb )
        # setup animate button
        self.animate_button = self.button( "", self.on_animate_button)
        self.on_animate_button( self.animate_button )
        self.offset = 0
        self.animate_progress = self.progress_bar()
        animate_controls = urwid.GridFlow( [
            self.animate_button,
            self.button("Reset", self.on_reset_button),
            ], 9, 2, 0, 'center')

        if urwid.get_encoding_mode() == "utf8":
            unicode_checkbox = urwid.CheckBox(
                "Enable Unicode Graphics",
                on_state_change=self.on_unicode_checkbox)
        else:
            unicode_checkbox = urwid.Text(
                "UTF-8 encoding not detected")

        self.animate_progress_wrap = urwid.WidgetWrap(
            self.animate_progress)

        l = [    urwid.Text("Mode",align="center"),
            ] + self.mode_buttons + [
            urwid.Divider(),
            urwid.Text("Animation",align="center"),
            animate_controls,
            self.animate_progress_wrap,
            urwid.Divider(),
            urwid.LineBox( unicode_checkbox ),
            urwid.Divider(),
            self.button("Quit", self.exit_program ),
            ]
        w = urwid.ListBox(urwid.SimpleListWalker(l))
        return w

    def main_window(self):
        self.graph = self.bar_graph()
        self.graph_wrap = urwid.WidgetWrap( self.graph )
        vline = urwid.AttrWrap( urwid.SolidFill(u'\u2502'), 'line')
        c = self.graph_controls()
        w = urwid.Columns([('weight',2,self.graph_wrap),
            ('fixed',1,vline), c],
            dividechars=1, focus_column=2)
        w = urwid.Padding(w,('fixed left',1),('fixed right',0))
        w = urwid.AttrWrap(w,'body')
        w = urwid.LineBox(w)
        w = urwid.AttrWrap(w,'line')
        w = self.main_shadow(w)
        return w


class GraphController:
    """
    A class responsible for setting up the model and view and running
    the application.
    """
    def __init__(self):
        self.animate_alarm = None
        self.model = GraphModel()
        self.view = GraphView( self )
        # use the first mode as the default
        mode = self.get_modes()[0]
        self.model.set_mode( mode )
        # update the view
        self.view.on_mode_change( mode )
        self.view.update_graph(True)

    def get_modes(self):
        """Allow our view access to the list of modes."""
        return self.model.get_modes()

    def set_mode(self, m):
        """Allow our view to set the mode."""
        rval = self.model.set_mode( m )
        self.view.update_graph(True)
        return rval

    def get_data(self, offset, range):
        """Provide data to our view for the graph."""
        return self.model.get_data( offset, range )


    def main(self):
        self.loop = urwid.MainLoop(self.view, self.view.palette)
        self.loop.run()

    def animate_graph(self, loop=None, user_data=None):
        """update the graph and schedule the next update"""
        self.view.update_graph()
        self.animate_alarm = self.loop.set_alarm_in(
            UPDATE_INTERVAL, self.animate_graph)

    def stop_animation(self):
        """stop animating the graph"""
        if self.animate_alarm:
            self.loop.remove_alarm(self.animate_alarm)
        self.animate_alarm = None


def main():
    GraphController().main()

if '__main__'==__name__:
    main()
