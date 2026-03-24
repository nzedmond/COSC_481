"""
Persists per-level best score, best completion %, and attempt count.

Save file location: saves/progress.json  (relative to cwd, i.e. the
geometry_snake/ directory).  Created automatically on first save.
"""

import json
import os

_SAVE_PATH = "saves/progress.json"


class SaveManager:
    def __init__(self):
        self._data: dict = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_best(self, level_name: str) -> tuple:
        """Return (best_score, best_pct, attempts) for *level_name*."""
        entry = self._data.get(level_name, {})
        return (
            entry.get("best_score", 0),
            entry.get("best_pct",   0.0),
            entry.get("attempts",   0),
        )

    def update(self, level_name: str, score: int, pct: float) -> bool:
        """
        Record a run.  Returns True if either score or pct is a new best.
        *pct* should be in [0, 1].
        """
        entry = self._data.get(level_name, {
            "best_score": 0,
            "best_pct":   0.0,
            "attempts":   0,
        })

        new_best = False
        entry["attempts"] += 1
        if score > entry["best_score"]:
            entry["best_score"] = score
            new_best = True
        if pct > entry["best_pct"]:
            entry["best_pct"] = round(pct, 4)
            new_best = True

        self._data[level_name] = entry
        self._persist()
        return new_best

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(_SAVE_PATH):
            try:
                with open(_SAVE_PATH, "r") as fh:
                    self._data = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _persist(self):
        os.makedirs(os.path.dirname(_SAVE_PATH), exist_ok=True)
        with open(_SAVE_PATH, "w") as fh:
            json.dump(self._data, fh, indent=2)
