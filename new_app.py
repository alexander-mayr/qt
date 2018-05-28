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


UNIT_TYPES = [UNIT_TYPE_ONE] # , UNIT_TYPE_TWO, UNIT_TYPE_THREE, UNIT_TYPE_FOUR, UNIT_TYPE_ONE, UNIT_TYPE_TWO, UNIT_TYPE_TWO, UNIT_TYPE_TWO]


class Unit(object):
	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y
		self.last_pos = [self.x, self.y]

	def move(self, dx, dy, rows, cols):
		self.last_pos = [self.x, self.y]

		new_pos = [self.x + dx, self.y + dy]

		if(new_pos == self.last_pos):
			return False

		if(new_pos[0] < 0 or new_pos[0] >= cols or new_pos[1] < 0 or new_pos[1] > rows):
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

		return [[n[0], n[1] + 10] for n in N]

	def expansion(self):
		return [[self.x, self.y]] + self.circle(self.x, self.y, 3) # + self.circle(self.x, self.y , 2)

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
			self.friendly_units.append(Unit(unit_type, 0, 0))
			# self.enemy_units.append(Unit(unit_type, self.cols - 3, (5 * i) + 1))

	def init_board(self):
		self.board = [[EMPTY for j in range(self.cols)] for i in range(self.rows)]

		for i, unit in enumerate(self.friendly_units):
			for i, cell in enumerate(unit.expansion()):
				x = cell[0]
				y = cell[1] 

				if(x > self.cols - 1 or x < 0 or y > self.rows - 1 or y < 0):
					continue

				if(self.board[y][x] == EMPTY):
					self.board[y][x] = FRIENDLY
				elif(self.board[y][x] == ENEMY):
					self.board[y][x] = CONTESTED
				else:
					pass

		for i, unit in enumerate(self.enemy_units):
			for i, cell in enumerate(unit.expansion()):
				x = cell[0]
				y = cell[1]

				if(x > self.cols - 1 or x < 0 or y >= self.rows - 1 or y < 0):
					continue

				try:
					if(self.board[y][x] == EMPTY):
						if(i == 0):
							self.board[y][x] = ENEMY_UNIT
						else:
							self.board[y][x] = ENEMY
					elif(self.board[y][x] == FRIENDLY):
						self.board[y][x] = CONTESTED
					else:
						pass
				except:
					print(x)
					print(y)
					print(len(self.board))
					print(len(self.board[0]))
					raise Exception

	def run(self, ai_agent, window):
		while 1:
			for unit in self.friendly_units + self.enemy_units:
				while not unit.move( np.random.randint(-1, 2),  np.random.randint(-1, 2), self.rows, self.cols): pass
			
				self.init_board()
				self.show_state(window)
				sleep(0.5)

	def show_state(self, window):
		fill = "   "

		c = 3

		for row_i, row in enumerate(self.board):
			for col_i, e in enumerate(row):
				window.addstr(row_i, c * col_i, fill, curses.color_pair(e))

		for unit in self.friendly_units:
			window.addstr(30, 0, str([unit.x, unit.y]))

		window.refresh()
