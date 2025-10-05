from __future__ import annotations

import curses

from core.models import DIFFICULTIES
from core.ui.widgets import Label, OptionsList


# SettingsState — экран настроек
class SettingsState:
    def __init__(self, ctx, stack):
        self.ctx = ctx
        self.stack = stack

        # Текущие значения
        cur_diff = self.ctx.settings.difficulty
        cur_cat = self.ctx.settings.category

        # Списки значений
        categories = self.ctx.categories[:]

        # Индексы по текущим значениям
        diff_idx = DIFFICULTIES.index(cur_diff) if cur_diff in DIFFICULTIES else 0
        cat_idx = (
            categories.index(cur_cat)
            if cur_cat in categories
            else (0 if categories else 0)
        )

        self.header = Label("НАСТРОЙКИ", bold=True)
        self.options = OptionsList(
            [
                ("Сложность", DIFFICULTIES, diff_idx),
                ("Категория", categories if categories else ["—"], cat_idx),
            ]
        )
        self.footer = Label(
            "↑/↓ — выбрать, ←/→ — изменить, Enter/Esc — сохранить и назад"
        )

    def on_push(self, stack): ...

    def on_pop(self): ...

    def handle_input(self, key: int) -> None:
        if key in (curses.KEY_UP, "w"):
            self.options.move_up()
        elif key in (curses.KEY_DOWN, "s"):
            self.options.move_down()
        elif key in (curses.KEY_LEFT, "a"):
            self.options.dec_value()
        elif key in (curses.KEY_RIGHT, "d"):
            self.options.inc_value()
        elif key in (27, curses.KEY_ENTER, "\n", "\x1b", 10, 13):
            # Сохранить и вернуться
            picked = dict(self.options.export())
            new_diff = picked.get("Сложность", self.ctx.settings.difficulty)
            new_cat = picked.get("Категория", self.ctx.settings.category)
            # Если категорий нет, оставим пустую
            if self.ctx.categories and new_cat not in self.ctx.categories:
                new_cat = self.ctx.categories[0]
            elif not self.ctx.categories:
                new_cat = ""
            self.ctx.settings.difficulty = new_diff
            self.ctx.settings.category = new_cat
            self.ctx.save_settings()
            self.stack.pop()

    def update(self, dt: float) -> None: ...

    def draw(self) -> None:
        stdscr = self.ctx.stdscr
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Заголовок
        hw, _ = self.header.measure(w, h)
        self.header.layout((w - hw) // 2, 1, hw, 1)
        self.header.draw(stdscr)

        # Рамка с опциями
        ow, oh = self.options.measure(w - 4, h - 6)
        fw, fh = max(ow + 4, 24), oh + 4
        x = (w - fw) // 2
        y = max(3, (h - fh) // 2)

        try:
            win = stdscr.derwin(fh, fw, y, x)
            win.box()
            try:
                win.addstr(0, 2, " Параметры ")
            except curses.error:
                pass
            self.options.layout(2, 2, fw - 4, oh)
            self.options.draw(win)
        except curses.error:
            pass

        # Подвал
        ftxt = self.footer.text
        try:
            stdscr.addstr(h - 2, max(0, (w - len(ftxt)) // 2), ftxt)
        except curses.error:
            pass

        stdscr.refresh()

        try:
            key = stdscr.get_wch()
            if key is not None:
                self.handle_input(key)
        except curses.error:
            pass
