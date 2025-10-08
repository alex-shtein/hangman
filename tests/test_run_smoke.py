import importlib

from conftest import add_project_paths
from conftest import install_stub_modules


def test_run_module_has_main():
    install_stub_modules()
    add_project_paths()
    try:
        run = importlib.import_module("src.run")
    except ModuleNotFoundError:
        run = importlib.import_module("src.run")
    assert hasattr(run, "src.main")
