from __future__ import annotations

import random
import threading
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class SongStats:
    appearances: int = 0
    wins: int = 0

    @property
    def win_rate(self) -> float:
        if self.appearances <= 0:
            return 0.0
        return self.wins / self.appearances


class VotingSystem:
    """Thread-safe, in-memory voting system for songs."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pool: List[str] = []
        self._stats: Dict[str, SongStats] = {}

    # --- Song management ---
    def add_song(self, name: str) -> bool:
        normalized = self._normalize(name)
        if not normalized:
            return False
        with self._lock:
            if normalized in self._pool:
                return False
            self._pool.append(normalized)
            self._stats[normalized] = SongStats()
            return True

    def remove_song(self, name: str) -> bool:
        normalized = self._normalize(name)
        with self._lock:
            if normalized not in self._pool:
                return False
            self._pool.remove(normalized)
            if normalized in self._stats:
                del self._stats[normalized]
            return True

    def list_songs(self) -> List[str]:
        with self._lock:
            return list(self._pool)

    # --- Voting ---
    def choose_pair(self) -> Tuple[str, str]:
        with self._lock:
            if len(self._pool) < 2:
                raise ValueError("Need at least 2 songs to vote")
            # Weighted selection favoring songs with fewer appearances
            max_appearances = max((s.appearances for s in self._stats.values()), default=0)
            names = list(self._pool)
            weights = [max(max_appearances - self._stats[n].appearances + 1, 1) for n in names]
            first = random.choices(names, weights=weights, k=1)[0]
            # Remove first and pick second
            idx = names.index(first)
            names.pop(idx)
            weights.pop(idx)
            second = random.choices(names, weights=weights, k=1)[0]
            return first, second

    def record_vote(self, selected: str, other: str) -> None:
        a = self._normalize(selected)
        b = self._normalize(other)
        if a == b:
            raise ValueError("Songs must be distinct")
        with self._lock:
            if a not in self._stats or b not in self._stats:
                raise KeyError("One or both songs not found in pool")
            # Both observed once
            self._stats[a].appearances += 1
            self._stats[b].appearances += 1
            # Selected wins
            self._stats[a].wins += 1

    # --- Leaderboard ---
    def leaderboard(self) -> List[Tuple[str, SongStats]]:
        with self._lock:
            items = list(self._stats.items())
        # Sort by win rate desc, then wins desc, then appearances asc, then name
        return sorted(
            items,
            key=lambda kv: (
                round(kv[1].win_rate, 6),
                kv[1].wins,
                -kv[1].appearances,
                kv[0],
            ),
            reverse=True,
        )

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip()
