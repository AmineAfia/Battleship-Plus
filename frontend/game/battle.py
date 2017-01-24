import urwid
import urwid.raw_display
import urwid.web_display
from urwid import BoxAdapter
from urwid import SolidFill


def main():

    # construct the shoots labels
    shoots = [(1,1), (2,2), (3,5), (1,2), (2,1), (1,3), (3,1), (1,4)]
    field_offset = 4
    text_button_list = {}

    for x in range(field_offset):
        for y in range(field_offset):
            if (x,y) in shoots:
                text_button_list[(x,y)] = "X"
            else:
                text_button_list[(x,y)] = "."

    def button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')

    blank = urwid.Divider()

    cell = urwid.WidgetWrap(urwid.GridFlow(
             [urwid.AttrWrap(urwid.Button(text_button_list[txt], button_press, txt),
                 'buttn','buttnf') for txt in text_button_list],
             2, 1, 1, 'center'))

    #cell = urwid.GridFlow(
    #        [urwid.AttrWrap(urwid.Button(text_button_list[txt], button_press, txt),
    #            'buttn','buttnf') for txt in text_button_list],
    #        2, 1, 1, 'center')

    #cell = cell.rows((4,))
    #cell.pack(4, focus=False)

    matrix = [
        #urwid.Padding(cell, left=4, right=3, min_width=13),
        cell,
        blank,
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(text_button_list[txt], button_press, txt),
                'buttn','buttnf') for txt in text_button_list],
            2, 1, 1, 'center'),
            left=4, right=3, min_width=13),
        blank,
        urwid.Padding(urwid.GridFlow(
            [urwid.AttrWrap(urwid.Button(text_button_list[txt], button_press, txt),
                'buttn','buttnf') for txt in text_button_list],
            2, 1, 1, 'center'),
            left=4, right=3, min_width=13),
        blank,
    ]

    widget_list = [
        urwid.Columns([
            urwid.Padding(urwid.Text("Opponent field"), left=2, right=0, min_width=20),
            urwid.Pile([ urwid.Text("Your field")]),
            ], 2),
        blank,

        urwid.Columns([
            cell,
            cell,
            #urwid.Pile(
            #    matrix
            #),
            ], 2, focus_column=0, min_width=4),
        blank,
    ]


    header = urwid.AttrWrap(urwid.Text("TEXT FOR HEADER!!"), 'header')
    listbox = urwid.ListBox(urwid.SimpleListWalker(widget_list))
    frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)

    palette = [
        ('hit', 'black', 'light gray', 'bold'),
        ('miss', 'black', 'black', ''),
        ('untouched', 'white', 'black', ''),
        ('body','white','black', 'standout'),
        ('reverse','light gray','black'),
        ('header','white','dark red', 'bold'),
        ('important','dark blue','light gray',('standout','underline')),
        ('editfc','white', 'dark blue', 'bold'),
        ('editbx','light gray', 'dark blue'),
        ('editcp','black','light gray', 'standout'),
        ('bright','dark gray','light gray', ('bold','standout')),
        ('buttn','black','dark cyan'),
        ('buttnf','white','dark blue','bold'),
        ]

    # use appropriate Screen class
    if urwid.web_display.is_web_request():
        screen = urwid.web_display.Screen()
    else:
        screen = urwid.raw_display.Screen()

    def unhandled(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    urwid.MainLoop(frame, palette, screen,
        unhandled_input=unhandled).run()

def setup():
    urwid.web_display.set_preferences("Urwid Tour")
    # try to handle short web requests quickly
    if urwid.web_display.handle_short_request():
        return

    main()

if '__main__'==__name__ or urwid.web_display.is_web_request():
    setup()
