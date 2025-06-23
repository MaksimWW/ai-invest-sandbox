import importlib
def test_core_packages():
    for pkg in ("numpy", "pandas", "telegram", "openai"):
        assert importlib.import_module(pkg).__version__
