"""
Personalised tour planner.

Pipeline
  1. XGBoost ranker scores every artifact for the visitor (gemcore.features -> models/tour_ranker.json)
  2. Time-budgeted greedy selection: pick artifacts by  utility / (viewing time + extra walking time)
     where the extra walking time is the cheapest-insertion cost of adding the artifact's zone to the tour
  3. Order the zones with nearest-neighbour + 2-opt on the *effort* matrix of the indoor graph
  4. Expand every leg with turn-by-turn directions from gemcore.navigation
  5. If the final schedule overruns the time budget, the lowest-value stop is dropped and steps 3-4 repeat
"""
from __future__ import annotations

import os
from collections import defaultdict

import numpy as np
import pandas as pd
import xgboost as xgb

from .constants import ERAS, INTERESTS, PACE_VIEW_FACTOR, WALK_SPEED_MPS
from .features import artifact_matrix, normalise_visitor, pair_features
from .navigation import MuseumGraph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERA_NAME = {e[0]: e[1] for e in ERAS}
INT_NAME = {i[0]: i[1] for i in INTERESTS}
NAV_MODE = {"full": "scenic", "avoid_stairs": "avoid_stairs", "wheelchair": "step_free"}


class TourPlanner:
    def __init__(self, data_dir: str | None = None, model_path: str | None = None):
        data_dir = data_dir or os.path.join(ROOT, "data")
        self.art = pd.read_csv(os.path.join(data_dir, "artifacts.csv")).fillna({"app_image_asset": "", "image_url": ""})
        self.amat = artifact_matrix(self.art)
        self.graph = MuseumGraph(pd.read_csv(os.path.join(data_dir, "zones.csv")),
                                 pd.read_csv(os.path.join(data_dir, "edges.csv")))
        zone_crowd = self.art.groupby("zone_id")["crowd_level"].mean().to_dict()
        self.graph.set_crowd(zone_crowd)
        self.model = xgb.XGBRanker()
        self.model.load_model(model_path or os.path.join(ROOT, "models", "tour_ranker.json"))
        self.by_zone = {z: g.index.tolist() for z, g in self.art.groupby("zone_id")}

    # ---------------------------------------------------------------- scoring
    def score(self, visitor: dict) -> np.ndarray:
        X = pair_features(visitor, self.art, self.amat)
        return self.model.predict(X[self.model.get_booster().feature_names])

    # ---------------------------------------------------------------- planning
    def _eff(self, a, b, mode, cw):
        return self.graph.effort(a, b, mode, cw) / WALK_SPEED_MPS / 60.0      # minutes

    def _insertion_cost(self, order, start, z, mode, cw):
        seq = [start] + order
        best = np.inf
        for i in range(len(seq)):
            prev = seq[i]
            nxt = seq[i + 1] if i + 1 < len(seq) else None
            c = self._eff(prev, z, mode, cw)
            if nxt is not None:
                c += self._eff(z, nxt, mode, cw) - self._eff(prev, nxt, mode, cw)
            best = min(best, c)
        return best

    def _order(self, zones, start, mode, cw):
        """Open-path TSP heuristic: nearest neighbour then 2-opt."""
        zones = list(dict.fromkeys(z for z in zones if z != start))
        if len(zones) <= 1:
            return zones
        cur, left, path = start, set(zones), []
        while left:
            nxt = min(left, key=lambda z: self._eff(cur, z, mode, cw))
            path.append(nxt)
            left.remove(nxt)
            cur = nxt

        def length(p):
            seq = [start] + p
            return sum(self._eff(seq[i], seq[i + 1], mode, cw) for i in range(len(seq) - 1))

        improved = True
        best = length(path)
        while improved:
            improved = False
            for i in range(len(path) - 1):
                for j in range(i + 1, len(path)):
                    cand = path[:i] + path[i:j + 1][::-1] + path[j + 1:]
                    c = length(cand)
                    if c + 1e-6 < best:
                        path, best, improved = cand, c, True
        return path

    def plan(self, visitor_in: dict, max_stops: int = 40) -> dict:
        v = normalise_visitor(visitor_in)
        if v["start"] not in self.graph.zones:
            v["start"] = "ENTRANCE"
        mode = NAV_MODE[v["mobility"]]
        cw = 0.8 if v["crowd"] == "avoid" else 0.0
        start = v["start"]
        pace_f = PACE_VIEW_FACTOR[v["pace"]]
        budget = v["time_minutes"] * 0.92                     # keep a buffer for rests / photos

        raw = self.score(v)
        # normalised utility 0..1 relative to the visitor's own score distribution
        med, mx = np.median(raw), raw.max()
        util = np.clip((raw - med) / max(mx - med, 1e-6), 0, 1)

        reachable = self.graph._dijkstra(start, mode, cw)[0]
        art = self.art
        cand = [i for i in np.argsort(-raw) if art.at[i, "zone_id"] in reachable][:60]

        chosen, zones_order, used = [], [], 0.0
        remaining = set(cand)
        while remaining and len(chosen) < max_stops:
            best, best_d, best_cost = None, 0.0, 0.0
            for i in remaining:
                if util[i] < 0.22 and len(chosen) >= 3:
                    continue
                z = art.at[i, "zone_id"]
                view = art.at[i, "view_minutes"] * pace_f
                travel = 0.0 if z in zones_order else self._insertion_cost(zones_order, start, z, mode, cw)
                cost = view + travel
                if used + cost > budget:
                    continue
                d = util[i] / max(cost, 0.5)
                if d > best_d:
                    best, best_d, best_cost = i, d, cost
            if best is None:
                break
            chosen.append(best)
            remaining.discard(best)
            z = art.at[best, "zone_id"]
            if z not in zones_order:
                zones_order = self._order(zones_order + [z], start, mode, cw)
            used += best_cost

        if not chosen:       # extremely short visits: at least the single best reachable item
            chosen = [cand[0]]
            zones_order = [art.at[cand[0], "zone_id"]]

        # build + verify schedule, dropping the weakest stop if we overrun
        while True:
            zones_order = self._order(zones_order, start, mode, cw)
            legs, total_travel = [], 0.0
            prev = start
            for z in zones_order:
                r = self.graph.route(prev, z, mode, cw)
                legs.append(r)
                total_travel += r["minutes"]
                prev = z
            zone_items = defaultdict(list)
            for i in chosen:
                zone_items[art.at[i, "zone_id"]].append(i)
            total_view = sum(art.at[i, "view_minutes"] * pace_f for i in chosen)
            if total_travel + total_view <= v["time_minutes"] or len(zones_order) <= 1:
                break
            weakest = min(chosen, key=lambda i: util[i])
            chosen.remove(weakest)
            if not any(art.at[i, "zone_id"] == art.at[weakest, "zone_id"] for i in chosen):
                zones_order.remove(art.at[weakest, "zone_id"])

        stops, clock = [], 0.0
        for z, leg in zip(zones_order, legs):
            clock += leg["minutes"]
            items = sorted(zone_items[z], key=lambda i: -raw[i])
            dwell = sum(art.at[i, "view_minutes"] * pace_f for i in items)
            stops.append(dict(
                zone_id=z, zone_name=self.graph.name(z), floor=self.graph.floor(z),
                x=self.graph.zones[z]["x"], y=self.graph.zones[z]["y"],
                arrive_at_min=round(clock, 1), dwell_min=round(dwell, 1),
                leg=dict(distance_m=leg["distance_m"], minutes=leg["minutes"], steps=leg["steps"],
                         nodes=leg["nodes"], uses_stairs=leg["uses_stairs"]),
                artifacts=[self._artifact_card(i, v, util[i], pace_f) for i in items],
            ))
            clock += dwell
        total_min = round(clock, 1)
        title, subtitle = self._title(v, stops)
        all_cards = [a for s in stops for a in s["artifacts"]]
        brk = None
        if v["time_minutes"] >= 180:
            nz = self.graph.nearest(zones_order[-1], "food", mode)
            if nz:
                brk = dict(zone_id=nz, zone_name=self.graph.name(nz),
                           suggestion="Plan a coffee break here when you need to recharge.")
        return dict(
            title=title, subtitle=subtitle, visitor=v, navigation_mode=mode,
            total_minutes=total_min, time_budget_minutes=v["time_minutes"],
            walking_minutes=round(total_travel, 1), viewing_minutes=round(total_view, 1),
            n_stops=len(stops), n_artifacts=len(all_cards),
            walking_distance_m=round(sum(s["leg"]["distance_m"] for s in stops), 1),
            floors=sorted({s["floor"] for s in stops}),
            stops=stops, suggested_break=brk,
            model=dict(name="XGBRanker(rank:ndcg)", version=1),
        )

    # ---------------------------------------------------------------- helpers
    def _artifact_card(self, i, v, util, pace_f):
        a = self.art.loc[i]
        tags = a["interest_tags"].split(";")
        why = []
        matched = [INT_NAME[t] for t in tags if t in v["interests"]]
        if matched:
            why.append("Matches your interest in " + ", ".join(matched[:2]))
        if a["era_id"] in v["eras"]:
            why.append(f"From your chosen period: {ERA_NAME[a['era_id']]}")
        if a["popularity"] >= 9:
            why.append("One of the museum's must-see masterpieces")
        if v["visitor_type"] == "family_kids" and a["kid_friendly"] >= 0.8:
            why.append("Great for children")
        if not why:
            why.append("Recommended by the AI model to round out your visit")
        return dict(artifact_id=a["artifact_id"], name=a["name"], era=ERA_NAME[a["era_id"]], period=a["period"],
                    category=a["category"], material=a["material"], description=a["description"],
                    minutes=round(float(a["view_minutes"]) * pace_f, 1), match=int(round(float(util) * 100)),
                    why=why, app_image_asset=(a["app_image_asset"] if isinstance(a.get("app_image_asset"), str) else ""))

    def _title(self, v, stops):
        h = v["time_minutes"] / 60.0
        dur = f"{h:g}-hour"
        if v["interests"]:
            main = INT_NAME[v["interests"][0]].split(" & ")[0]
        elif v["eras"]:
            main = ERA_NAME[v["eras"][0]].split(" (")[0]
        else:
            main = "Highlights"
        eras = [ERA_NAME[e].split(" (")[0] for e in v["eras"][:2]]
        title = f"{main} Tour - {dur}"
        sub = ("Focus: " + " & ".join(eras)) if eras else "A balanced journey through the museum"
        return title, sub
