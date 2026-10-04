# AI Campus Route Navigator (Assignment X_03)

Two routing agents on a weighted graph of the CU Technology Campus:

* **PATHFINDER** - Greedy Best-First Search, `f(n) = h(n)`
* **ORBIT** - A* Search, `f(n) = g(n) + h(n)`

Both use the same graph, the same heuristic and the same CSE-zone rule. No pathfinding library is used (`heapq` is only the priority queue).

## Files
| File | Responsibility |
|---|---|
| `campus.json` | The graph: 21 nodes (map locations only), 37 weighted edges, coordinates, CSE zone / role tags |
| `campus_map.py` | `CampusMap` (loads JSON), heuristic, **CSE-zone rule** in `successors()` |
| `search.py` | `greedy_best_first()` and `a_star()` written from scratch |
| `agents.py` | `Pathfinder` and `Orbit` classes |
| `experiment.py` | Runs 16 source/destination problems and writes `results.csv` |
| `main.py` | User interface (`python main.py`) and experiment runner (`python main.py --experiment`) |
| `results.csv` | Experiment output (Route, Agent, Path, Cost, Nodes Explored, Time, ...) |

Run: `python main.py` (interactive) or `python main.py --experiment`. Python 3.8+, standard library only.

## Graph
* **Nodes** are only the labels on the satellite map. The four gate markers are named by their marker: `Entry Gate 1 (G1)`, `Entry Gate 2 (G2)`, `Entry Gate 2 (G3)`, `Entry Gate 2 (G4)` (the map labels three of them "Entry Gate 2").
* **Coordinates** are pixel positions read from the map (`scale_m_per_pixel = 0.4`).
* **Edge weights** are approximate walking metres: straight-line distance x a detour factor (1.1 - 1.4, for curved paths), rounded up. These are my estimates of the layout; edit `campus.json` to change them, no code changes needed.
* **Heuristic** `h(n)` = straight-line distance to the destination (from coordinates). Because every edge weight >= straight-line distance, `h` is admissible and consistent (checked at start-up by `heuristic_is_admissible()`), so A* is guaranteed optimal.

## CSE-zone rule (how it is implemented)
The search state is `(location, phase)` with phase `OUTSIDE`, `AT_LIFT` or `IN_CSE`. `CampusMap.successors()` only yields valid moves:
* Lift Area can be entered only from a Tower 2 entry or a CSE location, and left only towards a Tower 2 entry or CSE location.
* A CSE location can be entered only from the Lift Area or another CSE location.
* While `IN_CSE`, ordinary locations are never generated.

To prove the rule is enforced in code and not by the graph shape, `campus.json` deliberately contains two physical shortcuts, `Library - Lift Area` and `Garden Area - CSE Laboratory`; the rule blocks both (the invalid route `Lift -> CSE Lab -> Garden -> Library` can never be produced). I checked every CSE-related path in `results.csv` against the rule and checked A* costs against an independent Dijkstra on the same constrained states.

Note: because a Tower 2 entry -> Lift Area -> other Tower 2 entry walk breaks no rule, it acts as a pass-through of the tower building (PATHFINDER uses it for Reception -> Library).

## Results (from `results.csv`, 16 problems; time = mean of 200 runs)
| Metric | PATHFINDER | ORBIT |
|---|---|---|
| Average cost | 261.9 m | 249.1 m |
| Optimal on | 9 / 16 problems | 16 / 16 |
| Avg. nodes explored | 6.0 | 9.25 |
| Avg. time | 0.0000249 s | 0.0000383 s |

The agents chose different routes on 8 of the 16 problems. Selected examples:

| Problem | PATHFINDER | ORBIT |
|---|---|---|
| Reception -> Library | 348 m, 6 explored (via CRNN, Tower 2 Front, Lift, Tower 2 Rear) | 293 m, 12 explored (via Canteen, Auditorium, Garden) |
| Playground -> Entry Gate 2 (G2) | 452 m, 7 explored | 401 m, 14 explored |
| Entry Gate 1 -> CSE Laboratory | 408 m, 8 explored | 363 m, 15 explored |
| Library -> CSE_Reflxon Room | 184 m, 11 explored (direct from Lift) | 177 m, 8 explored (Lift -> AKC -> Reflxon) |

## Observations
1. **Does Greedy always find the shortest route?** No. It was optimal on only 9 of 16 problems and up to 55 m (about 19%) longer on Reception -> Library. Greedy commits to whichever node *looks* nearest and never accounts for the distance already walked.
2. **How does A\* use distance travelled?** It ranks nodes by `g + h`, so a node that looks close but was expensive to reach is penalised, and it re-opens a state when a cheaper route to it is found. That is why ORBIT matched the optimal cost on all 16 problems.
3. **When do the agents differ?** When the node that is nearest to the goal in a straight line is reached by a long or indirect path (e.g. Reception -> Library: the straight line points through the Tower 2 side, but the Canteen/Auditorium/Garden road is shorter). When the straight-line choice also lies on the cheapest road (Canteen -> New Building 2, Library -> Canteen, Parking -> Garden), both return identical paths.
4. **Effect of the heuristic.** Greedy depends entirely on `h`, so it explored fewer nodes (avg 6.0 vs 9.25) and was faster, but its quality depends on how well straight lines match real walking routes. A* with the same admissible `h` pays extra exploration (about 54% more nodes, about 54% more time here) for a guaranteed optimal route. So the path that *looks* closest to the destination does **not** always give the best route.
5. **Effect of the CSE constraint.** It removes the shortcuts, so every route to or from a CSE location must go Tower entry -> Lift Area -> CSE (and the reverse). Many CSE problems then have a single sensible corridor and both agents agree (Garden -> CSE Lab, CSE Lab -> Library, AKC -> Canteen). The restriction can still make greedy mislead: for Library -> CSE_Reflxon Room Greedy walked Lift -> Reflxon directly (184 m), whereas A* found the cheaper Lift -> AKC -> Reflxon (177 m), and in this case A* explored fewer nodes (8 vs 11) because greedy wandered inside the small CSE sub-graph. Because only the Lift Area links the zone to the rest of the campus, entering/leaving it is a bottleneck that both agents have to pass through.

Caveat: the graph is small (21 nodes) and weights are estimates, so timings are microseconds and absolute numbers will change if you edit `campus.json`; the trends above come from the recorded runs.

