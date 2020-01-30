import typing
import pathlib
import toml
import yaml
import dataclasses
from functools import reduce
from collections.abc import Iterable
import random
from clint import textui

TypePathLike = typing.Union[str, pathlib.Path]


class ConfigerError(Exception):
    pass


class ConflictError(ConfigerError):
    def __init__(self, key_and_origins: typing.Tuple[typing.Tuple[str, TypePathLike], typing.Tuple[str, TypePathLike]]):
        super(ConflictError, self).__init__(
            f"Detect conflict. Check {key_and_origins[0][0]} in {key_and_origins[0][1]}"
            f" and {key_and_origins[1][0]} in {key_and_origins[1][1]}")


class InvalidDefaultFromError(ConfigerError):
    def __init__(self, key, default_value, this_value):
        super(InvalidDefaultFromError, self).__init__(f'{key} is modified from {default_value} to {this_value}')


class InvalidTypeError(ConfigerError):
    def __init__(self, key: str, expected_type: str, actual_type: str):
        super(InvalidTypeError, self).__init__(f"{key} is expected {expected_type}, actual {actual_type}")



@dataclasses.dataclass(frozen=True)
class Config(_Config):
    _origins: typing.ClassVar[typing.Dict[str, TypePathLike]]

    def pprint(self, wait: bool):
        default_config = dataclasses.asdict(_Config())

        """print setting values"""

        def print_dict(d1: dict, d2: dict, depth: int = 0, parent_key: str = ''):
            for k1, v1 in d1.items():
                indent = ' ' * depth
                if isinstance(v1, dict):
                    textui.puts(f"{indent}{textui.colored.blue(k1)}")
                    print_dict(v1, d2[k1], depth + 1, parent_key=f'{parent_key}/{k1}')
                else:
                    if d1[k1] == d2[k1]:
                        # same as default
                        textui.puts(f"{indent}{textui.colored.blue(k1)}: {textui.colored.green(str(v1))}")
                    else:
                        origin_k = f'{parent_key}/{k1}'
                        textui.puts(f"{indent}{textui.colored.yellow(k1)}: {textui.colored.red(str(v1))}"
                                    f" (default: {textui.colored.green(str(d2[k1]))}, "
                                    f"changed by {self._origins[origin_k]})")

        print_dict(dataclasses.asdict(self), default_config, 0, '')

        if wait:
            random_code = ''.join(random.choices([str(i) for i in range(10)], k=3))
            ans = input(
                'Check setting values. If these are OK, you input this one-time code [{}] > '.format(random_code))
            if ans == random_code:
                return
            else:
                print("OK, now re-check your settings.")
                exit()

    def save_as(self, out_path: TypePathLike, data_type: str):
        out_path = pathlib.Path(out_path)
        out_dir: pathlib.Path = out_path.parent
        if not out_dir.is_dir():
            out_dir.mkdir(exist_ok=False)
        with out_path.open('w') as f:
            current_dict = dataclasses.asdict(self)
            if data_type == 'yml' or data_type == 'yaml':
                yaml.safe_dump(current_dict, f)
            elif data_type == 'toml':
                toml.dump(current_dict, f)
            else:
                raise RuntimeError('Not supported type.')


class ConfigGenerator:
    def __init__(self, default_from: TypePathLike):
        self._default_from = default_from
        self._default_params: typing.Dict[str, typing.Any] = self.__load(pathlib.Path(default_from))
        self._update_params: typing.Dict[str, typing.Any] = {}
        self._origins: typing.Dict[str, TypePathLike] = {}
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

        def list_to_tuple(d: typing.Dict[str, typing.Any]):
            for k, v in d.items():
                if isinstance(v, list):
                    d[k] = tuple(v)
                if isinstance(v, dict):
                    list_to_tuple(v)

        list_to_tuple(params)

        return params

    def _check_type(self):

        def _check_type(obj: dataclasses.dataclass):
            for field in dataclasses.fields(obj):
                child_obj = obj.__getattribute__(field.name)

                if type(child_obj) == tuple:
                    actual_type = [str(type(c)) for c in child_obj]
                    if len(field.type.__args__) == 1 \
                            or (len(field.type.__args__) == 2 and field.type.__args__[-1] == Ellipsis):
                        if not all([isinstance(c, field.type.__args__[0]) for c in child_obj]):
                            raise InvalidTypeError(field.name, str(field.type), f"Tuple[{actual_type}]")
                    else:
                        if len(field.type.__args__) != len(child_obj):
                            raise InvalidTypeError(field.name, str(field.type), f"Tuple[{actual_type}]")
                        if not all([isinstance(c, t) for c, t in zip(child_obj, field.type.__args__)]):
                            raise InvalidTypeError(field.name, str(field.type), f"Tuple[{actual_type}]")
                    continue
                if dataclasses.is_dataclass(child_obj):
                    _check_type(child_obj)
                if child_obj is None and (field.type is None):
                    continue
                if type(child_obj) != field.type:
                    raise InvalidTypeError(field.name, str(field.type), str(type(child_obj)))
        if self._config is None:
            raise RuntimeError('generateが呼ばれていません')

        _check_type(self._config)

    def _check_default(self):
        def _check_default(obj, d: typing.Dict[str, typing.Any]):
            for k, v in d.items():
                if isinstance(v, dict):
                    _check_default(obj.__getattribute__(k), v)
                else:
                    default_v = obj.__getattribute__(k)
                    if default_v != v:
                        raise InvalidDefaultFromError(k, default_v, v)

        _check_default(self._config, self._default_params)

    def generate(self) -> Config:
        self._config = Config()
        self._check_default()
        self._set_params()
        self._check_type()
        return self._config

    def update_by(self, file_paths: typing.Union[TypePathLike, typing.Iterable[TypePathLike]]):
        if not isinstance(file_paths, Iterable):
            file_paths = [file_paths]
        if len(file_paths) == 0:
            return
        elif len(file_paths) > 1:
            _update_nested_dict(self._update_params, reduce(self._safe_file_merge, file_paths))
        else:
            d = self.__load(file_paths[0])
            _update_nested_dict(self._update_params, d)
            for d_k in _get_keys(d):
                self._origins[d_k] = file_paths[0]
        return self

    def _safe_file_merge(self, file_1: TypePathLike, file_2: TypePathLike) \
            -> typing.Dict[str, typing.Any]:
        d1 = self.__load(pathlib.Path(file_1))
        d2 = self.__load(pathlib.Path(file_2))

        d1_keys = set(_get_keys(d1))
        d2_keys = set(_get_keys(d2))

        for d1_key in d1_keys:
            self._origins[d1_key] = file_1
            for d2_key in d2_keys:
                self._origins[d2_key] = file_2
                if d1_key.startswith(d2_key) or d2_key.startswith(d1_key):
                    raise ConflictError(((d1_key, file_1), (d2_key, file_2)))

        _update_nested_dict(d1, d2)
        return d1

    def _set_params(self):
        def __set(obj, d: typing.Dict[str, typing.Any]):
            for k, v in d.items():
                if not isinstance(v, dict):
                    object.__setattr__(obj, k, v)
                else:
                    try:
                        __set(obj.__getattribute__(k), v)
                    except AttributeError:
                        raise AttributeError(f'キー {k} が{self._default_from}で定義されていません')

        __set(self._config, self._update_params)
        object.__setattr__(self._config, '_origins', self._origins)


def _get_keys(d: typing.Dict[str, typing.Any], parent_key: str = ''):
    keys = []
    for k in d:
        if isinstance(d[k], dict):
            keys.extend(_get_keys(d[k], parent_key=f'{parent_key}/{k}'))
        else:
            keys.append(f'{parent_key}/{k}')
    return keys


def _update_nested_dict(base_dict, new_dict):
    """
    :param base_dict:
    :param new_dict:
    :return:
    """
    for k, v in new_dict.items():
        if isinstance(v, dict) and k in base_dict:
            _update_nested_dict(base_dict[k], v)
        else:
            base_dict[k] = v
