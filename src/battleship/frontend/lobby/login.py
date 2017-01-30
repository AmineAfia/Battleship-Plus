import urwid

from .lobby import Lobby
# from ..common.GameController import GameController

class Login:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.username = urwid.Edit("Username: ")
        self.password = urwid.Edit("Password: ", mask="*")

    def forward_lobby(self, key):
        if key == 'enter':
            creat_game = Lobby(self.game_controller)
            creat_game.lobby_main()
            raise urwid.ExitMainLoop()

    def login_main(self):

        dialog = urwid.Columns([
                    urwid.Text(""),
                    urwid.LineBox(urwid.Pile([self.username, self.password]), 'Login'),
                    urwid.Text("")
                    ], 2)

        f = urwid.Filler(dialog)
        # f.render((1, 1))
        urwid.MainLoop(f, unhandled_input=self.forward_lobby).run()

if '__main__' == __name__:
    l = Login()
    l.login_main()
