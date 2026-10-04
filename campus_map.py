"""Graph, locations, connections, weights, coordinates, heuristic and the CSE-zone rule."""
import json, math
from dataclasses import dataclass

# Phases of the CSE-zone state machine (part of the search state)
OUTSIDE = "OUTSIDE"      # ordinary campus
AT_LIFT = "AT_LIFT"      # standing in the Lift Area (came from a tower entry or from the CSE zone)
IN_CSE = "IN_CSE"        # inside the CSE zone, must return via the Lift Area


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    x: float
    y: float
    zone: str = None     # "CSE" for CSE-labelled locations
    role: str = None     # "tower_entry" | "lift" | None


class CampusMap:
    def __init__(self, locations, edges, scale):
        self.locations = locations                 # id -> Location
        self.scale = scale
        self.adj = {i: {} for i in locations}      # id -> {neighbour: weight}
        for a, b, w in edges:
            self.adj[a][b] = w
            self.adj[b][a] = w
        self._by_name = {l.name.lower(): i for i, l in locations.items()}
        self._by_name.update({i.lower(): i for i in locations})

    # ---------- loading ----------
    @classmethod
    def from_json(cls, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        locs = {k: Location(k, v["name"], v["x"], v["y"], v.get("zone"), v.get("role"))
                for k, v in data["nodes"].items()}
        edges = []
        for e in data["edges"]:
            if e["from"] not in locs or e["to"] not in locs:
                raise ValueError(f"Edge uses unknown node: {e}")   # no new nodes allowed
            edges.append((e["from"], e["to"], e["weight"]))
        return cls(locs, edges, data["meta"]["scale_m_per_pixel"])

    # ---------- lookup ----------
    def resolve(self, text):
        """Name / id (case-insensitive, also unique prefix or substring) -> node id."""
        t = text.strip().lower()
        if t in self._by_name:
            return self._by_name[t]
        hits = {i for n, i in self._by_name.items() if t and t in n}
        if len(hits) == 1:
            return hits.pop()
        return None

    def name(self, node_id):
        return self.locations[node_id].name

    # ---------- heuristic ----------
    def heuristic(self, node, goal):
        """Estimated remaining cost h(n): straight-line distance in metres."""
        a, b = self.locations[node], self.locations[goal]
        return math.hypot(a.x - b.x, a.y - b.y) * self.scale

    def heuristic_is_admissible(self):
        """Edge-level check: h(u,v) <= w(u,v) for every edge (=> consistent)."""
        return all(self.heuristic(u, v) <= w + 1e-9
                   for u in self.adj for v, w in self.adj[u].items())

    # ---------- CSE-zone rule ----------
    def start_phase(self, node):
        loc = self.locations[node]
        if loc.zone == "CSE":
            return IN_CSE
        if loc.role == "lift":
            return AT_LIFT
        return OUTSIDE

    def successors(self, node, phase):
        """Yield (next_node, next_phase, weight) for every VALID move.

        Entering:  Tower entry -> Lift Area -> CSE locations
        Inside:    only CSE locations (or back to the Lift Area)
        Exiting:   CSE -> Lift Area -> Tower entry -> rest of campus
        """
        cur = self.locations[node]
        for nxt, w in self.adj[node].items():
            nl = self.locations[nxt]
            if nl.role == "lift":
                # Lift Area may only be reached from a tower entry or from the CSE zone
                if cur.role == "tower_entry" or cur.zone == "CSE":
                    yield nxt, AT_LIFT, w
            elif nl.zone == "CSE":
                # CSE locations may only be reached from the Lift Area or other CSE locations
                if cur.role == "lift" or cur.zone == "CSE":
                    yield nxt, IN_CSE, w
            else:
                # ordinary location: not allowed while inside the zone, and the Lift Area
                # may only be left towards a tower entry
                if phase == IN_CSE:
                    continue
                if cur.role == "lift" and nl.role != "tower_entry":
                    continue
                yield nxt, OUTSIDE, w
