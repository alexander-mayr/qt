from . import *

MIN_RADIUS = { UNIT_TYPE_ONE: 1, UNIT_TYPE_TWO: 2, UNIT_TYPE_THREE: 3, UNIT_TYPE_FOUR: 5}


class Unit(object):
	def __init__(self, type, x, y):
		self.type = type
		self.x = x
		self.y = y
		self.expansion_radius = MIN_RADIUS[self.type]


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
	
		for p in self.expansion()[1:]:
			e = board.get(p[0], p[1])

			if(e == self.side):
				raise(Exception(s))
				r += 1

		self.expansion_radius = MIN_RADIUS + r

	def expansion(self):
		L = [[self.x, self.y]]

		for r in range(1, self.expansion_radius):
			L = L + self.circle(self.x, self.y, r)

		return L
