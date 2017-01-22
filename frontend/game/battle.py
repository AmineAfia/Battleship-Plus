import urwid

shootings = [(1,1), (2,2), (3,5)]
field = 10
line = []

palette = [
    ('hit', 'black', 'light gray', 'bold'),
    ('miss', 'black', 'black', ''),
    ('untouched', 'white', 'black', ''),]

# construct shooting field
# The GridFlow widget is a flow widget designed for use with Button, CheckBox and RadioButton widgets.
# It renders all the widgets it contains the same width and it arranges them from left to right and top to bottom.

# The GridFlow widget uses Pile, Columns, Padding and Divider widgets to build a display widget that will handle the keyboard input
# and rendering. When the GridFlow widget is resized it regenerates the display widget to accommodate the new space.


#btn = urwid.Button('X', on_press=None, user_data=None)


#grid = urwid.GridFlow(btn, 1, 0, 0, 'center')

header = urwid.Text("Im Header")
footer = urwid.Text("Im Footer")
body = urwid.Text("HELLOOOOOOOO!", )

frame = urwid.Frame(body, header=header)

loop = urwid.MainLoop(frame)
loop.widget = urwid.AttrMap(frame, 'hit')

loop.run()
# construct move field
