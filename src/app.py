from __future__ import annotations

import curses
import glob
import json
import locale
import os
from typing import List

from core.models import DIFFICULTIES
from core.models import Settings
from core.models import Stats
from core.stack import StateStack
from states.menu import MenuState


class AppContext:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.normpath(os.path.join(base_dir, "data"))
        self.words_dir = os.path.join(self.data_dir, "words")
        self.settings_path = os.path.join(self.data_dir, "settings.json")
        self.stats_path = os.path.join(self.data_dir, "statistic.json")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.words_dir, exist_ok=True)
        self.categories: List[str] = self._scan_categories()
        self.settings = self._load_settings()
        self.stats = self._load_stats()
        if self.categories:
            if self.settings.category not in self.categories:
                self.settings.category = self.categories[0]
                self.save_settings()

    def _scan_categories(self) -> List[str]:
        paths = glob.glob(os.path.join(self.words_dir, "*.txt"))
        cats = [os.path.splitext(os.path.basename(p))[0] for p in paths]
        cats = [c for c in cats if c] + ["Случайная"]
        cats.sort()
        return cats

    def _load_settings(self) -> Settings:
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            diff = data.get("difficulty", DIFFICULTIES[0])
            cat = data.get("category", "")
            if diff not in DIFFICULTIES:
                diff = DIFFICULTIES[0]
            return Settings(difficulty=diff, category=cat)
        except (FileNotFoundError, json.JSONDecodeError):
            return Settings(difficulty=DIFFICULTIES[0], category=(self.categories[0]))

    def save_settings(self, s: Settings | None = None) -> None:
        s = s or self.settings
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(
                {"difficulty": s.difficulty, "category": s.category},
                f,
                ensure_ascii=False,
                indent=2,
            )

    def _load_stats(self) -> Stats:
        try:
            with open(self.stats_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Stats(
                games_played=int(data.get("games_played", 0)),
                wins=int(data.get("wins", 0)),
                losses=int(data.get("losses", 0)),
                best_streak=int(data.get("best_streak", 0)),
                current_streak=int(data.get("current_streak", 0)),
            )
        except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
            return Stats()

    def save_stats(self, st: Stats | None = None) -> None:
        st = st or self.stats
        with open(self.stats_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "games_played": st.games_played,
                    "wins": st.wins,
                    "losses": st.losses,
                    "best_streak": st.best_streak,
                    "current_streak": st.current_streak,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )


def _init_curses(stdscr):
    locale.setlocale(locale.LC_ALL, "")
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    try:
        curses.meta(True)
    except Exception:
        pass
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 8):
            curses.init_pair(i, i, -1)


def main():
    def _main(stdscr):
        _init_curses(stdscr)
        ctx = AppContext(stdscr)
        stack = StateStack()
        stack.push(MenuState(ctx, stack))
        stack.run_loop(fps=30)

    curses.wrapper(_main)
