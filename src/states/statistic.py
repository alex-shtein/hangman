from __future__ import annotations

import curses

from core.ui.widgets import Label


# StatisticState — экран статистики
class StatisticState:
    def __init__(self, ctx, stack):
        self.ctx = ctx
        self.stack = stack
        self.title = Label("СТАТИСТИКА", bold=True)

    def on_push(self, stack): ...
    def on_pop(self): ...

    def handle_input(self, key: int) -> None:
        if key in (27, "й", "\x1b", "\n", curses.KEY_ENTER, 10, 13):
            self.stack.pop()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        stdscr = self.ctx.stdscr
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Заголовок
        tw, _ = self.title.measure(w, h)
        self.title.layout((w - tw) // 2, 1, tw, 1)
        self.title.draw(stdscr)

        # Актуальные данные статистики из контекста
        s = self.ctx.stats
        lines = [
            f"Сыграно игр: {s.games_played}",
            f"Побед: {s.wins}",
            f"Поражений: {s.losses}",
            f"Лучшая серия: {s.best_streak}",
            f"Текущая серия: {s.current_streak}",
        ]
        for i, line in enumerate(lines):
            try:
                stdscr.addstr(3 + i, max(0, (w - len(line)) // 2), line)
            except curses.error:
                pass

        hint = "Enter / Esc / й — назад"
        try:
            stdscr.addstr(h - 2, max(0, (w - len(hint)) // 2), hint)
        except curses.error:
            pass

        stdscr.refresh()

        try:
            key = stdscr.get_wch()
            if key is not None:
                self.handle_input(key)
        except curses.error:
            pass
