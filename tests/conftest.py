import sys
import types


class FakeCursesWindow:
    def __init__(self):
        self.calls = []

    def getmaxyx(self):
        return (24, 80)

    def clear(self):
        self.calls.append(("clear",))

    def refresh(self):
        self.calls.append(("refresh",))

    def addstr(self, *args, **kwargs):
        self.calls.append(("addstr", args, kwargs))

    def box(self):
        self.calls.append(("box",))

    def nodelay(self, flag: bool):
        self.calls.append(("nodelay", flag))

    def keypad(self, flag: bool):
        self.calls.append(("keypad", flag))

    def get_wch(self):

        return None


def install_stub_modules():
    stubbed = {}

    def ensure_module(name):
        if name in sys.modules:
            return sys.modules[name], False
        m = types.ModuleType(name)
        sys.modules[name] = m
        return m, True

    for pkg in ["core", "core.ui", "states"]:
        _, created = ensure_module(pkg)
        if created:
            stubbed[pkg] = True

    if "core.models" not in sys.modules:
        m = types.ModuleType("core.models")

        m.DIFFICULTIES = ["Лёгкая", "Средняя", "Сложная", "Случайная"]

        class Settings:
            def __init__(self, difficulty=None, category=""):
                self.difficulty = difficulty or m.DIFFICULTIES[0]
                self.category = category

        class Stats:
            def __init__(self):
                self.games_played = 0
                self.wins = 0
                self.losses = 0
                self.best_streak = 0
                self.current_streak = 0

        m.Settings = Settings
        m.Stats = Stats
        sys.modules["core.models"] = m
        stubbed["core.models"] = True

    if "core.stack" not in sys.modules:
        m = types.ModuleType("core.stack")

        class DummyState:
            def on_push(self, stack):
                pass

            def on_pop(self):
                pass

            def handle_input(self, key):
                pass

            def update(self, dt):
                pass

            def draw(self):
                pass

        class StateStack:
            def __init__(self):
                self._stack = []
                self.run_loop_called_with = None

            def push(self, st):
                self._stack.append(st)
                if hasattr(st, "on_push"):
                    st.on_push(self)

            def pop(self):
                st = self._stack.pop()
                if hasattr(st, "on_pop"):
                    st.on_pop()
                return st

            def top(self):
                return self._stack[-1] if self._stack else None

            def run_loop(self, fps=30):

                self.run_loop_called_with = fps

        m.StateStack = StateStack
        sys.modules["core.stack"] = m
        stubbed["core.stack"] = True

    if "states.menu" not in sys.modules:
        m = types.ModuleType("states.menu")

        class MenuState:
            def __init__(self, ctx, stack):
                self.ctx = ctx
                self.stack = stack

        m.MenuState = MenuState
        sys.modules["states.menu"] = m
        stubbed["states.menu"] = True

    return stubbed


def add_project_paths():
    import pathlib
    import sys

    try:
        root = pathlib.Path.cwd()
    except Exception:
        root = pathlib.Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    src = root / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))
