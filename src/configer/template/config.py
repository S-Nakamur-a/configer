
from typing import List
from pathlib import Path

from prestring.python import PythonModule


def generate(my_dataclasses: List[str], params: List[str], default_file: str, default_hash: str):
    m = PythonModule(width=80, import_unique=True)
    m.stmt("""# Generated From configer
# Please do not modify.
# If you want to do, edit your default.yml, and run `configer update` on your terminal.""")
    m.import_("typing")  # import typing
    m.import_("dataclasses")  # import typing
    m.import_("pathlib")  # import typing
    m.import_("toml")  # import typing
    m.import_("yaml")  # import typing
    m.import_("random")  # import typing
    m.sep()

    with m.def_('get_default_file_and_hash'):
        try:
            path = Path(default_file).relative_to(Path.cwd())
        except ValueError:
            path = Path(default_file).absolute()
        m.stmt(f'return \'{path}\',\\{m.newline}{m.indent*2}\'{default_hash}\'')

    with (Path(__file__).parent / 'utils.py').open("r") as f:
        lines: List[str] = f.readlines()
        m.stmt(''.join([l for l in lines if not l.startswith("from")]))

    for my_dataclass in my_dataclasses:
        m.stmt(my_dataclass)
        m.stmt(m.newline)

    m.stmt("@dataclasses.dataclass(frozen=True)")
    with m.class_("_Config"):
        post_inits = []
        for key in params:
            if 'dataclasses.field(init=False)' in key:
                s = key.split(' ')
                key_name = s[0][:-1]
                class_name = s[1]
                post_inits.append(f"super().__setattr__('{key_name}', {class_name}())")
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
