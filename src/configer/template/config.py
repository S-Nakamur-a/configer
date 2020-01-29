from typing import List
from pathlib import Path

from prestring.python import PythonModule


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
        m.stmt(m.newline)

    m.stmt("@dataclasses.dataclass")
    with m.class_("Config"):
        post_inits = []
        for key in params:
            if 'dataclasses.field(init=False)' in key:
                s = key.split(' ')
                key_name = s[0][:-1]
                class_name = s[1]
                post_inits.append(f'self.{key_name} = {class_name}()')
            m.stmt(key)
        m.stmt(m.newline)
        if len(post_inits):
            with m.method('__post_init__'):
                for post_init in post_inits:
                    m.stmt(post_init)

    with (Path(__file__).parent / 'core.py').open("r") as f:
        lines: List[str] = f.readlines()
        m.stmt(''.join([l for l in lines if not l.startswith("import")]))

    return m

