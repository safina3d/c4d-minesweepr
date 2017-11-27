# -*- coding: utf-8 -*-

# Author: safina3d
# Blog: Safina3d.blogspot.com

import os
import math
import c4d
from c4d import gui
from random import randint


class Observable:

    observers = []

    def __init__(self):
        self.changed = False

    def addObserver(self, obs):
        self.observers.append(obs)

    def setChanged(self):
        self.changed = True

    def notifyObservers(self):
        for observer in self.observers:
            observer.notify()
        self.changed = False


class Observer:

    def notify(self):
        self.update()

    def update(self):
        pass


class Helper:

    def __init__(self): pass

    @staticmethod
    def create_2d_list(rows, cols, default_value=None):
        return map(lambda index: [default_value] * cols, xrange(rows))


class Level:
    """
    Percentage of mines
    ex: Easy = 0.1 = 10%

    """
    EASY = 0.1
    MEDIUM = 0.3
    HARD = 0.6


class Square:

    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.mines_around_count = 0
        self.is_bomb = False
        self.is_exploding = False
        self.is_visible = False


class Grid:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = Helper.create_2d_list(rows, cols)
        for i in xrange(rows):
            for j in xrange(cols):
                self.grid[i][j] = Square(i, j)

    def get_square(self, i, j):
        return None if self.is_out_of_bounds(i, j) else self.grid[i][j]

    def place_mines(self, total_mines_count):
        while total_mines_count > 0:
            random_line_index = randint(0, self.rows - 1)
            random_column_index = randint(0, self.cols - 1)
            while self.grid[random_line_index][random_column_index].is_bomb:
                random_line_index = randint(0, self.rows - 1)
                random_column_index = randint(0, self.cols - 1)
            self.grid[random_line_index][random_column_index].is_bomb = True
            total_mines_count -= 1

        # update all boxes mines count
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                self.grid[i][j].mines_around_count = self.get_mines_count_around(i, j)

    def get_mines_count_around(self, i, j):
        count = 0
        for a in xrange(i - 1, i + 2):
            for b in xrange(j - 1, j + 2):
                if -1 < a < self.rows and -1 < b < self.cols and self.get_square(a, b).is_bomb:
                    count += 1
        if self.get_square(i, j).is_bomb:
            count -= 1
        return count

    def is_out_of_bounds(self, i, j):
        return not (0 <= i < self.rows and 0 <= j < self.cols)

    def reveal_square_content(self, i, j, is_user_choice=False):
        if self.is_out_of_bounds(i, j):
            return
        square = self.get_square(i, j)
        if square and not square.is_visible:
            if square.mines_around_count == 0:
                square.is_visible = True
                self.reveal_square_content(i - 1, j)
                self.reveal_square_content(i + 1, j)
                self.reveal_square_content(i, j + 1)
                self.reveal_square_content(i, j - 1)
            else:
                if is_user_choice:
                    square.is_visible = True

    def reval_grid_content(self):
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                self.grid[i][j].mines_around_count = self.get_mines_count_around(i, j)
                self.grid[i][j].is_visible = True

    def only_mines_are_hidden(self):
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                current = self.grid[i][j]
                if not current.is_visible and not current.is_bomb:
                    return False
        return True


class Game(Observable):

    def __init__(self, rows, cols, level):
        Observable.__init__(self)
        self.grid = Grid(rows, cols)
        self.score = 0
        self.can_play = True
        self.is_victory = False
        self.grid.place_mines(1 + int(level * rows * cols))

    def stop_game(self):
        self.can_play = False

    def select_square(self, i, j):
        if self.can_play:
            square = self.grid.get_square(i, j)
            if square:
                if square.is_bomb:
                    square.is_exploding = True
                    self.grid.reval_grid_content()
                    self.stop_game()
                else:
                    self.grid.reveal_square_content(i, j, True)
                    self.score += Game.get_points(square)
                    if self.grid.only_mines_are_hidden():
                        self.grid.reval_grid_content()
                        self.stop_game()
                        self.is_victory = True
                self.setChanged()
                self.notifyObservers()

    def get_square(self, i, j):
        return self.grid.get_square(i, j)

    @staticmethod
    def get_points(case):
        return int(math.pow(2, case.mines_around_count + 1))


class Images:

    PATH = os.path.join(os.path.dirname(__file__), 'img/')
    BOMB = PATH + 'bomb.png'
    EMPTY = PATH + 'empty.png'
    NUMBER = PATH + 'nb%s.png'
    DEFAULT = PATH + 'default.png'
    BOMB_EXPLODE = PATH + 'bomb-exp.png'

    def __init__(self): pass


class MinesweeperGui(gui.GeDialog, Observer):

    TXT_SCORE_ID = 999
    GRP_GRID_ID = 1000

    def __init__(self, rows, cols, level):
        self.rows = rows
        self.cols = cols
        self.level = level
        self.game = Game(self.rows, self.cols, self.level)
        self.button_instance_list = Helper.create_2d_list(self.rows, self.cols)

        self.game.addObserver(self)

    def CreateLayout(self):
        self.SetTitle("Minesweeper 1.0")
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 1, 'Main')
        self.GroupBorderSpace(10, 10, 10, 10)

        # Infos score
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFH_SCALEFIT, 1, 1, 'Infos', 0)
        self.AddStaticText(MinesweeperGui.TXT_SCORE_ID, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 20, 'SCORE : %s' % self.game.score, 0)
        self.GroupEnd()

        # Grid
        self.GroupBegin(MinesweeperGui.GRP_GRID_ID, c4d.BFH_SCALEFIT | c4d.BFH_SCALEFIT, self.cols, self.rows, 'Grid', 0)
        self.GroupSpace(1, 1)
        self.GroupBorderNoTitle(c4d.BORDER_THIN_IN)

        bc = c4d.BaseContainer()
        bc.SetLong(c4d.BITMAPBUTTON_BORDER, c4d.BORDER_NONE)

        index = 0
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                self.button_instance_list[i][j] = self.AddCustomGui(
                    MinesweeperGui.GRP_GRID_ID + index,
                    c4d.CUSTOMGUI_BITMAPBUTTON,
                    '%s %s' % (i, j),
                    c4d.BFH_CENTER | c4d.BFV_CENTER, 0, 0, bc)
                self.button_instance_list[i][j].SetImage(Images.DEFAULT)
                index += 1
        self.GroupEnd()
        self.GroupEnd()
        return True

    def Command(self, id, msg):
        row = (id - MinesweeperGui.GRP_GRID_ID) / self.cols
        column = (id - MinesweeperGui.GRP_GRID_ID) % self.cols
        self.game.select_square(row, column)
        return True

    def update(self):
        self.render()
        self.SetString(MinesweeperGui.TXT_SCORE_ID, 'SCORE : %s' % self.game.score)
        if not self.game.can_play:
            if self.game.is_victory:
                gui.MessageDialog('VICTORY :) \nFinal score %s' % self.game.score)
            else:
                gui.MessageDialog('GAME OVER :( \nFinal score %s' % self.game.score)

    def render(self):
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                current_square = self.game.get_square(i, j)
                button_instance = self.button_instance_list[i][j]
                if button_instance is not None and current_square.is_visible:
                    if current_square.is_bomb:
                        if current_square.is_exploding:
                            button_instance.SetImage(Images.BOMB_EXPLODE)
                        else:
                            button_instance.SetImage(Images.BOMB)
                    else:
                        if current_square.mines_around_count == 0:
                            button_instance.SetImage(Images.EMPTY)
                        else:
                            button_instance.SetImage(Images.NUMBER % current_square.mines_around_count)

                    self.button_instance_list[i][j] = None


if __name__ == '__main__':
    dlg = MinesweeperGui(15, 10, Level.EASY)
    dlg.Open(dlgtype=c4d.DLG_TYPE_ASYNC)
