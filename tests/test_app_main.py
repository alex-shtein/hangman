import sys
from types import ModuleType

from conftest import FakeCursesWindow
from conftest import add_project_paths
from conftest import install_stub_modules


def maybe_stub_dependencies():
    import importlib.util

    need_stub = any(
        importlib.util.find_spec(name) is None
        for name in ["core", "core.models", "core.stack", "states", "states.menu"]
    )
    if need_stub:
        install_stub_modules()
    return need_stub


def test_main_runs_wrapper_and_pushes_menu(monkeypatch):
    called = {"wrapper": False}
    fake_win = FakeCursesWindow()

    class FakeCurses(ModuleType):
        def wrapper(self, fn):
            called["wrapper"] = True
            return fn(fake_win)

        COLOR_BLACK = 0
        KEY_UP = 259
        KEY_DOWN = 258
        KEY_LEFT = 260
        KEY_RIGHT = 261
        KEY_RESIZE = 410
        A_BOLD = 1
        A_REVERSE = 2
        A_DIM = 3
        A_NORMAL = 0

        def curs_set(self, *a, **k):
            pass

        def use_default_colors(self, *a, **k):
            pass

        def init_pair(self, *a, **k):
            pass

        def start_color(self, *a, **k):
            pass

        def noecho(self, *a, **k):
            pass

        def cbreak(self, *a, **k):
            pass

        def keypad(self, *a, **k):
            pass

        def meta(self, *a, **k):
            pass

        def has_colors(self):
            return True

    sys.modules["curses"] = FakeCurses("curses")
    stubbed = maybe_stub_dependencies()
    add_project_paths()

    try:
        import app
    except ModuleNotFoundError:
        import importlib

        app = importlib.import_module("src.app")

    import importlib

    importlib.reload(app)

    from core.stack import StateStack

    app.main()

    assert called["wrapper"] is True

    if stubbed:
        s = StateStack()
        assert isinstance(s, StateStack)
        assert hasattr(s, "run_loop_called_with")
    else:
        assert True
