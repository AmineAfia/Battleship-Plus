import npyscreen, curses
from pyfiglet import Figlet


class MyGrid(npyscreen.GridColTitles):
    # You need to override custom_print_cell to manipulate how
    # a cell is printed. In this example we change the color of the
    # text depending on the string value of cell.
    def custom_print_cell(self, actual_cell, cell_display_value):
        if cell_display_value =='X':
           actual_cell.color = 'DANGER'
        elif cell_display_value == '.':
           actual_cell.color = 'DEFAULT'
        else:
           actual_cell.color = 'DEFAULT'

class TestApp(npyscreen.NPSApp):

    def main(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F = npyscreen.FormMultiPageActionWithMenus(name = "Battleship+",)

    # First Page
        wlcm = Figlet(font='big')
        welcome= F.add(npyscreen.MultiLineEdit, value = wlcm.renderText('Battleship+'))

        new_page = F.add_page()

    # Second Page
        # Games list
        games = F.add(npyscreen.MultiLine, name = "Games", values = ["game 1", "game 2", "Game 2"])

        # t = F.add(npyscreen.TitleText, name = "Text:",)
        # fn = F.add(npyscreen.TitleFilename, name = "Filename:")
        # dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
        # s = F.add(npyscreen.TitleSlider, out_of=12, name = "Slider")

    # Third Page
        new_page = F.add_page()

        gd = F.add(MyGrid, col_margin = 0, column_width = 3)

        # Adding values to the Grid, for each (x,y)
        # check the positions array and append charachter according to it
        fieldSize = 10
        gd.values = []
        positions = [(1,1), (2,2), (3,3), (4,4)]

        for x in range(fieldSize):
            row = []
            for y in range(fieldSize):
                if (x,y) in positions:
                    row.append("X")
                else:
                    row.append(".")
            gd.values.append(row)

        F.switch_page(0)

        def shoot(x, y):
            positions.append((x,y))

        def on_ok():
            npyscreen.notify_confirm("You are sure to quit the game?")
        F.on_ok = on_ok
        # This lets the user play with the Form.
        F.edit()


if __name__ == "__main__":
    App = TestApp()
    App.run()
