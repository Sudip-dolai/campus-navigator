"""AI Campus Route Navigator - user interface.
   python main.py              interactive mode
   python main.py --experiment run all experiments and write results.csv
"""
import sys
from campus_map import CampusMap
from agents import Pathfinder, Orbit
import experiment

JSON = "campus.json"


def show(cmap, agent, s, d):
    r = agent.solve(s, d, repeats=50)
    print(f"\n{agent.name}")
    if not r.found:
        print("Route: no valid route (CSE rule / disconnected)")
    else:
        print("Route:\n" + " -> ".join(cmap.name(n) for n in r.path))
        print(f"Cost: {r.cost} m")
    print(f"Nodes explored: {r.explored}")
    print(f"Time: {r.time:.6f} s")
    return r


def ask(cmap, prompt):
    while True:
        node = cmap.resolve(input(prompt))
        if node:
            return node
        print("  Unknown location. Choose from:", ", ".join(l.name for l in cmap.locations.values()))


def run_experiments(cmap):
    rows = experiment.run_all(cmap)
    experiment.save_csv(rows)
    for r in rows:
        print(f"{r['Route']:55s} {r['Agent']:10s} cost={r['Cost (m)']:>4} explored={r['Nodes Explored']:>2} "
              f"time={r['Time (s)']}  differs={r['Differs from other agent']}")
    print("\nSummary:", experiment.summary(rows))
    print("Saved results.csv")


def main():
    cmap = CampusMap.from_json(JSON)
    print(f"Loaded {len(cmap.locations)} locations from {JSON}. "
          f"Heuristic admissible/consistent: {cmap.heuristic_is_admissible()}")
    if "--experiment" in sys.argv:
        return run_experiments(cmap)
    print("Locations:", ", ".join(l.name for l in cmap.locations.values()))
    agents = [Pathfinder(cmap), Orbit(cmap)]
    while True:
        s = ask(cmap, "\nEnter starting location: ")
        d = ask(cmap, "Enter destination: ")
        for a in agents:
            show(cmap, a, s, d)
        if input("\nAnother route? (y/n): ").strip().lower() != "y":
            break


if __name__ == "__main__":
    main()
