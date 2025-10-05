from __future__ import annotations

import curses
import glob
import os
import random
from typing import Callable, Set

from core.models import DIFFICULTIES
from core.stack import StateStack
from core.ui.widgets import Label
from states.game_result import GameResultState

# попытки по сложности
ATTEMPTS_BY_DIFF = {
    "Лёгкая": 8,
    "Средняя": 6,
    "Сложная": 4,
}

HINTS_BY_DIFF = {
    "Лёгкая": 2,
    "Средняя": 1,
    "Сложная": 0,
}

# ASCII стадии виселицы (индекс = число ошибок)
GALLOWS = [
    [" ┌───────┐", " │       │", " │       ", " │       ", " │       ", "─┴─      "],
    [" ┌───────┐", " │       │", " │       O", " │       ", " │       ", "─┴─      "],
    [" ┌───────┐", " │       │", " │       O", " │       |", " │       ", "─┴─      "],
    [" ┌───────┐", " │       │", " │       O", " │      /|", " │       ", "─┴─      "],
    [
        " ┌───────┐",
        " │       │",
        " │       O",
        " │      /|\\",
        " │       ",
        "─┴─      ",
    ],
    [
        " ┌───────┐",
        " │       │",
        " │       O",
        " │      /|\\",
        " │      / ",
        "─┴─      ",
    ],
    [
        " ┌───────┐",
        " │       │",
        " │       O",
        " │      /|\\",
        " │      / \\",
        "─┴─      ",
    ],
]


# game_round.py (или общий utils.py)
def _rus_upper(s: str) -> str:
    return s.strip().upper().replace("Ё", "Е")


def _is_rus_letter_key(key) -> bool:
    if isinstance(key, str) and len(key) == 1:
        c = _rus_upper(key)
        return "А" <= c <= "Я"
    return False


def _read_random_word(words_dir: str, category: str) -> str:
    path = os.path.join(words_dir, f"{category}.txt")
    with open(path, "r", encoding="utf-8") as f:
        candidates = [
            word.strip() for line in f for word in line.split(",") if word.strip()
        ]
    if not candidates:
        raise RuntimeError(f"В категории '{category}' нет слов")
    return _rus_upper(random.choice(candidates))


def _mask_word(word: str, opened: Set[str]) -> str:
    return "".join(
        ch if (_rus_upper(ch) in opened) or ch == "-" else "*" for ch in word
    )


def _random_closed_letter(word: str, opened: Set[str]) -> str | None:
    letters = sorted({_rus_upper(ch) for ch in word if ch.isalpha()})
    closed = [c for c in letters if c not in opened]
    return random.choice(closed) if closed else None


class GameRoundState:
    def __init__(
        self,
        ctx,
        stack: StateStack,
        open_confirm_exit_in_menu: Callable[[], None],
        restart_round: Callable[[], None],
    ):
        self.ctx = ctx
        self.stack = stack
        self.open_confirm_exit_in_menu = open_confirm_exit_in_menu
        self.restart_round = restart_round

        # Выбираем категорию
        self.category = self._choose_category()

        # Выбираем сложность
        self.difficulty = self._choose_difficulty()

        # Настройки по выбранной сложности
        self.max_hints = HINTS_BY_DIFF.get(self.difficulty, 2)
        self.start_attempts = ATTEMPTS_BY_DIFF.get(self.difficulty, 8)
        self.attempts_left = self.start_attempts

        # Инициализация состояния
        self.word = _read_random_word(ctx.words_dir, self.category)
        self.opened: Set[str] = set()
        self.used: Set[str] = set()
        self.hints_used = 0

        self.title = Label("ВИСЕЛИЦА", bold=True)
        self.flash_msg = ""
        self.flash_timer = 0.0

    def _choose_category(self) -> str:
        cat = self.ctx.settings.category
        if cat == "Случайная" or not cat:
            paths = glob.glob(os.path.join(self.ctx.words_dir, "*.txt"))
            cats = [os.path.splitext(os.path.basename(p))[0] for p in paths]
            cats = [c for c in cats if c and c != "Случайная"]
            if not cats:
                return "Без категории"
            return random.choice(cats)
        return cat

    def _choose_difficulty(self) -> str:
        diff = self.ctx.settings.difficulty
        if diff == "Случайная" or diff not in ATTEMPTS_BY_DIFF:
            return random.choice([d for d in DIFFICULTIES if d != "Случайная"])
        return diff

    def on_push(self, stack: StateStack) -> None: ...
    def on_pop(self) -> None: ...

    def _flash(self, text: str, t: float = 1.2) -> None:
        self.flash_msg, self.flash_timer = text, t

    def _apply_guess(self, letter: str) -> None:
        letter = _rus_upper(letter)
        if letter in self.used:
            return
        self.used.add(letter)
        if letter in _rus_upper(self.word):
            self.opened.add(letter)
        else:
            self.attempts_left = max(0, self.attempts_left - 1)

    def _apply_hint(self) -> None:
        if self.hints_used >= self.max_hints:
            self._flash("Подсказок больше нет")
            return
        letter = _random_closed_letter(self.word, self.opened)
        if letter is None:
            self._flash("Слово уже раскрыто")
            return
        self.hints_used += 1
        self.opened.add(letter)
        self.used.add(letter)

    def _is_win(self) -> bool:
        for ch in self.word:
            cu = _rus_upper(ch)
            if ch.isalpha() and cu not in self.opened:
                return False
        return True

    def _is_lose(self) -> bool:
        return self.attempts_left <= 0 and not self._is_win()

    def _finish_round(self, win: bool) -> None:
        s = self.ctx.stats
        s.games_played += 1
        if win:
            s.wins += 1
            s.current_streak += 1
            s.best_streak = max(s.best_streak, s.current_streak)
        else:
            s.losses += 1
            s.current_streak = 0
        self.ctx.save_stats()

        self.stack.push(
            GameResultState(
                ctx=self.ctx,
                stack=self.stack,
                win=win,
                word=self.word,
                hints_used=self.hints_used,
                attempts_left=self.attempts_left,
                restart_round=self.restart_round,
            )
        )

    def handle_input(self, key) -> None:
        if _is_rus_letter_key(key):
            self._apply_guess(key)
        elif key in (curses.KEY_ENTER, 10, 13, "\n"):
            self.attempts_left = 0
        elif key in (27, "\x1b"):
            self.open_confirm_exit_in_menu()
        elif key == " ":
            self._apply_hint()

        if self._is_win():
            self._finish_round(True)
        elif self._is_lose():
            self._finish_round(False)

    def update(self, dt: float) -> None:
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_msg = ""

    def draw(self) -> None:
        stdscr = self.ctx.stdscr
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Заголовок
        tw, _ = self.title.measure(w, h)
        self.title.layout((w - tw) // 2, 1, tw, 1)
        self.title.draw(stdscr)

        # Попытки (центр сверху)
        attempts_line = f"Попытки: {self.attempts_left}"
        try:
            stdscr.addstr(3, max(0, (w - len(attempts_line)) // 2), attempts_line)
        except curses.error:
            pass

        # Категория (справа)
        cat_line = f"Категория: {self.category or '—'}"
        try:
            stdscr.addstr(3, max(0, w - len(cat_line) - 2), cat_line)
        except curses.error:
            pass

        dif_line = f"Сложность: {self.difficulty or '—'}"
        try:
            stdscr.addstr(4, max(0, w - len(cat_line) - 2), dif_line)
        except curses.error:
            pass

        hints_used = f"Подсказки: {self.max_hints - self.hints_used}"
        try:
            stdscr.addstr(5, max(0, w - len(cat_line) - 2), hints_used)
        except curses.error:
            pass

        # Виселица слева
        mistakes = self.start_attempts - self.attempts_left
        stage_idx = min(mistakes, len(GALLOWS) - 1)
        for i, line in enumerate(GALLOWS[stage_idx]):
            try:
                stdscr.addstr(3 + i, 2, line)
            except curses.error:
                pass

        # Загаданное слово по центру
        masked = _mask_word(self.word, self.opened)
        try:
            stdscr.addstr(h // 2 - 1, max(0, (w - len(masked)) // 2), masked)
        except curses.error:
            pass

        # Использованные буквы под словом
        used_str = "Использованные: " + (
            " ".join(sorted(self.used)) if self.used else "—"
        )
        try:
            stdscr.addstr(h // 2 + 1, max(0, (w - len(used_str)) // 2), used_str)
        except curses.error:
            pass

        # Всплывающее
        if self.flash_msg:
            try:
                stdscr.addstr(
                    h - 3, max(0, (w - len(self.flash_msg)) // 2), self.flash_msg
                )
            except curses.error:
                pass

        # Hint
        hint = "Пробел — использвоать подсказку • Esc — в меню"
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
