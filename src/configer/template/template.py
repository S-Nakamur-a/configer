
from typing import List
from pathlib import Path

from prestring.python import PythonModule


def generate(my_dataclasses: List[str], params: List[str], default_file: str, default_hash: str):
    m = PythonModule(width=80, import_unique=True)
    m.stmt("""# Generated From configer
# Please do not modify.
# If you want to do, edit your default.yml, and run `configer update` on your terminal.""")

    embedding_file(m, Path(__file__).parent / 'imports.py')
    m.sep()
    with m.def_('get_default_file_and_hash'):
        try:
            path = Path(default_file).absolute().relative_to(Path.cwd())
        except ValueError:
            path = Path(default_file).absolute()
        m.stmt(f'return \'{path}\',\\{m.newline}{m.indent*2}\'{default_hash}\'')

    embedding_file(m, Path(__file__).parent / 'type_hint.py')
    m.sep()
    embedding_file(m, Path(__file__).parent / 'errors.py')
    m.sep()
    embedding_file(m, Path(__file__).parent / 'utils.py')
    m.sep()

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
        m.sep()
        if len(post_inits):
            with m.method('__post_init__'):
                for post_init in post_inits:
                    m.stmt(post_init, end="")
            m.body.pop()
    embedding_file(m, Path(__file__).parent / 'core.py')

    return m


def embedding_file(python_module: PythonModule, path: Path):
    """
    # no include - # no includeで囲まれた領域以外を読み込む
    Args:
        python_module:
        path:

    Returns:

    """
    with path.open("r") as f:
        raw_lines: List[str] = f.readlines()
        include_line = True
        for raw_line in raw_lines:
            if raw_line.startswith('# no include'):
                include_line = not include_line
                continue
            if include_line:
                python_module.append(raw_line)
