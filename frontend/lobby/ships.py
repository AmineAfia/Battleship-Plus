import urwid

s1 = urwid.Button('.', on_press=None, user_data=None)
s2 = urwid.Button('.', on_press=None, user_data=None)
s3 = urwid.Button('X', on_press=None, user_data=None)
s4 = urwid.Button('.', on_press=None, user_data=None)
s5 = urwid.Button('X', on_press=None, user_data=None)

palette = [
    ('hit', 'black', 'light gray', 'bold'),
    ('miss', 'black', 'black', ''),
    ('untouched', 'white', 'black', ''),]


class shipsPositioning():

    field_offset = 5
    shoots = [(1,1), (3,2), (2,5)]
    c = []

    for x in range(field_offset):
        for y in range(field_offset):
            if (x,y) in shoots:
                c.append(urwid.Button('X', on_press=None, user_data=None))
            else:
                c.append(urwid.Button('.', on_press=None, user_data=None))


    field = urwid.GridFlow(c, 20, 0, 0, 'center')

    loop = urwid.MainLoop(field)
    loop.run()

