
from random import randrange as rand
# import pygame
import sys
import curses
import numpy as np
import os
import argparse

import ai

from apps import new
from apps import tetris

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", help = "name", dest = "name")
	parser.add_argument("-g", help = "game", dest = "game")

	args = parser.parse_args()
	ai_agent = ai.AI(name = args.name)
	i = 0
	window = curses.initscr()
	curses.start_color()

	if("SHOW" in os.environ.keys()):
		show = True
	else:
		show = False

	while(True):
		if(args.game == "tetris"):
			App = tetris.TetrisApp(show)
		elif(args.game == "new"):
			App = new.App(show)
		else:
			print("No such game")
			raise Exception("No such game")

		ai_agent.run(App, window)

		# if(i % 10 == 0):
		# 	ai_agent.save_knowledge_file()
