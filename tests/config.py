﻿from typing import NamedTuple, Union, Dict, List, Optional, Any
from pathlib import Path
import toml
import yaml
try:
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
    from yaml import Loader as YamlLoader, Dumper as YamlDumper
from clint.textui import colored, puts
import random
import shutil


class ModelsBaseMLP(NamedTuple):
    in_channels: int
    middle_channels: int
    middle_depth: int
    out_channels: int
    activation: str
    last_activation: str
    drop_out: float
    batch_norm: bool


class Models(NamedTuple):
    BaseMLP: ModelsBaseMLP


class OptimizerAdam(NamedTuple):
    alpha: float
    beta: float


class Optimizer(NamedTuple):
    adam: OptimizerAdam


class Training(NamedTuple):
    batchsize: int
    loss: str
    scheduler: str


class Config(NamedTuple):
    models: Models
    use_model: str
    optimizer: Optimizer
    training: Training

    __sduiyvcaishrugoasdgo = Path('.')

    @staticmethod
    def load(path: Union[Path, str]):
        """load setting file and convert it to Config class"""
        setting_path = path
        "load latest default values from toml file"
        assert isinstance(setting_path, Path) or isinstance(setting_path, str), "setting_path must be Pathlike {}".format(type(setting_path))
        setting_path = Path(setting_path)
        assert setting_path.is_file(), "setting_path should be a path to setting file {}".format(setting_path)
        # Load Setting
        if setting_path.suffix == '.toml':
            with setting_path.open('r') as f:
                params = toml.load(f)
        elif setting_path.suffix == '.yaml' or setting_path.suffix == '.yml':
            with setting_path.open('r') as f:
                params = yaml.load(f, Loader=YamlLoader)
        else:
            raise RuntimeError('Not support type (Toml / Yaml)')
        Config.__sduiyvcaishrugoasdgo = path
        return Config(**Config.__convert_dict_to_namedtuple(params))

    def pprint(self, wait_yes: bool):
        """print setting values"""
        for field in self._fields:
            current_config_value = self.__getattribute__(field)
            # 現在のソースコードに書かれている値と設定値が一致
            puts("{}\t{}".format(colored.blue(field), colored.green(str(current_config_value))))
        if wait_yes:
            random_code = ''.join(random.choices([str(i) for i in range(10)], k=3))
            ans = input('Check setting values. If these are OK, you input this one-time code [{}] > '.format(random_code))
            if ans == random_code:
                return
            else:
                print("OK, now re-check your settings.")
                exit()

    @staticmethod
    def save(out_dir: Union[Path, str]):
        """save setting values"""
        out_dir = Path(out_dir)
        shutil.copy2(str(Config.__sduiyvcaishrugoasdgo.resolve()), str(out_dir / Config.__sduiyvcaishrugoasdgo.split('/')[-1]))

    @staticmethod
    def __convert_dict_to_namedtuple(params):
        for key, val in params.items():
            if isinstance(val, dict):
                params[key] = Config.__to_named_tuple(key, val)
        return params

    @staticmethod
    def __to_named_tuple(key, value: dict):
        key = key[0].capitalize() + key[1:]
        for k, v in value.items():
            if isinstance(v, dict):
                value[k] = Config.__to_named_tuple(
                    key + ''.join([_k[0].capitalize() + _k[1:] for _k in k.split('_')]), v)
        return globals()[key](**value)