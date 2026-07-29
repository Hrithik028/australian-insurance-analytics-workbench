"""Download or load the revision-pinned freMTPL2 source files."""

from pprint import pprint

from src.fremtpl2.download import acquire_fremtpl2

if __name__ == "__main__":
    pprint(acquire_fremtpl2())
