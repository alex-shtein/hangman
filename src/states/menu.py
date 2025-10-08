from __future__ import annotations

import curses

from core.stack import StateStack
from core.ui.widgets import Label
from core.ui.widgets import VerticalMenu
from states.confirm_exit import ConfirmExitState
from states.game_round import GameRoundState


class MenuState:
    def __init__(self, ctx, stack: StateStack):
        self.ctx = ctx
        self.stack = stack
        self.menu = VerticalMenu(["Играть", "Настройки", "Статистика", "Выйти"])
        self.title = Label("ВИСЕЛИЦА", bold=True)
        self.flash_msg = ""
        self.flash_timer = 0.0

    def on_push(self, stack: StateStack) -> None:
        pass

    def on_pop(self) -> None:
        pass

    def _open_settings(self):
        from states.settings import SettingsState

        self.stack.push(SettingsState(self.ctx, self.stack))

    def _open_statistic(self):
        from states.statistic import StatisticState

        self.stack.push(StatisticState(self.ctx, self.stack))

    def _open_confirm_exit(self):
        self.stack.push(ConfirmExitState(self.ctx, self.stack))

    def _open_confirm_exit_in_menu(self):
        def _yes_to_menu():
            self.stack.clear()
            self.stack.push(MenuState(self.ctx, self.stack))

        self.stack.push(
            ConfirmExitState(
                self.ctx,
                self.stack,
                title="Вы хотите выйти в меню?",
                on_yes=_yes_to_menu,
            )
        )

    def _restart_round(self):
        def _open_confirm_exit_in_menu():
            self._open_confirm_exit_in_menu()

        def _restart():
            self._restart_round()

        self.stack.push(
            GameRoundState(self.ctx, self.stack, _open_confirm_exit_in_menu, _restart)
        )

    def _start_round(self):
        def _open_confirm_exit_in_menu():
            self._open_confirm_exit_in_menu()

        def _restart():
            self._restart_round()

        self.stack.push(
            GameRoundState(self.ctx, self.stack, _open_confirm_exit_in_menu, _restart)
        )

    def handle_input(self, key: int) -> None:
        if key in (curses.KEY_UP, "k"):
            self.menu.move_up()
        elif key in (curses.KEY_DOWN, "j"):
            self.menu.move_down()
        elif key in (curses.KEY_ENTER, "10", "13", "\n"):
            sel = self.menu.get_selected()
            if sel == "Играть":
                self._start_round()
            elif sel == "Настройки":
                self._open_settings()
            elif sel == "Статистика":
                self._open_statistic()
            elif sel == "Выйти":
                self._open_confirm_exit()
        elif key in ("27", "й", "\x1b"):
            self._open_confirm_exit()

    def update(self, dt: float) -> None:
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_msg = ""

    def draw(self) -> None:
        stdscr = self.ctx.stdscr
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        tw, _ = self.title.measure(w, h)
        self.title.layout((w - tw) // 2, 2, tw, 1)
        self.title.draw(stdscr)

        mw, mh = self.menu.measure(w, h)
        self.menu.layout((w - mw) // 2, 5, mw, mh)
        self.menu.draw(stdscr)

        if self.flash_msg:
            try:
                stdscr.addstr(
                    h - 2, max(0, (w - len(self.flash_msg)) // 2), self.flash_msg
                )
            except curses.error:
                pass

        hint = "↑/↓ — выбор • Enter — подтвердить • Esc/й — выход"
        try:
            stdscr.addstr(h - 1, max(0, (w - len(hint)) // 2), hint)
        except curses.error:
            pass

        stdscr.refresh()

        try:
            key = stdscr.get_wch()
            if key is not None:
                self.handle_input(key)
        except curses.error:
            pass
