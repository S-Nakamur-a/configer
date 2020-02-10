# no include
import typing
from .type_hint import TypePathLike


# no include
class ConfigerError(Exception):
    pass


class ConflictError(ConfigerError):
    def __init__(self, key_and_origins: typing.Tuple[typing.Tuple[str, TypePathLike], typing.Tuple[str, TypePathLike]]):
        super(ConflictError, self).__init__(
            f"Detect conflict. Check {key_and_origins[0][0]} in {key_and_origins[0][1]}"
            f" and {key_and_origins[1][0]} in {key_and_origins[1][1]}")


class ChangeDefaultError(ConfigerError):
    def __init__(self, default_file: TypePathLike):
        super(ChangeDefaultError, self).__init__(
            f'you might be update {default_file}. If so, please run `configer update`')


class InvalidTypeError(ConfigerError):
    def __init__(self, key: str, expected_type: str, actual_type: str):
        super(InvalidTypeError, self).__init__(f"{key} is expected {expected_type}, actual {actual_type}")
