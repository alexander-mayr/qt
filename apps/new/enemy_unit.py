from .unit import Unit, MIN_RADIUS
from . import ENEMY_UNIT

class EnemyUnit(Unit):
	def calculate_radius(self, board):
		r = 0

		for p in self.expansion()[1:]:
			if(p[0] != self.x and p[1] != self.y and board.get(p[0], p[1]) == ENEMY_UNIT):
				r = r + 1


		self.expansion_radius = MIN_RADIUS[self.type] + r