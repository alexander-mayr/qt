import numpy as np

import os
import hashlib
import curses
import redis
import json

class AI():
	def __init__(self, db = 0, name = None, num_actions = 5):
		self.name = name
		self.num_actions = num_actions
		self.redis = redis.Redis(decode_responses=True)
		self.games_played = self.redis.get("games_played")

		self.redis.set("highscore", 0)
		if(self.games_played == None):
			self.games_played = 0
		else:
			self.games_played = int(self.games_played)

	def run(self, app, window):
		score, state, board_value = app.run(self, window)

		self.redis.set("last_score", score)
		self.games_played = self.games_played + 1
		self.redis.set("games_played", self.games_played)

		if(int(self.redis.get("highscore")) < score):
			self.redis.set("highscore", score)

	def get_state_actions(self, state):
		v = self.get_state_actions_dict(state)
		return v["actions"]

	def get_state_actions_dict(self, state):
		state_key = self.get_state_key(state)
		actions_dict = self.redis.get(state_key)

		if(actions_dict == None):
			actions_dict = self.initial_actions_dict()
			self.set_state_actions_dict(state, actions_dict)
		else:
			actions_dict = json.loads(str(actions_dict))

		return actions_dict

	def set_state_actions_dict(self, state, value):
		key = self.get_state_key(state)
		self.redis.set(key, json.dumps(value))

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

	def initial_actions_dict(self):
		return { "experienced": 0, "actions": [np.random.randint(10) for i in range(self.num_actions)] }

	def register_experience(self, state):
		d = self.get_state_actions_dict(state)
		v = int(d["experienced"])
		d["experienced"] = v + 1

		self.set_state_actions_dict(state, d)

	def is_registered(self, state):
		return int(self.get_state_actions_dict(state)["experienced"]) > 0

	def get_state_key(self, state):
		t = "".join(map(str, np.array(state).flatten()))
		return hashlib.sha512(t.encode()).hexdigest()

	def update_entry(self, state, action, value):
		d = self.get_state_actions_dict(state)
		d["actions"][action] = value
		self.set_state_actions_dict(state, d)

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
