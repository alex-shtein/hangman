from __future__ import annotations

import curses
from typing import List
from typing import Optional
from typing import Tuple


class Widget:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0

    def measure(self, max_w: int, max_h: int) -> Tuple[int, int]:
        return (self.width or max_w, self.height or 1)

    def layout(self, x: int, y: int, w: int, h: int) -> None:
        self.x, self.y, self.width, self.height = x, y, w, h

    def draw(self, stdscr) -> None:
        pass


class Container(Widget):
    def __init__(self, children: Optional[List[Widget]] = None, padding: int = 0):
        super().__init__()
        self.children = children or []
        self.padding = padding

    def add(self, child: Widget) -> "Container":
        self.children.append(child)
        return self


class VBox(Container):
    def __init__(
        self,
        children: Optional[List[Widget]] = None,
        padding: int = 0,
        spacing: int = 1,
        align: str = "center",
    ):
        super().__init__(children, padding)
        self.spacing = spacing
        self.align = align

    def layout(self, x: int, y: int, w: int, h: int) -> None:
        super().layout(x, y, w, h)
        cy = y + self.padding
        for ch in self.children:
            ch_w, ch_h = ch.measure(w - 2 * self.padding, h)
            if self.align == "left":
                cx = x + self.padding
            elif self.align == "right":
                cx = x + w - self.padding - ch_w
            else:
                cx = x + (w - ch_w) // 2
            ch.layout(cx, cy, ch_w, ch_h)
            cy += ch_h + self.spacing

    def draw(self, stdscr) -> None:
        for ch in self.children:
            ch.draw(stdscr)


class HBox(Container):
    def __init__(
        self,
        children: Optional[List[Widget]] = None,
        padding: int = 0,
        spacing: int = 2,
        align: str = "middle",
    ):
        super().__init__(children, padding)
        self.spacing = spacing
        self.align = align

    def layout(self, x: int, y: int, w: int, h: int) -> None:
        super().layout(x, y, w, h)
        cx = x + self.padding
        for ch in self.children:
            ch_w, ch_h = ch.measure(w, h - 2 * self.padding)
            if self.align == "top":
                cy = y + self.padding
            elif self.align == "bottom":
                cy = y + h - self.padding - ch_h
            else:
                cy = y + (h - ch_h) // 2
            ch.layout(cx, cy, ch_w, ch_h)
            cx += ch_w + self.spacing

    def draw(self, stdscr) -> None:
        for ch in self.children:
            ch.draw(stdscr)


class Frame(Container):
    def __init__(
        self,
        child: Optional[Widget] = None,
        title: Optional[str] = None,
        padding: int = 1,
    ):
        super().__init__([child] if child else [], padding)
        self.title = title or ""

    def layout(self, x: int, y: int, w: int, h: int) -> None:
        super().layout(x, y, w, h)
        if self.children:
            inner_w = max(0, w - 2 - 2 * self.padding)
            inner_h = max(0, h - 2 - 2 * self.padding)
            self.children[0].layout(
                x + 1 + self.padding, y + 1 + self.padding, inner_w, inner_h
            )

    def draw(self, stdscr) -> None:
        try:
            stdscr.box()
        except curses.error:
            pass
        if self.title:
            try:
                stdscr.addstr(self.y, self.x + 2, f" {self.title} ")
            except curses.error:
                pass
        for ch in self.children:
            ch.draw(stdscr)


class Center(Container):
    def __init__(self, child: Optional[Widget] = None):
        super().__init__([child] if child else [])

    def layout(self, x: int, y: int, w: int, h: int) -> None:
        super().layout(x, y, w, h)
        if self.children:
            ch = self.children[0]
            cw, ch_h = ch.measure(w, h)
            cx = x + (w - cw) // 2
            cy = y + (h - ch_h) // 2
            ch.layout(cx, cy, cw, ch_h)

    def draw(self, stdscr) -> None:
        for ch in self.children:
            ch.draw(stdscr)
