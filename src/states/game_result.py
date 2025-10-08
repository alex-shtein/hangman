from __future__ import annotations

import curses

from core.ui.widgets import ConfirmButtons
from core.ui.widgets import Label


class GameResultState:
    def __init__(
        self,
        ctx,
        stack,
        win: bool,
        word: str,
        hints_used: int,
        attempts_left: int,
        restart_round,
    ):
        self.ctx = ctx
        self.stack = stack
        self.win = win
        self.word = word
        self.hints_used = hints_used
        self.attempts_left = attempts_left
        self.restart_round = restart_round
        self.title = Label("РЕЗУЛЬТАТ РАУНДА", bold=True)
        self.buttons = ConfirmButtons(["Да", "Нет"])

    def on_push(self, stack):
        pass

    def on_pop(self):
        pass

    def handle_input(self, key: int) -> None:
        if key in (curses.KEY_ENTER, 10, 13, "\n"):
            self.stack.pop()
            self.stack.pop()
            self.restart_round()
        elif key in (27, "\x1b") or (isinstance(key, str) and key.lower() == "й"):
            self.stack.pop()
            self.stack.pop()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        stdscr = self.ctx.stdscr
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        tw, _ = self.title.measure(w, h)
        self.title.layout((w - tw) // 2, 1, tw, 1)
        self.title.draw(stdscr)

        lines = [
            f"Итог: {'ПОБЕДА' if self.win else 'ПОРАЖЕНИЕ'}",
            f"Слово: {self.word}",
            f"Подсказок использовано: {self.hints_used}",
            f"Оставшиеся попытки: {self.attempts_left}",
            "",
            "Enter — начать заново   •   Esc/й — в меню",
        ]
        for i, line in enumerate(lines):
            try:
                stdscr.addstr(3 + i, max(0, (w - len(line)) // 2), line)
            except curses.error:
                pass

        stdscr.refresh()

        try:
            key = stdscr.get_wch()
            if key is not None:
                self.handle_input(key)
        except curses.error:
            pass
