# form with needed parameters for the game

# ships: carrier, battleship, cruiser, destroyer, submarine
import urwid

palette = [('I say', 'default,bold', 'default', 'bold'),]
ask = urwid.Edit(('I say', u"What is your name?\n"))

title = urwid.Text('------------------------------Lobby------------------------------')
carrier = urwid.Edit(('I say', u"carrier: "))
battleship = urwid.Edit(('I say', u"battleship: "))
cruiser = urwid.Edit(('I say', u"cruiser: "))
destroyer = urwid.Edit(('I say', u"destroyer: "))
submarine = urwid.Edit(('I say', u"submarine: "))

reply = urwid.Text(u"")
button = urwid.Button(u'Next >')
div = urwid.Divider()
pile = urwid.Pile([title, carrier, div, battleship, div, cruiser, div, destroyer, div, submarine, div, button])
top = urwid.Filler(pile, valign='top')


def on_ask_change(edit, new_edit_text):
    reply.set_text(('I say', u"Nice to meet you, %s" % new_edit_text))


def on_exit_clicked(button):
    raise urwid.ExitMainLoop()

urwid.connect_signal(carrier, 'change', on_ask_change)
urwid.connect_signal(button, 'click', on_exit_clicked)

urwid.MainLoop(top, palette).run()
