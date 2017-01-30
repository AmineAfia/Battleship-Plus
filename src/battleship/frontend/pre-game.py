# import urwid
#
#
# def main():
#     term = urwid.Terminal(None)
#
#     mainframe = urwid.LineBox(
#         urwid.Pile([
#             ('weight', 70, term),
#             ('fixed', 1, urwid.Filler(urwid.Edit('focus test edit: '))),
#         ]),
#     )
#
#     def set_title(widget, title):
#         mainframe.set_title(title)
#
#     def quit(*args, **kwargs):
#         raise urwid.ExitMainLoop()
#
#     def handle_key(key):
#         if key in ('q', 'Q'):
#             quit()
#
#     urwid.connect_signal(term, 'title', set_title)
#     urwid.connect_signal(term, 'closed', quit)
#
#     loop = urwid.MainLoop(
#         mainframe,
#         handle_mouse=False,
#         unhandled_input=handle_key)
#
#     term.main_loop = loop
#     loop.run()
#
# if __name__ == '__main__':
#     main()

# import urwid
#
# def exit_on_q(key):
#     if key in ('q', 'Q'):
#         raise urwid.ExitMainLoop()
#
# class QuestionBox(urwid.Filler):
#     def keypress(self, size, key):
#         if key != 'enter':
#             return super(QuestionBox, self).keypress(size, key)
#         self.original_widget = urwid.Text(
#             u"Nice to meet you,\n%s.\n\nPress Q to exit." %
#             edit.edit_text)
#
# edit = urwid.Edit(u"What is your name?\n")
# fill = QuestionBox(edit)
# loop = urwid.MainLoop(fill, unhandled_input=exit_on_q)
# loop.run()

import urwid

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

class QuestionBox(urwid.Filler):
    def keypress(self, size, key):
        if key != 'enter':
            return super(QuestionBox, self).keypress(size, key)
        self.original_widget = urwid.Text(
            u"Nice to meet you,\n%s.\n\nPress Q to exit." %
            edit.edit_text)

edit = urwid.Edit(u"What is your name?\n")
fill = QuestionBox(edit)
loop = urwid.MainLoop(fill, unhandled_input=exit_on_q)
loop.run()
