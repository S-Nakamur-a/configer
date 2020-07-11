from typing import Any, Optional, Tuple
from collections import OrderedDict


class ConfigParser:
    def __init__(self):
        self.dataclasses = OrderedDict()
        self.post_inits = []

    def get_type_and_default(self, value: Any, this_class_name: Optional[str] = None, parent_class_name: Optional[str] = None)\
            -> Tuple[str, Any]:
        """
        設定ファイルから型名を得る
        :param value: 設定値そのもの
        :param this_class_name:
        :param parent_class_name:
        :return:
        """

        # List, Tuple
        # Tupleとして保存し、各要素の型を記述する
        if isinstance(value, list) or isinstance(value, tuple):
            keys_and_defaults = [self.get_type_and_default(v, this_class_name) for v in value]
            return f'typing.Tuple[{", ".join([k for k, d in keys_and_defaults])}]',\
                   f'({", ".join(tuple([str(d) for k, d in keys_and_defaults]))})'


        # Dict
        # 新たなdataclassとして新規クラス名を作成する
        # 作成の際は親要素のクラス名をprefixにし、重複を防ぐ
        if isinstance(value, dict):
            if parent_class_name is None:
                self.make_dataclass_from_dict(this_class_name, value)
                parent_class_name = ''
            return parent_class_name + this_class_name, None

        # primitive types
        # Python表記に直していく
        if type(value) == int:
            return 'int', value
        if type(value) == float:
            return 'float', value
        if type(value) == str:
            return 'str', f'\'{value}\''
        if type(value) == bool:
            return 'bool', value
        if value is None:
            return 'None', 'None'
        raise NotImplementedError(f'Type: {type(value)} not supported')

    def parse(self, key_name: str, value: Any, parent_class_name: Optional[str] = None) -> str:
        """
        ex)
        parse('hoge', 12, None) = 'hoge: int = 12'
        :param key_name:
        :param value:
        :param parent_class_name:
        :return:
        """
        assert key_name.isidentifier(), f'{key_name} is not a valid Python identifier'
        if key_name.lower() != key_name:
            print("Sorry, all key names must be in lowercase.")
        key_class_name = self.to_class_name(key_name)
        key_type_name, default_value = self.get_type_and_default(value, key_class_name, parent_class_name)
        if default_value is None:
            self.post_inits.append(f"super().__setattr__('{key_name}', {key_type_name}())")
            return f'{key_name}: {key_type_name} = dataclasses.field(init=False)'
        return f'{key_name}: {key_type_name} = {default_value}'

    def make_dataclass_from_dict(self, class_name: str, class_setting_values: dict) -> None:
        # _dictのvalueにdictの型が存在しなくなるまで掘っていく
        for k, v in class_setting_values.items():
            if isinstance(v, dict):
                self.make_dataclass_from_dict(class_name + self.to_class_name(k), v)
        # _dictのkeyとvalueからdataclassを生成する
        self.post_inits.clear()
        members = [self.parse(k, v, parent_class_name=class_name) for k, v in class_setting_values.items()]
        indent = "    "
        members = f'\n{indent}'.join(members)
        if len(self.post_inits) > 0:
            post_inits = f'\n{indent}{indent}'.join([f'{pi}' for pi in self.post_inits])
            class_def = f"@dataclasses.dataclass(frozen=True)\n" \
                        f"class {class_name}:\n" \
                        f"{indent}{members}\n\n" \
                        f"{indent}def __post_init__(self):\n" \
                        f"{indent}{indent}{post_inits}"
        else:
            class_def = f"@dataclasses.dataclass(frozen=True)\n" \
                        f"class {class_name}:\n" \
                        f"{indent}{members}"
        # 既に登録済みのclassはスルーする
        if class_name in self.dataclasses and len(self.dataclasses[class_name]) > len(class_def):
            return
        self.dataclasses[class_name] = class_def

    @staticmethod
    def to_class_name(key: str):
        """
        ex) cat_dog -> CatDog
        """
        return ''.join([k[0].capitalize() + k[1:] for k in key.split('_')])
