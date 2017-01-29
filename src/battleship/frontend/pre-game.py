import urwid


class ShowMessages:
    def __init__(self):
        self.reply = urwid.Text("hahahah")
        self.palette = [('I say', 'default,bold', 'default', 'bold')]
        self.ask = urwid.Edit(('I say', ""))

        self.button = urwid.Button('Send')
        self.div = urwid.Divider()
        self.pile = urwid.Pile([self.ask, self.div, self.reply, self.div, self.button])
        self.top = urwid.Filler(self.pile, valign='top')

    def on_write_message(self, edit, new_edit_text):
        self.reply.set_text(('I say', "You: %s" % new_edit_text))

    def exit_on_q(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    def on_enter_clicked(self, key, new_edit_text):
        if key == 'enter':
            raise urwid.ExitMainLoop()
            # self.reply.set_text(('I say', "You: %s" % new_edit_text))

            # urwid.connect_signal(self.ask, 'change', self.on_write_message)
            # urwid.connect_signal(button, 'click', self.on_enter_clicked)
            # self.ask.set_text("")

    def render_messages(self):
        urwid.MainLoop(self.top, self.palette, unhandled_input=self.on_enter_clicked).run()

if __name__ == '__main__':
    s = ShowMessages()
    s.render_messages()
