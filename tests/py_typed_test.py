from importlib import resources


def test_the_package_ships_its_typing_marker():
    # pyproject.toml declares "Typing :: Typed", which type checkers only honour when the installed
    # package carries a py.typed marker; without it, mypy skips the whole package as untyped.
    assert resources.files("xai_sdk").joinpath("py.typed").is_file()
