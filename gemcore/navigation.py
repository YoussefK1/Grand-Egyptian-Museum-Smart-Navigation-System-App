"""
Indoor navigation for the GEM.

Cost model ("easiest route"): the router minimises *effort*, not just metres.
  effort(edge) = length * (1 + crowd_weight * crowd(zone))      for walking edges
               = length * stairs_penalty                         for stairs
               = length + elevator_wait                          for elevators
Modes
  easiest      : stairs allowed but penalised (default for point-to-point navigation)
  shortest     : pure distance
  scenic       : prefers the Grand Staircase (used by tours - it is part of the experience)
  avoid_stairs : stairs very strongly penalised (visitors who can climb a few steps at most)
  step_free    : stairs are removed from the graph (wheelchair / pushchair users)
"""
from __future__ import annotations

import heapq
import math
import os
from dataclasses import dataclass

import pandas as pd

from .constants import WALK_SPEED_MPS
from .layout import FLOOR_LABELS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

STAIRS_PENALTY = {"easiest": 2.2, "shortest": 1.0, "scenic": 0.6, "avoid_stairs": 8.0}
ELEVATOR_WAIT_M = {"easiest": 14.0, "shortest": 0.0, "step_free": 14.0, "scenic": 60.0, "avoid_stairs": 14.0}
ELEVATOR_WAIT_S = 30.0
STAIRS_SEC_PER_LEVEL = 40.0


@dataclass
class Step:
    kind: str                 # start | walk | stairs | elevator | arrive
    text: str
    from_id: str
    to_id: str
    distance_m: float
    seconds: float
    floor_from: int
    floor_to: int
    turn: str = "straight"

    def to_dict(self):
        return self.__dict__.copy()


class MuseumGraph:
    def __init__(self, zones: pd.DataFrame | None = None, edges: pd.DataFrame | None = None):
        zones = zones if zones is not None else pd.read_csv(os.path.join(DATA, "zones.csv"))
        edges = edges if edges is not None else pd.read_csv(os.path.join(DATA, "edges.csv"))
        self.zones = {r["id"]: r for r in zones.to_dict("records")}
        self.adj: dict[str, list[dict]] = {z: [] for z in self.zones}
        for e in edges.to_dict("records"):
            for a, b in ((e["a"], e["b"]), (e["b"], e["a"])):
                self.adj[a].append(dict(to=b, kind=e["kind"], length=float(e["length_m"]), levels=int(e["levels"])))
        self.crowd: dict[str, float] = {}      # zone_id -> 0..1 (set from artifact popularity)
        self._cache: dict = {}

    # ------------------------------------------------------------------ utilities
    def set_crowd(self, crowd: dict[str, float]):
        self.crowd = dict(crowd)
        self._cache.clear()

    def name(self, zid: str) -> str:
        return self.zones[zid]["name"]

    def floor(self, zid: str) -> int:
        return int(self.zones[zid]["floor"])

    def search(self, query: str, limit: int = 8):
        q = query.strip().lower()
        out = []
        for z in self.zones.values():
            if z["type"] in ("elevator", "stairs") and q not in z["name"].lower():
                continue
            hay = f'{z["name"]} {z["type"]} {z.get("description", "")} {z.get("theme", "")} {z.get("era_group", "")}'.lower()
            if not q:
                score = 1
            elif q in z["name"].lower():
                score = 3
            elif all(tok in hay for tok in q.split()):
                score = 2
            else:
                continue
            out.append((score, z))
        out.sort(key=lambda t: (-t[0], t[1]["name"]))
        return [z for _, z in out[:limit]]

    def _edge_cost(self, e: dict, src: str, mode: str, crowd_weight: float) -> float | None:
        kind = e["kind"]
        if kind == "stairs":
            if mode == "step_free":
                return None
            return e["length"] * STAIRS_PENALTY.get(mode, 1.0)
        if kind == "elevator":
            return e["length"] + ELEVATOR_WAIT_M.get(mode, 0.0)
        c = 1.0 + crowd_weight * max(self.crowd.get(src, 0.0), self.crowd.get(e["to"], 0.0))
        return e["length"] * c

    # ------------------------------------------------------------------ shortest path
    def _dijkstra(self, src: str, mode: str, crowd_weight: float):
        key = (src, mode, round(crowd_weight, 2))
        if key in self._cache:
            return self._cache[key]
        dist = {src: 0.0}
        prev: dict[str, tuple[str, dict]] = {}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, math.inf):
                continue
            for e in self.adj[u]:
                c = self._edge_cost(e, u, mode, crowd_weight)
                if c is None:
                    continue
                nd = d + c
                if nd < dist.get(e["to"], math.inf):
                    dist[e["to"]] = nd
                    prev[e["to"]] = (u, e)
                    heapq.heappush(pq, (nd, e["to"]))
        self._cache[key] = (dist, prev)
        return dist, prev

    def effort(self, a: str, b: str, mode="easiest", crowd_weight=0.0) -> float:
        dist, _ = self._dijkstra(a, mode, crowd_weight)
        return dist.get(b, math.inf)

    def route(self, start: str, goal: str, mode: str = "easiest", crowd_weight: float = 0.0) -> dict:
        if start not in self.zones:
            raise KeyError(f"unknown start '{start}'")
        if goal not in self.zones:
            raise KeyError(f"unknown destination '{goal}'")
        dist, prev = self._dijkstra(start, mode, crowd_weight)
        if goal not in dist:
            return dict(found=False, mode=mode, message="No route found for this mode (e.g. step-free access is not available).")
        nodes, edges = [goal], []
        cur = goal
        while cur != start:
            p, e = prev[cur]
            edges.append((p, cur, e))
            nodes.append(p)
            cur = p
        nodes.reverse()
        edges.reverse()
        steps = self._to_steps(start, goal, edges)
        total_m = sum(s.distance_m for s in steps)
        total_s = sum(s.seconds for s in steps)
        floors = []
        for n in nodes:
            f = self.floor(n)
            if not floors or floors[-1] != f:
                floors.append(f)
        return dict(
            found=True, mode=mode, start=start, goal=goal,
            start_name=self.name(start), goal_name=self.name(goal),
            distance_m=round(total_m, 1), minutes=round(total_s / 60.0, 1),
            floors_visited=floors, uses_stairs=any(e["kind"] == "stairs" for _, _, e in edges),
            nodes=[dict(id=n, name=self.name(n), floor=self.floor(n), x=self.zones[n]["x"], y=self.zones[n]["y"])
                   for n in nodes],
            steps=[s.to_dict() for s in steps],
        )

    # ------------------------------------------------------------------ instructions
    def _heading(self, a: str, b: str):
        za, zb = self.zones[a], self.zones[b]
        return (zb["x"] - za["x"], zb["y"] - za["y"])

    @staticmethod
    def _turn(h1, h2):
        if h1 is None or (h1 == (0, 0)) or (h2 == (0, 0)):
            return "straight"
        cross = h1[0] * h2[1] - h1[1] * h2[0]       # y axis points down on the map
        dot = h1[0] * h2[0] + h1[1] * h2[1]
        ang = math.degrees(math.atan2(cross, dot))
        if abs(ang) < 35:
            return "straight"
        if abs(ang) > 150:
            return "turn around"
        return "right" if ang > 0 else "left"

    def _to_steps(self, start, goal, edges):
        steps = [Step("start", f"Start at {self.name(start)} ({FLOOR_LABELS[self.floor(start)]}).",
                      start, start, 0, 0, self.floor(start), self.floor(start))]
        last_h = None
        i = 0
        while i < len(edges):
            a, b, e = edges[i]
            if e["kind"] == "elevator":
                # merge consecutive elevator segments
                j = i
                total_levels = 0
                while j < len(edges) and edges[j][2]["kind"] == "elevator":
                    total_levels += edges[j][2]["levels"]
                    j += 1
                end = edges[j - 1][1]
                fa, fb = self.floor(a), self.floor(end)
                direction = "up" if fb > fa else "down"
                secs = ELEVATOR_WAIT_S + 6.0 * abs(fb - fa)
                steps.append(Step("elevator",
                                  f"Take the elevator {direction} to {FLOOR_LABELS[fb]} (step-free).",
                                  a, end, 0.0, secs, fa, fb))
                last_h = None
                i = j
                continue
            if e["kind"] == "stairs":
                j = i
                while j < len(edges) and edges[j][2]["kind"] == "stairs":
                    j += 1
                end = edges[j - 1][1]
                fa, fb = self.floor(a), self.floor(end)
                direction = "up" if fb > fa else "down"
                n_levels = abs(fb - fa)
                if self.zones[a].get("name", "").startswith("Grand Staircase") or self.zones[end].get("name", "").startswith("Grand Staircase"):
                    label = "the Grand Staircase"
                else:
                    label = "the stairs"
                dist = sum(edges[k][2]["length"] for k in range(i, j))
                steps.append(Step("stairs",
                                  f"Go {direction} {label} to {self.name(end)} ({n_levels} level{'s' if n_levels != 1 else ''}).",
                                  a, end, dist, STAIRS_SEC_PER_LEVEL * n_levels, fa, fb))
                last_h = None
                i = j
                continue
            h = self._heading(a, b)
            turn = self._turn(last_h, h)
            last_h = h
            verb = {"straight": "Continue straight to", "left": "Turn left toward", "right": "Turn right toward",
                    "turn around": "Turn around and head to"}[turn]
            if turn == "straight" and last_h is not None and steps[-1].kind == "start":
                verb = "Head to"
            if e["kind"] == "outdoor":
                verb += " (outdoors)"
            steps.append(Step("walk", f"{verb} {self.name(b)} (~{int(round(e['length']))} m).",
                              a, b, e["length"], e["length"] / WALK_SPEED_MPS, self.floor(a), self.floor(b), turn))
            i += 1
        steps.append(Step("arrive", f"You have arrived at {self.name(goal)}.", goal, goal, 0, 0,
                          self.floor(goal), self.floor(goal)))
        return steps

    def nearest(self, start: str, zone_type: str, mode="easiest"):
        dist, _ = self._dijkstra(start, mode, 0.0)
        cands = [(dist[z["id"]], z["id"]) for z in self.zones.values() if z["type"] == zone_type and z["id"] in dist]
        return min(cands)[1] if cands else None
