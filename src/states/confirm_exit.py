from __future__ import annotations

import curses

from core.ui.widgets import ConfirmButtons, Label


# ConfirmExitState — универсальный диалог подтверждения.
class ConfirmExitState:
    def __init__(self, ctx, stack, title: str | None = None, on_yes=None):
        self.ctx = ctx
        self.stack = stack
        self.title = Label(title or "Вы уверены, что хотите выйти из игры?", bold=True)
        self.buttons = ConfirmButtons(["Да", "Нет"])
        self.on_yes = on_yes

    def on_push(self, stack): ...
    def on_pop(self): ...

    def handle_input(self, key) -> None:
        if key in (curses.KEY_LEFT, "h", "H"):
            self.buttons.left()
        elif key in (curses.KEY_RIGHT, "l", "L"):
            self.buttons.right()

        elif key in (curses.KEY_ENTER, 10, 13, "\n"):
            if self.buttons.get_selected() == "Да":
                if callable(self.on_yes):
                    self.on_yes()
                else:
                    self.stack.request_quit()
            else:
                self.stack.pop()

        elif key in (27, "\x1b") or (isinstance(key, str) and key.lower() == "й"):
            self.stack.pop()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        stdscr = self.ctx.stdscr
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        dlg_w = min(max(len(self.title.text) + 4, 38), max(20, w - 2))
        dlg_h = 7
        x = (w - dlg_w) // 2
        y = (h - dlg_h) // 2

        try:
            win = stdscr.derwin(dlg_h, dlg_w, y, x)
            win.box()

            # Заголовок
            self.title.layout(2, 2, dlg_w - 4, 1)
            self.title.draw(win)

            # Кнопки
            bw, _ = self.buttons.measure(dlg_w - 4, 1)
            self.buttons.layout((dlg_w - bw) // 2, dlg_h - 3, bw, 1)
            self.buttons.draw(win)
        except curses.error:
            pass

        stdscr.refresh()

        try:
            key = stdscr.get_wch()
            if key is not None:
                self.handle_input(key)
        except curses.error:
            pass
