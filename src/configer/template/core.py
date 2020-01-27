import typing
import pathlib
import toml
import yaml
import dataclasses
from clint import textui
import random
import shutil


@dataclasses.dataclass(frozen=True)
class Config(_Config):
    origin_config_path: typing.ClassVar[pathlib.Path] = pathlib.Path()

    def __post_init__(self):
        def get_type_error_message(key: str, expected_type: str, actual_type: str):
            return f"{key} is expected {expected_type}, actual {actual_type}"

        def check_type(obj: dataclasses.dataclass):
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
                    check_type(child_obj)
                if child_obj is None and (field.type is None):
                    continue
                assert type(child_obj) == field.type, \
                    get_type_error_message(field.name, str(field.type), str(type(child_obj)))
        try:
            check_type(self)
        except AssertionError as e:
            print(e)
            exit(1)

    @staticmethod
    def load(path: typing.Union[pathlib.Path, str]):
        """load setting file and convert it to Config class"""
        setting_path = path
        assert isinstance(setting_path, pathlib.Path) \
               or isinstance(setting_path, str), \
            "setting_path must be pathlib.Pathlike {}".format(type(setting_path))
        setting_path = pathlib.Path(setting_path)
        assert setting_path.is_file(), \
            "setting_path should be a path to setting file {}".format(setting_path)
        # Load Setting
        if setting_path.suffix == '.toml':
            with setting_path.open('r') as f:
                params = toml.load(f)
        elif setting_path.suffix == '.yaml' or setting_path.suffix == '.yml':
            with setting_path.open('r') as f:
                params = yaml.safe_load(f)
        else:
            raise RuntimeError('Not support type (Toml / Yaml)')
        Config.origin_config_path = path
        return Config(**Config.__convert_to_proper_name(params))

    def pprint(self, wait_yes: bool):
        """print setting values"""

        def print_dict(d: dict, depth: int = 0):
            for k, v in d.items():
                if isinstance(v, dict):
                    textui.puts("{}{}".format(
                        '\t' * depth,
                        textui.colored.blue(k)))
                    print_dict(v, depth + 1)
                else:
                    textui.puts("{}{}\t{}".format(
                        '\t' * depth,
                        textui.colored.blue(k),
                        textui.colored.green(str(v))))

        print_dict(dataclasses.asdict(self), 0)

        if wait_yes:
            random_code = ''.join(random.choices([str(i) for i in range(10)], k=3))
            ans = input(
                'Check setting values. If these are OK, you input this one-time code [{}] > '.format(random_code))
            if ans == random_code:
                return
            else:
                print("OK, now re-check your settings.")
                exit()

    @staticmethod
    def save(out_dir: typing.Union[pathlib.Path, str]):
        """save setting values"""
        out_dir = pathlib.Path(out_dir)
        shutil.copy2(str(Config.origin_config_path.resolve()),
                     str(out_dir / Config.origin_config_path.name))

    @staticmethod
    def __convert_to_proper_name(params):
        for key, val in params.items():
            if isinstance(val, dict):
                params[key] = Config.__to_proper(key, val)
        return params

    @staticmethod
    def __to_proper(key, value: dict):
        key = key[0].capitalize() + key[1:]
        for k, v in value.items():
            if isinstance(v, dict):
                value[k] = Config.__to_proper(
                    key + ''.join([_k[0].capitalize() + _k[1:] for _k in k.split('_')]), v)
        return globals()[key](**value)
