# no include
import pathlib
import hashlib


# no include
def hash_md5(setting_file_path: pathlib.Path) -> str:
    """
    設定ファイルの変更を追跡するためにhashを作成している
    :param setting_file_path:
    :return:
    """
    block_size = 65536
    hasher = hashlib.md5()
    with setting_file_path.open('rb') as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(block_size)
    return hasher.hexdigest()
