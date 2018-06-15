from collections import defaultdict
import numpy as np

def tree(): return defaultdict(tree)

T = tree()
N = np.array(range(0,10))