
from random import randrange as rand
import pygame, sys
import curses
import numpy as np
import os

import ai

import argparse
import new_app
import tetris_app


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", help = "name", dest = "name")
	parser.add_argument("-g", help = "game", dest = "game")

	args = parser.parse_args()
	ai_agent = ai.AI(args.name)
	i = 0
	window = curses.initscr()
	curses.start_color()

	if("SHOW" in os.environ.keys()):
		show = True
	else:
		show = False

	while(True):
		if(args.game == "tetris"):
			App = tetris_app.TetrisApp(show)
		elif(args.game == "new"):
			App = new_app.NewApp(show)
		else:
			print("No such game")
			raise Exception("No such game")

		ai_agent.run(App, window)
