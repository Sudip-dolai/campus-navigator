"""Runs both agents on many source/destination pairs and saves results.csv."""
import csv
from agents import Pathfinder, Orbit

# problems only (no expected answers)
PAIRS = [
    ("Reception", "Library"),
    ("Canteen", "New Building 2"),
    ("Entry Gate 1 (G1)", "CSE Laboratory"),
    ("Auditorium Hall", "CSE_AKC Seminar Hall"),
    ("Library", "Canteen"),
    ("Playground", "Entry Gate 2 (G2)"),
    ("Entry Gate 1 (G1)", "Entry Gate 2 (G4)"),
    ("Power Area", "New Building 1"),
    ("Parking Area", "Garden Area"),
    ("Entry Gate 2 (G3)", "CSE_Reflxon Room"),
    ("CSE Laboratory", "Library"),
    ("CSE_AKC Seminar Hall", "Canteen"),
    ("CSE_Reflxon Room", "CSE_AKC Seminar Hall"),
    ("Library", "CSE_Reflxon Room"),
    ("Garden Area", "CSE Laboratory"),
    ("New Building 2", "Library"),
]
FIELDS = ["Route", "Agent", "Path", "Cost (m)", "Nodes Explored", "Time (s)",
          "Optimal", "Differs from other agent"]


def run_all(cmap, pairs=PAIRS, repeats=200):
    agents = [Pathfinder(cmap), Orbit(cmap)]
    rows = []
    for s_name, d_name in pairs:
        s, d = cmap.resolve(s_name), cmap.resolve(d_name)
        res = {a.name: a.solve(s, d, repeats) for a in agents}
        best = min(r.cost for r in res.values())
        differ = res["PATHFINDER"].path != res["ORBIT"].path
        for a in agents:
            r = res[a.name]
            rows.append({
                "Route": f"{cmap.name(s)} -> {cmap.name(d)}", "Agent": a.name,
                "Path": " -> ".join(cmap.name(n) for n in r.path) if r.found else "NO ROUTE",
                "Cost (m)": r.cost if r.found else "", "Nodes Explored": r.explored,
                "Time (s)": f"{r.time:.6f}",
                # A* with a consistent h is optimal, so its cost is the reference
                "Optimal": "yes" if r.found and r.cost == best and a.name == "ORBIT"
                           else ("yes" if r.found and r.cost == res["ORBIT"].cost else "no"),
                "Differs from other agent": "yes" if differ else "no"})
    return rows


def save_csv(rows, path="results.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def summary(rows):
    out = {}
    for ag in ("PATHFINDER", "ORBIT"):
        rs = [r for r in rows if r["Agent"] == ag]
        out[ag] = {"problems": len(rs),
                   "avg_cost": sum(float(r["Cost (m)"]) for r in rs if r["Cost (m)"] != "") / len(rs),
                   "avg_explored": sum(r["Nodes Explored"] for r in rs) / len(rs),
                   "avg_time": sum(float(r["Time (s)"]) for r in rs) / len(rs),
                   "optimal": sum(r["Optimal"] == "yes" for r in rs)}
    return out
