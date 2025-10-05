import curses


class Button:
    def __init__(self, label, callback=None):
        self.label = label
        self.callback = callback

    def activate(self):
        if self.callback:
            self.callback()

    def get_label(self):
        return self.label


class CycleButton(Button):
    def __init__(self, options, current_index=0, on_change=None):
        super().__init__(options[current_index])
        self.options = options
        self.index = current_index
        self.on_change = on_change

    def cycle(self, direction=1):
        self.index = (self.index + direction) % len(self.options)
        self.label = self.options[self.index]
        if self.on_change:
            self.on_change(self.label)


class SettingsButtons:
    def __init__(self, items, stdscr):
        self.items = items
        self.stdscr = stdscr
        self.row = 0
        self.col = 0

    def draw(self):
        self.stdscr.clear()
        for r, row in enumerate(self.items):
            x = 2
            for c, item in enumerate(row):
                highlight = r == self.row and c == self.col
                if highlight:
                    self.stdscr.attron(curses.A_REVERSE)
                self.stdscr.addstr(r + 2, x, item.get_label())
                if highlight:
                    self.stdscr.attroff(curses.A_REVERSE)
                x += len(item.get_label()) + 4
        self.stdscr.refresh()

    def run(self):
        while True:
            self.draw()
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                self.row = (self.row - 1) % len(self.items)
                self.col = min(self.col, len(self.items[self.row]) - 1)

            elif key == curses.KEY_DOWN:
                self.row = (self.row + 1) % len(self.items)
                self.col = min(self.col, len(self.items[self.row]) - 1)

            elif key == curses.KEY_LEFT:
                item = self.items[self.row][self.col]
                if isinstance(item, CycleButton):
                    item.cycle(-1)
                else:
                    self.col = (self.col - 1) % len(self.items[self.row])

            elif key == curses.KEY_RIGHT:
                item = self.items[self.row][self.col]
                if isinstance(item, CycleButton):
                    item.cycle(1)
                else:
                    self.col = (self.col + 1) % len(self.items[self.row])

            elif key == ord("\n"):
                self.items[self.row][self.col].activate()
                return


def main(stdscr):
    settings = {"difficulty": "Лёгкий", "category": "Автомобили"}

    def save_settings():
        with open("settings.json", "w", encoding="8-utf") as file:
            file.write(settings, file, ensure_ascii=False, indent=4)

    items = [
        [
            CycleButton(
                ["Лёгкий", "Средний", "Сложный", "Случайно"],
                on_change=lambda val: settings.update(difficulty=val),
            )
        ],
        [
            CycleButton(
                ["Автомобили", "Страны", "Животные", "Фрукты", "Случайно"],
                on_change=lambda val: settings.update(category=val),
            )
        ],
        [
            Button("Назад", callback=lambda: exit(0)),
            Button("Сохранить", callback=save_settings),
        ],
    ]

    settings_buttons = SettingsButtons(items, stdscr)
    settings_buttons.run()


if __name__ == "__main__":
    curses.wrapper(main)
