from random import randrange as rand
import pygame, sys
import curses
import numpy as np
import os

import ai

from pprint import pprint
from time import sleep


EMPTY = 1
FRIENDLY = 2
ENEMY = 3
CONTESTED = 4
FRIENDLY_UNIT = 5
ENEMY_UNIT = 6

# 1 unit types
UNIT_TYPE_ONE = 21
UNIT_TYPE_TWO = 22
UNIT_TYPE_THREE = 23
UNIT_TYPE_FOUR = 24


# UNIT_TYPES = [UNIT_TYPE_ONE, UNIT_TYPE_TWO]

UNIT_TYPES = [UNIT_TYPE_ONE , UNIT_TYPE_TWO, UNIT_TYPE_THREE, UNIT_TYPE_FOUR, UNIT_TYPE_ONE, UNIT_TYPE_TWO, UNIT_TYPE_TWO, UNIT_TYPE_TWO]

class Unit(object):
	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y
		self.last_pos = [self.x, self.y]
		self.expansion_radius = 3

	def move(self, dx, dy, rows, cols, board):
		self.last_pos = [self.x, self.y]

		new_pos = [self.x + dx, self.y + dy]

		if(new_pos == self.last_pos):
			return False

		if(new_pos[0] < 0 or new_pos[0] >= rows or new_pos[1] < 0 or new_pos[1] >= cols):
			return False

		if(board[new_pos[0]][new_pos[1]] in [FRIENDLY_UNIT or ENEMY_UNIT]):
			return False

		self.x += dx
		self.y += dy

		return True

	def circle(self, x0, y0, r):
		x, y, p = 0, r, 1-r

		L = []
		L.append((x, y))

		for x in range(int(r)):
			if p < 0:
				p = p + 2 * x + 3
			else:
				y -= 1
				p = p + 2 * x + 3 - 2 * y

			L.append((x, y))

			if x >= y: break

		N = L[:]
		for i in L:
			N.append((i[1], i[0]))

		L = N[:]
		for i in N:
			L.append((-i[0], i[1]))
			L.append((i[0], -i[1]))
			L.append((-i[0], -i[1]))

		N = []
		for i in L:
			N.append((x0+i[0], y0+i[1]))

		Z = [[n[0], n[1]] for n in N]
		Y = []

		for z in Z:
			if(z in Y):
				pass
			else:
				Y.append(z)

		return Y

	def calculate_radius(self, board):
		r = 0
		s = board[self.x][self.y]
		for p in self.expansion()[1:]:
			try:
				if(board[p[0]!= self.x and p[0]][p[1]] == s):
					r += 1
			except:
				continue

		self.expansion_radius = 3 + r

	def expansion(self):
		expansions = []

		for r in range(self.expansion_radius + 1):
			expansions = expansions + self.circle(self.x, self.y, r)
		
		return expansions

class NewApp(object):
	def __init__(self, show):
		self.cell_size = 20
		self.cols =	60
		self.rows = 40
		self.num_units = 6

		pygame.init()

		if(show):
			pygame.key.set_repeat(250,25)

		self.show = show

		curses.init_pair(EMPTY, 231, 231)
		curses.init_pair(FRIENDLY, 24, 24)
		curses.init_pair(FRIENDLY_UNIT, 17, 17)
		curses.init_pair(ENEMY_UNIT, 196, 196)
		curses.init_pair(ENEMY, 203, 203)

		curses.curs_set(0)

		self.init_units()
		self.init_board()

	def init_units(self):
		self.friendly_units = []
		self.enemy_units = []

		for i, unit_type in enumerate(UNIT_TYPES):
			self.friendly_units.append(Unit(unit_type, 5 * i, 5))
			self.enemy_units.append(Unit(unit_type, (5 * i), self.cols - 3))

	def init_board(self):
		self.board = [[EMPTY for j in range(self.cols)] for i in range(self.rows)]

		for i, unit in enumerate(self.friendly_units):
			for j, cell in enumerate(unit.expansion()):
				x = cell[0]
				y = cell[1]

				if(x > self.rows - 1 or x < 0 or y > self.cols - 1 or y < 0):
					continue

				if(j == 0):
					if(self.board[x][y] in [FRIENDLY, ENEMY, EMPTY]):
						self.board[x][y] = FRIENDLY_UNIT
				else:
					if(self.board[x][y] == EMPTY):
						self.board[x][y] = FRIENDLY
					elif(self.board[x][y] == ENEMY):
						self.board[x][y] = CONTESTED

		for i, unit in enumerate(self.enemy_units):
			for j, cell in enumerate(unit.expansion()):
				x = cell[0]
				y = cell[1]

				if(x > self.rows - 1 or x < 0 or y > self.cols - 1 or y < 0):
					continue

				if(j == 0):
					if(self.board[x][y] in [FRIENDLY, ENEMY, EMPTY]):
						self.board[x][y] = ENEMY_UNIT
				else:
					if(self.board[x][y] == EMPTY):
						self.board[x][y] = ENEMY
					elif(self.board[x][y] == FRIENDLY):
						self.board[x][y] = CONTESTED

	def run(self, ai_agent, window):
		self.init_board()

		while 1:
			for unit in self.friendly_units + self.enemy_units:
				while not unit.move( np.random.randint(-1, 2),  np.random.randint(-1, 2), self.rows, self.cols, self.board): pass

				self.init_board()
				unit.calculate_radius(self.board)
				self.show_state(window)

	def show_state(self, window):
		fill = "   "
		c = 3

		for row_i, row in enumerate(self.board):
			for col_i, e in enumerate(row):
				window.addstr(row_i, c * col_i, fill, curses.color_pair(e))

		for i, unit in enumerate(self.friendly_units + self.enemy_units):
			window.addstr(i, 0, str([unit.x, unit.y]) + " " + str(unit.expansion_radius))

		window.refresh()
