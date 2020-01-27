from typing import List
from pathlib import Path

from prestring.python import PythonModule
from prestring.go import GoModule


def generate(my_dataclasses: List[str], params: List[str]):
    m = PythonModule(width=80, import_unique=True)

    m.import_("typing")  # import typing
    m.import_("dataclasses")  # import typing
    m.import_("pathlib")  # import typing
    m.import_("toml")  # import typing
    m.import_("yaml")  # import typing
    m.import_("random")  # import typing
    m.import_("shutil")  # import typing
    m.sep()

    for my_dataclass in my_dataclasses:
        m.stmt(my_dataclass)
        m.sep()

    m.stmt("@dataclasses.dataclass(frozen=True)")
    with m.class_("_Config"):
        for key in params:
            m.stmt(key)

    m.sep()
    with (Path(__file__).parent / 'core.py').open("r") as f:
        lines: List[str] = f.readlines()
        m.stmt(''.join([l for l in lines if not l.startswith("import")]))

    return m

