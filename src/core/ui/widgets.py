from __future__ import annotations

import curses
from typing import List, Tuple

from .containers import Widget


class Label(Widget):
    def __init__(self, text: str, bold: bool = False):
        super().__init__()
        self.text = text
        self.bold = bold

    def measure(self, max_w: int, max_h: int) -> Tuple[int, int]:
        return (min(len(self.text), max_w), 1)

    def draw(self, stdscr) -> None:
        try:
            if self.bold:
                stdscr.attron(curses.A_BOLD)
            stdscr.addstr(self.y, self.x, self.text[: self.width])
            if self.bold:
                stdscr.attroff(curses.A_BOLD)
        except curses.error:
            pass


class VerticalMenu(Widget):
    def __init__(self, items: List[str], selected: int = 0):
        super().__init__()
        self.items = items
        self.selected = selected

    def measure(self, max_w: int, max_h: int) -> Tuple[int, int]:
        w = min(max((len(i) for i in self.items), default=0), max_w)
        h = min(len(self.items), max_h)
        return (w, h)

    def draw(self, stdscr) -> None:
        for i, item in enumerate(self.items):
            attr = curses.A_REVERSE if i == self.selected else curses.A_NORMAL
            try:
                stdscr.addstr(
                    self.y + i, self.x, item.ljust(self.width)[: self.width], attr
                )
            except curses.error:
                pass

    def move_up(self) -> None:
        self.selected = (self.selected - 1) % len(self.items)

    def move_down(self) -> None:
        self.selected = (self.selected + 1) % len(self.items)

    def get_selected(self) -> str:
        return self.items[self.selected]


class OptionsList(Widget):
    def __init__(self, options: List[Tuple[str, List[str], int]]):
        super().__init__()
        self.options = options
        self.row = 0

    def measure(self, max_w: int, max_h: int):
        w = 0
        for name, vals, idx in self.options:
            text = f"{name}: {vals[idx]}"
            w = min(max(w, len(text)), max_w)
        h = min(len(self.options), max_h)
        return (w, h)

    def draw(self, stdscr) -> None:
        for i, (name, vals, idx) in enumerate(self.options):
            text = f"{name}: {vals[idx]}"
            attr = curses.A_REVERSE if i == self.row else curses.A_NORMAL
            try:
                stdscr.addstr(
                    self.y + i, self.x, text.ljust(self.width)[: self.width], attr
                )
            except curses.error:
                pass

    def move_up(self) -> None:
        self.row = (self.row - 1) % len(self.options)

    def move_down(self) -> None:
        self.row = (self.row + 1) % len(self.options)

    def dec_value(self) -> None:
        name, vals, idx = self.options[self.row]
        idx = (idx - 1) % len(vals)
        self.options[self.row] = (name, vals, idx)

    def inc_value(self) -> None:
        name, vals, idx = self.options[self.row]
        idx = (idx + 1) % len(vals)
        self.options[self.row] = (name, vals, idx)

    def export(self) -> List[Tuple[str, str]]:
        # Возвращает список выбранных значений в виде [(имя, значение)]
        return [(name, vals[idx]) for name, vals, idx in self.options]


class ConfirmButtons(Widget):
    def __init__(self, labels: List[str]):
        super().__init__()
        self.labels = labels
        self.idx = 0

    def measure(self, max_w: int, max_h: int):
        w = sum(len(x) for x in self.labels) + 2 * (len(self.labels) - 1)
        w = min(w, max_w)
        return (w, 1)

    def draw(self, stdscr) -> None:
        x = self.x
        for i, lab in enumerate(self.labels):
            attr = curses.A_REVERSE if i == self.idx else curses.A_NORMAL
            try:
                stdscr.addstr(self.y, x, lab, attr)
            except curses.error:
                pass
            x += len(lab) + 2

    def left(self) -> None:
        self.idx = (self.idx - 1) % len(self.labels)

    def right(self) -> None:
        self.idx = (self.idx + 1) % len(self.labels)

    def get_selected(self) -> str:
        return self.labels[self.idx]
