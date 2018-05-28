from random import randrange as rand
import pygame, sys
import curses
import numpy as np
import os

import ai

from pprint import pprint

COLOR_EMPTY = 1
COLOR_FRIENDLY = 2
COLOR_FRIENDLY_ACTIVE = 3
COLOR_ENEMY = 4

EMPTY = 0
UNIT_TYPE_ONE = 11
UNIT_TYPE_TWO = 12
UNIT_TYPE_THREE = 13
UNIT_TYPE_FOUR = 14

FRIENDLY_UNIT_ONE= 21
FRIENDLY_UNIT_TWO = 22
FRIENDLY_UNIT_THREE = 23
FRIENDLY_UNIT_FOUR = 24

ENEMY_UNIT_ONE = 31
ENEMY_UNIT_TWO = 32
ENEMY_UNIT_THREE = 33
ENEMY_UNIT_FOUR = 34

UNIT_TYPES = [UNIT_TYPE_ONE, UNIT_TYPE_TWO, UNIT_TYPE_THREE, UNIT_TYPE_FOUR]
FRIENDLY_UNITS = [FRIENDLY_UNIT_ONE, FRIENDLY_UNIT_TWO, FRIENDLY_UNIT_THREE, FRIENDLY_UNIT_FOUR]
ENEMY_UNITS = [ENEMY_UNIT_ONE, ENEMY_UNIT_TWO, ENEMY_UNIT_THREE, ENEMY_UNIT_FOUR]

UNIT_LABELS = { EMPTY: " ", ENEMY_UNIT_ONE: "A", ENEMY_UNIT_TWO: "B", ENEMY_UNIT_THREE: "C", ENEMY_UNIT_FOUR: "D",
				FRIENDLY_UNIT_ONE: "A", FRIENDLY_UNIT_TWO: "B", FRIENDLY_UNIT_THREE: "C", FRIENDLY_UNIT_FOUR: "D" }
class Unit(object):
	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y

class NewApp(object):
	def __init__(self, show):
		self.cell_size = 10
		self.cols =	10
		self.rows =	10
		self.num_units = 6

		pygame.init()

		if(show):
			pygame.key.set_repeat(250,25)


		self.show = show

		curses.init_pair(COLOR_EMPTY, curses.COLOR_WHITE, curses.COLOR_WHITE)
		curses.init_pair(COLOR_FRIENDLY, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(COLOR_FRIENDLY_ACTIVE, curses.COLOR_CYAN, curses.COLOR_WHITE)
		curses.init_pair(COLOR_ENEMY, curses.COLOR_WHITE, curses.COLOR_RED)

		self.init_board()

	def init_board(self):
		p = 1
		self.board = [[EMPTY for j in range(self.cols)] for i in range(self.rows)]
		a_x = self.cols - p
		b_x = p

		for i, unit_type in enumerate(UNIT_TYPES):
			unit_a_x = a_x
			unit_a_y = i + 1
			unit_b_x = b_x
			unit_b_y = i + 1

			self.board[unit_a_y][unit_a_x] = FRIENDLY_UNITS[i]
			self.board[unit_b_y][unit_b_x] = ENEMY_UNITS[i]

	def run(self, ai_agent, window):
		while 1:
			self.show_state(window)

	def show_state(self, window):
		for row_i, row in enumerate(self.board):
			for col_i, e in enumerate(row):
				if(e in FRIENDLY_UNITS):
					cp = curses.color_pair(COLOR_FRIENDLY)
				elif(e in ENEMY_UNITS):
					cp = curses.color_pair(COLOR_ENEMY)
				else:
					cp = curses.color_pair(COLOR_EMPTY)

				window.addstr(row_i, col_i, u'\u4e00', cp)

		window.refresh()
