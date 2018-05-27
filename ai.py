import numpy as np

from time import sleep
from pprint import pprint

import pickle
import os
import hashlib

import zlib
import json_tricks
import curses

from defaultlist import defaultlist

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
ENTER = 4

ACTIONS = ["LEFT", "RIGHT", "UP", "DOWN", "ENTER"]

class AI():
	def __init__(self, name = None):
		self.name = name
		self.knowledge_file = name + ".gz"

		self.experience_matrix = defaultlist(factory = lambda: 0)

		if(self.knowledge_file and os.path.exists(self.knowledge_file) and os.path.getsize(self.knowledge_file) > 0):
			with open(self.knowledge_file, "rb") as file:
				print("Loading ", self.knowledge_file)
				data = json_tricks.loads(file.read(), decompression = True)
				self.q_matrix = data["q_matrix"]
				self.games_played = int(data["games_played"])
				loaded_em = data["experience_matrix"]
				self.experience_matrix = [e for i, e in enumerate(loaded_em)]

				print("Loaded " + str(len(self.q_matrix.keys())) + " memories over " + str(sum(self.experience_matrix)) + " experiences in " + str(self.games_played) + " games.")
		else:
			self.games_played = 0
			self.q_matrix = dict()


	def get_state_actions(self, state):
		state_key = self.get_state_key(state)

		if(state_key not in self.q_matrix.keys()):
			self.initialize_state(state_key)

		return self.q_matrix[state_key]

	def get_action(self, state):
		actions = self.get_state_actions(state)

		if(np.random.randint(10) == 0):
			action = np.random.randint(4)
			reward = actions[action]
		else:
			action, reward = self.get_best_action(actions)

		return action, reward

	def get_best_action(self, actions):
		best_action = np.argmax(actions)
		reward = actions[best_action]

		return best_action, reward

	def save_knowledge(self):
		with open(self.knowledge_file, "wb") as file:
			content = {"games_played": self.games_played, "q_matrix": self.q_matrix, "experience_matrix": self.experience_matrix }
			file.write(json_tricks.dumps(content, compression = True))

		#np.savez(self.knowledge_file + "_experience.npz", "w", np.array(self.experience_matrix))

	def show_state(self, state, old_state, window, reward, turn, score):
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

		old_state_key = self.get_state_key(old_state)
		reg = self.is_registered(old_state_key)

		if(reg):
			cp = curses.color_pair(1)
		else:
			cp = curses.color_pair(2)

		window.addstr(0, 0, "game #" + str(self.games_played))
		window.addstr(1, 0, "turn #" + str(turn))
		window.addstr(2, 0, "reward: " + str(reward))
		window.addstr(3, 0, "score: " + str(score))
		window.addstr(5, 0, x, cp)
		window.refresh()
 
	def print_state(self, state, file = None):
		print_state = []

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

			print_state.append(r)

		pprint(print_state, file)


	def initialize_state(self, state_key):
		self.q_matrix[state_key] = [np.random.randint(10) for i in range(5)]
		return self.q_matrix[state_key]

	def register_experience(self, state_key):
		idx = list(self.q_matrix.keys()).index(state_key)
		self.experience_matrix[idx] += 1

	def is_registered(self, state_key):
			idx = list(self.q_matrix.keys()).index(state_key)
		return self.experience_matrix[idx] > 0

	def get_state(self, app):
		state = np.array(app.board)

		for i, row in enumerate(state):
			state[i][np.where(row != 0)] = 1

		for row_i, row in enumerate(app.stone):
			for col_i, e in enumerate(row):
				if e != 0:
					state[row_i + app.stone_y][col_i + app.stone_x] = -1

		return state

	def get_state_key(self, state):
		return str(state)

	def update_entry(self, state, action, value):
		state_key = self.get_state_key(state)
		self.q_matrix[state_key][action] = value

	def update_q_matrix(self, new_state, old_state, action_taken):
		old_state_actions = self.get_state_actions(old_state)
		new_state_actions = self.get_state_actions(new_state)

		old_value = old_state_actions[action_taken]

		reward = self.calculate_reward(new_state, old_state, old_value)
		next_action, next_reward = self.get_best_action(new_state_actions)

		new_value = (1 - 0.2) * old_value + 0.2 * (reward + 0.8 * next_reward)

		self.update_entry(old_state, action_taken, new_value)
		# self.q_matrix[old_state_key][action_taken] = new_value

	def calculate_reward(self, new_state, old_state, old_value):
		new_value = self.get_state_value(new_state)

		return new_value - old_value

	def get_state_value(self, state):
		max_x = state.shape[1] - 1
		max_y = state.shape[0] - 1

		value = 0

		for row_i, row in enumerate(state):
			if(1 in row):
				v = len([x for x in row if x == 1])
				value += v
			else:
				value += 50

		return value # if occupied != 0 else 100
