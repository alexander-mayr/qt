import numpy as np

import os
import hashlib
import curses
import json

import h5py

CHUNKS = 200

from collections import defaultdict
def tree(): return defaultdict(tree)

class AI():
	def __init__(self, db = 0, name = None, num_actions = 5):
		self.name = name
		self.num_actions = num_actions
		self.filename = name + ".hdf5"

		self.file = h5py.File(self.filename)
			
		if(set(self.file.keys()) != set(["q_matrix", "hash_indices", "experience_counts","stats"])):
			self.file.create_dataset("q_matrix", (CHUNKS, num_actions), compression = "gzip", maxshape = (1000 * CHUNKS, num_actions))
			self.file.create_dataset("hash_indices", (CHUNKS,), dtype="S512", compression = "gzip", maxshape = (1000 * CHUNKS,))
			self.file.create_dataset("experience_counts", (CHUNKS,), compression = "gzip", maxshape = (1000 * CHUNKS, ))
			self.file.create_dataset("stats", (1,))

			self.next_index = 0
		else:
			self.next_index = np.where(self.hash_indices.value == b"")[0][0]

		self.q_matrix = self.file["q_matrix"]
		self.hash_indices = self.file["hash_indices"]
		self.experience_counts = self.file["experience_counts"]
		self.games_played = self.file["stats"][0]
		self.T = tree()

	def save_file(self):
		self.file["stats"].write_direct(np.array([self.games_played]))
		self.file.close()
		self.file = h5py.File(self.filename)
		self.q_matrix = self.file["q_matrix"]
		self.hash_indices = self.file["hash_indices"]
		self.experience_counts = self.file["experience_counts"]

		self.games_played = self.file["stats"][0]

	def run(self, app, window):
		score, state, board_value = app.run(self, window)
		self.games_played = self.games_played + 1
		self.save_file()

	def get_state_actions(self, state):
		state_key = self.get_state_key(state)
		new, state_key_idx = self.get_index(state)

		if(new):
			actions = self.initial_actions()
			self.set_state_actions(state, actions)
		else:
			try:
				actions = self.q_matrix[state_key_idx]
			except Exception as e:
				print(state_key_idx)
				print(new)

		return actions

	def resize_datasets(self):
		q = self.hash_indices.shape[0]/CHUNKS
		p = (q + 1) * CHUNKS
		self.hash_indices.resize((p,))
		self.q_matrix.resize((p, self.num_actions))
		self.experience_counts.resize((p,))

	def set_state_actions(self, state, value):
		state_key = self.get_state_key(state)
		n, state_key_idx = self.get_index(state)
		X = self.q_matrix.value
		X[state_key_idx] = value
		self.q_matrix.write_direct(X)

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

	def initial_actions(self):
		return [np.random.randint(10) for i in range(self.num_actions)]

	def get_index(self, state):
		state_key = self.get_state_key(state)
		indices = self.hash_indices.value

		new = False
		L = self.T

		for n in state_key:
			L = L[n]

		if("value" not in L.keys()):
			state_key_idx = -1
		else:
			state_key_idx = L["value"]

		if(state_key_idx == -1):
			if(self.next_index >= self.hash_indices.shape[0]):
				self.resize_datasets()
				indices = self.hash_indices.value

			indices[self.next_index] = np.string_(state_key)
			self.hash_indices.write_direct(indices)
			self.next_index += 1
			new = True
		else:
			state_key_idx = state_key_idx[0]

		return new, state_key_idx

	def register_experience(self, state):
		n, state_key_idx = self.get_index(state)
		X = self.experience_counts.value
		X[state_key_idx] = X[state_key_idx] + 1
		self.experience_counts.write_direct(X)

	def is_registered(self, state):
		n, state_key_idx = self.get_index(state)
		return self.experience_counts[state_key_idx] > 0

	def get_state_key(self, state):
		t = "".join(map(str, np.array(state).flatten()))
		return hashlib.sha512(t.encode()).hexdigest()

	def update_entry(self, state, action, value):
		actions = self.get_state_actions(state)
		actions[action] = value
		self.set_state_actions(state, actions)

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

		return value
