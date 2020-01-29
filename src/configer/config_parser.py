from typing import Any, Optional, Tuple
from collections import OrderedDict


class ConfigParser:
    def __init__(self):
        self.dataclasses = OrderedDict()

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
            return f'typing.Tuple[{", ".join([k for k, d in keys_and_defaults])}]', \
                   tuple([d for k, d in keys_and_defaults])

        # Dict
        # 新たなdataclassとして新規クラス名を作成する
        # 作成の際は親要素のクラス名をprefixにし、重複を防ぐ
        if isinstance(value, dict):
            if parent_class_name is None:
                self.make_dataclass_from_dict(this_class_name, value)
                parent_class_name = ''
            return parent_class_name + this_class_name, parent_class_name + this_class_name + '()'

        # primitive types
        # Python表記に直していく
        if type(value) == int:
            return 'int', value
        if type(value) == float:
            return 'float', value
        if type(value) == str:
            return 'str', f'"{value}"'
        if type(value) == bool:
            return 'bool', value
        if value is None:
            return 'None', value
        raise NotImplementedError(f'Type: {type(value)} not supported')

    def parse(self, key: str, value: Any, parent_class_name: Optional[str] = None) -> str:
        """
        key: TypeOfValue というPythonの型アノテーションを作成する
        ValueがDictのとき、DictをNamedTupleを継承したクラスに変換して型アノテーションする

        ex)
        parse('hoge', 12, None) = 'hoge: int'
        parse('fuga', {'piyo': 12}, None) = fuga: Fuga  （class Fuga(NamedTuple): piyo: int は別に作られる）
        :param key:
        :param value:
        :param parent_class_name:
        :return:
        """
        this_key_class_name = self.to_class_name(key)
        key_name, default = self.get_type_and_default(value, this_key_class_name, parent_class_name)
        return f'{key}: {key_name} = {default}'

    def make_dataclass_from_dict(self, class_name: str, _dict: dict) -> None:
        # _dictのvalueにdictの型が存在しなくなるまで掘っていく
        for k, v in _dict.items():
            if isinstance(v, dict):
                self.make_dataclass_from_dict(class_name + self.to_class_name(k), v)
            assert type(k) == str

        # _dictのkeyとvalueからdataclassを生成する
        class_def = "@dataclasses.dataclass\nclass {}:\n    {}\n".format(
            class_name, '\n    '.join([self.parse(
                k, v, parent_class_name=class_name) for k, v in _dict.items()]))
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
