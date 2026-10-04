"""The two routing agents. Both share the same graph and the same heuristic."""
import time
from search import greedy_best_first, a_star


class Agent:
    name = "AGENT"
    strategy = None

    def __init__(self, cmap):
        self.cmap = cmap

    def solve(self, start, goal, repeats=1):
        """Route from start to goal (node ids). Time = mean over `repeats` runs."""
        res = self.strategy(self.cmap, start, goal)
        if repeats > 1:
            t0 = time.perf_counter()
            for _ in range(repeats):
                self.strategy(self.cmap, start, goal)
            res.time = (time.perf_counter() - t0) / repeats
        return res


class Pathfinder(Agent):
    name = "PATHFINDER"          # Greedy Best-First, f(n) = h(n)
    strategy = staticmethod(greedy_best_first)


class Orbit(Agent):
    name = "ORBIT"               # A*, f(n) = g(n) + h(n)
    strategy = staticmethod(a_star)
