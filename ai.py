import numpy as np

from time import sleep
from pprint import pprint

import pickle
import os
import hashlib

import zlib
import json_tricks
import curses

class AI():
	def __init__(self, name = None, num_actions = 5):
		self.name = name
		self.num_actions = num_actions

		if(self.name and self.knowledge_file and os.path.exists(self.knowledge_file) and os.path.getsize(self.knowledge_file) > 0):
			with open(self.knowledge_file, "rb") as file:
				print("Loading ", self.knowledge_file)
				data = json_tricks.loads(file.read(), decompression = True)
				self.q_matrix = data["q_matrix"]
				self.games_played = int(data["games_played"])

				print("Loaded " + str(len(self.q_matrix.keys())) + " memories over " + str(self.games_played) + " games.")
		else:
			self.games_played = 0
			self.q_matrix = dict()


	def run(self, app, window):
		score, state, board_value = app.run(self, window)

	def get_state_actions(self, state):
		state_key = self.get_state_key(state)

		try:
			actions = self.q_matrix[state_key]["actions"]
		except KeyError:
			self.initialize_state(state_key)
			actions = self.q_matrix[state_key]["actions"]

		return actions


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
			content = {"games_played": self.games_played, "q_matrix": self.q_matrix, }
			file.write(json_tricks.dumps(content, compression = True))

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
		self.q_matrix[state_key] = { "experienced": 0, "actions": [np.random.randint(10) for i in range(self.num_actions)] }
		return self.q_matrix[state_key]

	def register_experience(self, state_key):
		v = int(self.q_matrix[state_key]["experienced"])
		self.q_matrix[state_key]["experienced"]= v + 1


	def is_registered(self, state_key):
		return self.q_matrix[state_key]["experienced"] > 0


	def get_state_key(self, state):
		return str(state)

	def update_entry(self, state, action, value):
		state_key = self.get_state_key(state)
		self.q_matrix[state_key]["actions"][action] = value

	def update_q_matrix(self, new_state, old_state, action_taken):
		old_state_actions = self.get_state_actions(old_state)
		new_state_actions = self.get_state_actions(new_state)

		old_value = old_state_actions[action_taken]

		reward = self.calculate_reward(new_state, old_state, old_value)
		next_action, next_reward = self.get_best_action(new_state_actions)

		new_value = (1 - 0.2) * old_value + 0.2 * (reward + 0.8 * next_reward)

		self.update_entry(old_state, action_taken, new_value)

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
