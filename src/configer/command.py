from pathlib import Path
from argparse import ArgumentParser
import hashlib

from jinja2 import Environment, FileSystemLoader
import toml
import yaml

try:
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
    from yaml import Loader as YamlLoader, Dumper as YamlDumper
from clint.textui import colored, puts

from .config_parser import ConfigParser


lock_file_path = Path('.config.lock')


class Configer:
    @staticmethod
    def load_setting(setting_file_path: Path):
        """
        :param setting_file_path: 指定された設定値へのpath
        :return: dict パースされた辞書データ
        """
        assert setting_file_path.is_file(), setting_file_path
        if setting_file_path.suffix == '.toml':
            with setting_file_path.open('r') as f:
                setting = toml.load(f)
        elif setting_file_path.suffix == '.yaml' or setting_file_path.suffix == '.yml':
            with setting_file_path.open('r') as f:
                setting = yaml.load(f, Loader=YamlLoader)
        else:
            raise RuntimeError('Not support type (Toml / Yaml)')
        return setting

    @staticmethod
    def hash_md5(setting_file_path: Path) -> str:
        """
        設定ファイルの変更を追跡するためにhashを作成している
        :param setting_file_path:
        :return:
        """
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with setting_file_path.open('rb') as f:
            buf = f.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(BLOCKSIZE)
        return hasher.hexdigest()

    @staticmethod
    def create(args):
        """create config.py form setting.toml and generate config.py"""
        setting_file = args.setting
        output_file = args.output
        Configer.create_from_files(Path(setting_file), Path(output_file))

    @staticmethod
    def update(args):
        """logファイル内のすべてのファイルについてhashから変更を検出し更新をかける"""
        if not lock_file_path.is_file():
            print("You should create config.py from setting.toml")
            exit()

        with lock_file_path.open('r') as f:
            registered_setting_files = yaml.load(f, Loader=YamlLoader)
            for registered_setting_file, contents in registered_setting_files.items():
                previous_hash = contents['hash_value']
                output_file = contents['output']

                current_hash = Configer.hash_md5(Path(registered_setting_file))

                if current_hash != previous_hash:
                    Configer.create_from_files(Path(registered_setting_file), Path(output_file))
                    puts(colored.yellow(f'Updated {registered_setting_file}'))
                else:
                    puts(colored.green(f'No changes in {registered_setting_file}'))

    @staticmethod
    def create_from_files(setting_file_path: Path, output_file_path: Path):
        assert setting_file_path.is_file(), setting_file_path

        template_file = Path(__file__).parent / 'template' / 'config.py.j2'
        assert template_file.is_file(), str(template_file)

        # Load template.
        env = Environment(loader=FileSystemLoader(searchpath=str(template_file.parent), encoding='utf_8_sig'))
        tpl = env.get_template(str(template_file.name))

        # Load Setting
        config_parser = ConfigParser()
        setting = Configer.load_setting(setting_file_path)
        params = [config_parser.parse(k, v, parent_class_name=None) for k, v in setting.items()]

        # Render
        render = tpl.render(
            {'params': params, 'sduiyvcaishrugoasdgo': setting_file_path,
             'named_tuples': list(config_parser.named_tuples.values())})
        # Output
        with output_file_path.open('w', encoding='utf_8_sig') as stream:
            stream.write(render)
        # Logging
        # 一度中身を読み込み、既に登録済みであれば更新、なければ新規作成する
        if lock_file_path.is_file():
            with open(lock_file_path, 'r') as f:
                current_contents = yaml.load(f, Loader=YamlLoader)
                if not isinstance(current_contents, dict):
                    current_contents = {}
        else:
            current_contents = {}
        with open(lock_file_path, 'w') as f:
            current_contents[str(setting_file_path)] = {
                    'hash_value': Configer.hash_md5(setting_file_path),
                    'output': str(output_file_path)
                }
            yaml.dump(current_contents, f, Dumper=YamlDumper)


def get_arg_parser():
    parser = ArgumentParser(description='configer command')
    subparsers = parser.add_subparsers()

    # config create
    config_create = subparsers.add_parser(
        'create', help='create config.py from your setting.toml')
    config_create.add_argument(
        '-s', '--setting', required=False, type=str, help='path to setting file [toml]', default='setting/setting.toml')
    config_create.add_argument(
        '-o', '--output', required=False, type=str, help='path to output config file [python]', default='config.py')
    config_create.set_defaults(handler=Configer.create)

    config_update = subparsers.add_parser('update', help='update your config file [python]')
    config_update.set_defaults(handler=Configer.update)
    return parser


def main():
    # コマンドライン引数をパースして対応するハンドラ関数を実行
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        arg_parser.print_help()
