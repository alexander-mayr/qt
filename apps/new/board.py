from .app import *

class Board():
	def __init__(self, rows, cols):
		self.rows = rows
		self.cols = cols
		self.init_empty_table()

	def get(self, x, y):
		if(x not in range(self.cols) or y not in range(self.rows)):
			return None
		else:
			return self.table[y][x]

	def init_empty_table(self):
		self.table = [[EMPTY for j in range(self.cols)] for i in range(self.rows)]

	def build_table(self, friendly_units, enemy_units):
		self.init_empty_table()

		for i, unit in enumerate(friendly_units):
			for j, cell in enumerate(unit.expansion()):
				y = cell[1]
				x = cell[0]

				if(not x in range(self.cols) or not y in range(self.rows)):
					continue

				if(j == 0):
					if(self.table[y][x] in [FRIENDLY, ENEMY, EMPTY]):
						self.table[y][x] = FRIENDLY_UNIT
				else:
					if(self.table[y][x] == EMPTY):
						self.table[y][x] = FRIENDLY
					elif(self.table[y][x] == ENEMY):
						self.table[y][x] = CONTESTED

		for i, unit in enumerate(enemy_units):
			for j, cell in enumerate(unit.expansion()):
				y = cell[1]
				x = cell[0]

				if(not x in range(self.cols) or not y in range(self.rows)):
					continue

				if(j == 0):
					if(self.table[y][x] in [FRIENDLY, ENEMY, EMPTY]):
						self.table[y][x] = ENEMY_UNIT
				else:
					if(self.table[y][x] == EMPTY):
						self.table[y][x] = ENEMY
					elif(self.table[y][x] == FRIENDLY):
						self.table[y][x] = CONTESTED

		for y, row in enumerate(self.table):
			for x, e in enumerate(row):
				if(e == EMPTY):
					n = 0

					# if(self.get(x, y + 1) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x, y - 1) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x + 1, y) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x + 1, y + 1) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x + 1, y - 1) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x - 1, y) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x - 1, y + 1) == FRIENDLY):
					# 	n = n + 1

					# if(self.get(x - 1, y - 1) == FRIENDLY):
					# 	n = n + 1

					# if(n >= 4):
					# 	self.table[y][x] = ENEMY

					nb =  [	self.get(x, y + 1),
							self.get(x, y - 1),
							self.get(x + 1, y),
							self.get(x + 1, y + 1),
							self.get(x + 1, y - 1),
							self.get(x - 1, y),
							self.get(x - 1, y + 1),
							self.get(x - 1, y - 1)]

					nb = [n for n in nb if n in [FRIENDLY, ENEMY]]
					u, c = np.unique(nb, return_counts = True)

					if(len(u) > 0):
						amax = np.argmax(c)

						if(c[amax] >= 4):
							self.table[y][x] = u[amax]
					

	def move_unit(self, unit, dx, dy):
		new_x = unit.x + dx
		new_y = unit.y + dy

		if(not new_x in range(self.cols) or not new_y in range(self.rows)):
			return False

		p = self.get(new_x, new_y)
		if(p in [FRIENDLY_UNIT, ENEMY_UNIT]):
			return False

		unit.x = new_x
		unit.y = new_y

		return True

	def draw(self, window):
		for x in range(self.cols):
			for y in range(self.rows):
				e = self.get(x, y)
				window.addstr(y, 3 * x, " " + str(e) + " ", curses.color_pair(e))

	def draw_unit_info(self, window, units):
		for i, unit in enumerate(units):
			window.addstr(i, 0, str([unit.x, unit.y]) + ": " + str(unit.expansion_radius))