import pathlib
import hashlib

def hash_md5(setting_file_path: pathlib.Path) -> str:
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
