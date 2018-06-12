# import pygame
import sys, curses, ai
import numpy as np
from time import sleep
from random import randrange as rand

from . import *
from .friendly_unit import FriendlyUnit
from .enemy_unit import EnemyUnit
from .board import Board

NUM_COLS = 60
NUM_ROWS = 40

class App(object):
	def __init__(self, show):
		pygame.init()

		if(show):
			pygame.key.set_repeat(250,25)

		self.show = show

		curses.init_pair(EMPTY, curses.COLOR_BLACK, 231)
		curses.init_pair(FRIENDLY, 231, 24)
		curses.init_pair(FRIENDLY_UNIT, 231, 17)
		curses.init_pair(ENEMY_UNIT, curses.COLOR_BLACK, 196)
		curses.init_pair(ENEMY, curses.COLOR_BLACK, 203)

		curses.curs_set(0)

		self.board = Board(NUM_ROWS, NUM_COLS)
		self.init_units()
		self.build_board()

	def init_units(self):
		self.friendly_units = []
		self.enemy_units = []

		for i, unit_type in enumerate(UNIT_TYPES):
			xa = rand(NUM_COLS/2 - 1)
			ya = rand(NUM_ROWS)

			xb = rand(NUM_COLS/2, NUM_COLS)
			yb = rand(NUM_ROWS)

			self.friendly_units.append(FriendlyUnit(unit_type, xa, ya))
			self.enemy_units.append(FriendlyUnit(unit_type, xb, yb))

	def build_board(self):
		self.board.build_table(self.friendly_units, self.enemy_units)

	def run(self, ai_agent, window):
		while 1:
			self.build_board()
			self.show_state(window)

			for unit in self.friendly_units + self.enemy_units:
				while not self.board.move_unit(unit, np.random.randint(-1, 2), np.random.randint(-1, 2)): pass
				unit.calculate_radius(self.board)

				# sleep(0.01)

	def show_state(self, window):
		self.board.draw(window)
		self.board.draw_unit_info(window, self.friendly_units)
		window.refresh()