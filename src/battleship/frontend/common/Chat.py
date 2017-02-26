import urwid
import logging
import re

class Chat:
    def __init__(self, loop, lobby_controller):
        self.loop = loop
        self.lobby_controller = lobby_controller
        self.chat_messages = None
        self.chat_message = None
        self.post_chat_message = None
        self.username = None
        self.message_without_username = None
        self.lobby_controller.ui_chat_recv_callback = self.chat_recv_callback

    def render_chat(self):
        self.chat_messages = urwid.Pile([urwid.Text("Hello!"), urwid.Text("Hey sup"), urwid.Text("join my game")])
        self.chat_message = urwid.Edit("->", edit_text="")
        self.post_chat_message = urwid.Button("Send")
        urwid.connect_signal(self.post_chat_message, 'click', lambda button: self.append_message())

        chat_messages_pile = urwid.LineBox(self.chat_messages, 'Chat')
        chat_message_pile = urwid.LineBox(urwid.Columns([self.chat_message, self.post_chat_message]), '')
        chat_pile = urwid.Pile([chat_messages_pile, chat_message_pile])
        return chat_pile

    def append_message(self):
        if '@' in self.chat_message.get_edit_text():
            self.username = re.search('@(.+?) ', self.chat_message.get_edit_text()).group(1)
            # TODO: fix this double space thingy
            self.message_without_username = self.chat_message.get_edit_text().replace("@{} ".format(self.username), "")
        else:
            self.username = ""
            self.message_without_username = self.chat_message.get_edit_text()

        try:
            self.loop.create_task(self.lobby_controller.send_chat(self.username, self.message_without_username))
            message_to_append = urwid.Text("")
            message_to_append.set_text(self.chat_message.get_edit_text())
            self.chat_messages.contents.append((message_to_append, self.chat_messages.options()))
            self.chat_message.set_edit_text("")
        except Exception as e:
            logging.error(str(e))

    def chat_recv_callback(self, sender, recipient, text):
        message_to_append = urwid.Text("")
        if recipient == "":
            message_to_append.set_text("{}: {}".format(sender, text))
        else:
            message_to_append.set_text("{}: @{} {}".format(sender, recipient, text))

        self.chat_messages.contents.append((message_to_append, self.chat_messages.options()))
