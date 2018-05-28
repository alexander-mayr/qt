#!/usr/bin/env python2
#-*- coding: utf-8 -*-

# NOTE FOR WINDOWS USERS:
# You can download a "exefied" version of this game at:
# http://hi-im.laria.me/progs/tetris_py_exefied.zip
# If a DLL is missing or something like this, write an E-Mail (me@laria.me)
# or leave a comment on this gist.

# Very simple tetris implementation
# 
# Control keys:
#       Down - Drop stone faster
# Left/Right - Move stone
#         Up - Rotate Stone clockwise
#     Escape - Quit game
#          P - Pause game
#     Return - Instant drop
#
# Have fun!

# Copyright (c) 2010 "Laria Carolin Chabowski"<me@laria.me>
# 
# Permission is hereby granted, <ee of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from random import randrange as rand
import pygame, sys
import curses
import numpy as np
import os

import ai

import argparse
import new_app

# The configuration
cell_size =	18
cols =		10
rows =		22
maxfps = 	10

colors = [
(0,   0,   0  ),
(255, 85,  85),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218 ),
(35,  35,  35) # Helper color for background grid
]

# Define the shapes of the single parts

A = 0

tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]


def rotate_clockwise(shape):
	return [ [ shape[y][x]
			for y in range(len(shape)) ]
		for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True

	return False

def remove_row(board, row):
	del board[row]
	return [[0 for i in range(cols)]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [ [ 0 for x in range(cols) ]
			for y in range(rows) ]
	board += [[ 1 for x in range(cols)]]
	return board

class TetrisApp(object):
	def __init__(self, show):
		pygame.init()

		if(show):
			pygame.key.set_repeat(250,25)

		self.width = cell_size*(cols+6)
		self.height = cell_size*rows
		self.rlim = cell_size*cols
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in range(cols)] for y in range(rows)]
		self.show = show

		curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

		self.default_font =  pygame.font.Font(
			pygame.font.get_default_font(), 12)
		
		if(self.show):
			self.screen = pygame.display.set_mode((self.width, self.height))
			pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need
		    	                                         # mouse movement
		        	                                     # events, so we
		            	                                 # block them.
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		self.init_game()
	
	def new_stone(self):
		self.stone = tetris_shapes[rand(len(tetris_shapes))]
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		self.stone_x = int(cols / 2 - len(self.stone[0])/2)
		self.stone_y = 0
		
		if check_collision(self.board,
		                   self.stone,
		                   (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_stone()
		self.level = 1
		self.score = 0
		self.lines = 0
		self.time_run = 0
		pygame.time.set_timer(pygame.USEREVENT+1, 1000)
	
	def disp_msg(self, msg, topleft):
		x,y = topleft
		for line in msg.splitlines():
			self.screen.blit(
				self.default_font.render(
					line,
					False,
					(255,255,255),
					(0,0,0)),
				(x,y))
			y+=14
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line, False,
				(255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pygame.draw.rect(
						self.screen,
						colors[val],
						pygame.Rect(
							(off_x+x) *
							  cell_size,
							(off_y+y) *
							  cell_size, 
							cell_size,
							cell_size),0)
	
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.lines += n
		self.score += linescores[n] * self.level
		if self.lines >= self.level*6:
			self.level += 1
			newdelay = 1000-50*(self.level-1)
			newdelay = 100 if newdelay < 100 else newdelay
			pygame.time.set_timer(pygame.USEREVENT+1, newdelay)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > cols - len(self.stone[0]):
				new_x = cols - len(self.stone[0])
			if not check_collision(self.board,
			                       self.stone,
			                       (new_x, self.stone_y)):
				self.stone_x = new_x

	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()
	
	def drop(self, manual):
		if not self.gameover and not self.paused:
			self.score += 1 if manual else 0
			self.stone_y += 1
			if check_collision(self.board,
			                   self.stone,
			                   (self.stone_x, self.stone_y)):
				self.board = join_matrixes(
				  self.board,
				  self.stone,
				  (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(
							  self.board, i)
							cleared_rows += 1
							break
					else:
						break
				self.add_cl_lines(cleared_rows)
				return True
		return False
	
	def insta_drop(self):
		if not self.gameover and not self.paused:
			while(not self.drop(True)):
				pass
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board,
			                       new_stone,
			                       (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False

	def show_state(self, state, old_state, window, reward, turn, score, fps):
		x = ''

		for row_i, row in enumerate(state):
			r = []

			for col_i, e in enumerate(row):
				if(e == 1):
					v = "X"
				elif(e == -1):
					v = "Y"
				else:
					v = " "

				r.append(v)

			x += " ".join(r)
			x += "\n"

		old_state_key = self.ai_agent.get_state_key(old_state)
		reg = self.ai_agent.is_registered(old_state_key)

		if(reg):
			cp = curses.color_pair(1)
		else:
			cp = curses.color_pair(2)

		window.addstr(0, 0, "game #" + str(self.ai_agent.games_played))
		window.addstr(1, 0, "turn #" + str(turn))
		window.addstr(2, 0, "reward: " + str(reward))
		window.addstr(3, 0, "score: " + str(score))
		window.addstr(4, 0, "fps: " + str(fps))
		window.addstr(5, 0, x, cp)
		window.refresh()

	def get_state(self):
		state = np.array(self.board)

		for i, row in enumerate(state):
			state[i][np.where(row != 0)] = 1

		for row_i, row in enumerate(self.stone):
			for col_i, e in enumerate(row):
				if e != 0:
					state[row_i + self.stone_y][col_i + self.stone_x] = -1

		return state

	def run(self, ai_agent, window):
		self.ai_agent = ai_agent

		j = 0
		key_actions = {
			'ESCAPE':	self.quit,
			'p':		self.toggle_pause
		}
		
		self.gameover = False
		self.paused = False

		dont_burn_my_cpu = pygame.time.Clock()
		myclock = pygame.time.Clock()

		while 1:
			if(self.show):
				self.screen.fill((0,0,0))

			if self.gameover:
				state = self.get_state()
				return self.score, state, ai_agent.get_state_value(state)
			else:
				if(self.show):
					pygame.draw.line(self.screen, (255,255,255), (self.rlim+1, 0),(self.rlim+1, self.height-1))
					self.disp_msg("Next:", (self.rlim+cell_size, 2))
					self.disp_msg("Score: %d\n\nLevel: %d\\nLines: %d" % (self.score, self.level, self.lines), (self.rlim+cell_size, cell_size*5))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone, (cols+1,2))

					pygame.display.update()

					for event in pygame.event.get():
						if event.type == pygame.USEREVENT+1:
							self.drop(False)
						elif event.type == pygame.QUIT:
							self.quit()
						elif event.type == pygame.KEYDOWN:
							for key in key_actions:
								if event.key == eval("pygame.K_"
								+key):
									key_actions[key]()

			#if not self.paused:

			state = self.get_state
			action, reward = ai_agent.get_action(state)


			if(action == 0):
				self.move(-1)
			elif(action == 1):
				self.move(+1)
			elif(action == 2):
				self.rotate_stone()
			elif(action == 3):
				self.drop(True)
			elif(action == 4):
				self.insta_drop()

			# ai_agent.register(state)

			fps = dont_burn_my_cpu.get_fps()


			new_state = self.get_state()

			state_key = ai_agent.get_state_key(state)
			new_state_key = ai_agent.get_state_key(new_state)

			if(state_key != new_state_key):
				ai_agent.register_experience(state_key)


			self.show_state(new_state, state, window, reward, j, self.score, fps)
			ai_agent.update_q_matrix(new_state, state, action)

			if(self.time_run >= 1000/30 * fps):
				self.drop(False)
				self.time_run = 0

			if(self.show):
				dont_burn_my_cpu.tick(maxfps)
			else:
				self.time_run += myclock.tick()
				dont_burn_my_cpu.tick()
			j = j + 1
