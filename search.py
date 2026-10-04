"""Greedy Best-First Search and A* written from scratch (heapq is just a priority queue)."""
import heapq, time
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    found: bool
    path: list = field(default_factory=list)
    cost: float = float("inf")
    explored: int = 0            # number of nodes expanded
    order: list = field(default_factory=list)   # expansion order
    time: float = 0.0


def _rebuild(parent, state):
    path = []
    while state is not None:
        path.append(state[0])
        state = parent[state]
    return path[::-1]


def greedy_best_first(cmap, start, goal):
    """f(n) = h(n). A state is (node, CSE-phase)."""
    t0 = time.perf_counter()
    s0 = (start, cmap.start_phase(start))
    frontier, tie = [(cmap.heuristic(start, goal), 0, s0)], 1
    parent, g, seen, closed, order = {s0: None}, {s0: 0}, {s0}, set(), []
    while frontier:
        _, _, state = heapq.heappop(frontier)
        if state in closed:
            continue
        closed.add(state)
        order.append(state[0])
        if state[0] == goal:
            return SearchResult(True, _rebuild(parent, state), g[state], len(order), order,
                                time.perf_counter() - t0)
        for nxt, ph, w in cmap.successors(*state):
            ns = (nxt, ph)
            if ns in seen:
                continue
            seen.add(ns)
            parent[ns] = state
            g[ns] = g[state] + w                       # only used to report the cost
            heapq.heappush(frontier, (cmap.heuristic(nxt, goal), tie, ns))
            tie += 1
    return SearchResult(False, explored=len(order), order=order, time=time.perf_counter() - t0)


def a_star(cmap, start, goal):
    """f(n) = g(n) + h(n). Cheaper paths to an already-seen state replace the old one."""
    t0 = time.perf_counter()
    s0 = (start, cmap.start_phase(start))
    frontier, tie = [(cmap.heuristic(start, goal), 0, s0)], 1
    parent, g, closed, order = {s0: None}, {s0: 0}, set(), []
    while frontier:
        _, _, state = heapq.heappop(frontier)
        if state in closed:
            continue
        closed.add(state)
        order.append(state[0])
        if state[0] == goal:
            return SearchResult(True, _rebuild(parent, state), g[state], len(order), order,
                                time.perf_counter() - t0)
        for nxt, ph, w in cmap.successors(*state):
            ns = (nxt, ph)
            ng = g[state] + w
            if ns not in g or ng < g[ns]:
                g[ns] = ng
                parent[ns] = state
                heapq.heappush(frontier, (ng + cmap.heuristic(nxt, goal), tie, ns))
                tie += 1
    return SearchResult(False, explored=len(order), order=order, time=time.perf_counter() - t0)
