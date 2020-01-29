import typing
import pathlib
import toml
import yaml
import dataclasses
from functools import reduce
from collections.abc import Iterable

TypePathLike = typing.Union[str, pathlib.Path]


class ConfigGenerator:
    def __init__(self):
        self._update_params: typing.Dict[str, typing.Any] = {}
        self._config: typing.Optional[Config] = None

    @staticmethod
    def __load(file: pathlib.Path):
        assert isinstance(file, pathlib.Path), f'file expected: pathlib.Path, actual {type(file)}'
        assert file.is_file(), f'{file} is not a valid file path'
        # Load Setting
        if file.suffix == '.toml':
            with file.open('r') as f:
                params = toml.load(f)
        elif file.suffix == '.yaml' or file.suffix == '.yml':
            with file.open('r') as f:
                params = yaml.safe_load(f)
        else:
            raise RuntimeError('Not support type (Toml / Yaml)')
        return params

    def type_check(self):
        def get_type_error_message(key: str, expected_type: str, actual_type: str):
            return f"{key} is expected {expected_type}, actual {actual_type}"

        def _type_check(obj: dataclasses.dataclass):
            for field in dataclasses.fields(obj):
                child_obj = obj.__getattribute__(field.name)
                if type(child_obj) == list or type(child_obj) == tuple:
                    child_obj = tuple(child_obj)
                    actual_type = [str(type(c)) for c in child_obj]
                    if len(field.type.__args__) == 1 \
                            or (len(field.type.__args__) == 2 and field.type.__args__[-1] == Ellipsis):
                        assert all([isinstance(c, field.type.__args__[0]) for c in child_obj]), \
                            get_type_error_message(field.name, str(field.type), f"Tuple[{actual_type}]")
                    else:
                        assert len(field.type.__args__) == len(child_obj), \
                            get_type_error_message(field.name, str(field.type), f"Tuple[{actual_type}]")
                        assert all([isinstance(c, t) for c, t in zip(child_obj, field.type.__args__)]), \
                            get_type_error_message(field.name, str(field.type), f"Tuple[{actual_type}]")
                    continue
                if dataclasses.is_dataclass(child_obj):
                    _type_check(child_obj)
                if child_obj is None and (field.type is None):
                    continue
                assert type(child_obj) == field.type, \
                    get_type_error_message(field.name, str(field.type), str(type(child_obj)))
        try:
            _type_check(self._config)
        except AssertionError as e:
            print(e)
            exit(1)

    def generate(self):
        self._config = Config()
        self.__set_params()
        self.type_check()
        return self._config

    def update_by(self, file_paths: typing.Union[TypePathLike, typing.Iterable[TypePathLike]]):
        if not isinstance(file_paths, Iterable):
            file_paths = [file_paths]
        if len(file_paths) == 0:
            return
        elif len(file_paths):
            self._update_params.update(reduce(self.safe_file_merge, file_paths))
        else:
            self._update_params.update(self.__load(file_paths[0]))
        return self

    def safe_file_merge(self, file_1: TypePathLike, file_2: TypePathLike)\
            -> typing.Dict[str, typing.Any]:
        d1 = self.__load(pathlib.Path(file_1))
        d2 = self.__load(pathlib.Path(file_2))

        def get_keys(d: typing.Dict[str, typing.Any], parent_key: str = ''):
            keys = []
            for k in d:
                if not isinstance(d[k], dict):
                    keys.extend(get_keys(d[k], parent_key=f'{k}/'))
                else:
                    keys.append(f'{parent_key}{k}')
            return keys

        d1_keys = set(get_keys(d1))
        d2_keys = set(get_keys(d2))

        for d1_key in d1_keys:
            for d2_key in d2_keys:
                assert not(d1_key.startswith(d2_key) or d2_key.startswith(d1_key)),\
                    f'Detect conflict. Check {d1_key} in {file_1} and {d2_key} in {file_2}'

        d1.update(d2)
        return d1

    def __set_params(self):
        def __set(obj, d: typing.Dict[str, typing.Any]):
            for k, v in d.items():
                if not isinstance(v, dict):
                    setattr(obj, k, v)
                else:
                    __set(obj.__getattribute__(k), v)
        __set(self._config, self._update_params)

