"""Distribution related data parsing.                  """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from pathlib import Path
from typing  import Union

DATA_FILE_PATH: Union[None, Path] = None

META_FILE_PATH: Union[None, Path] = None


def set_data(data: Path) -> bool:
    """Sets the data file path. Does some existence checks.

    Args:
        data (Path): The actual data file path.

    Returns:
        bool: `True` if path can be set, if the file exists and IS a file, `False` otherwise.
    """

    global DATA_FILE_PATH

    if not isinstance(DATA_FILE_PATH, type(None)) or not data.exists() or not data.is_file():
        return False

    DATA_FILE_PATH = data

    return True


def set_meta(data: Path) -> bool:
    """Sets the metadata file path. Does some existence checks.

    Args:
        data (Path): The actual metadata file path.

    Returns:
        bool: `True` if path can be set, if the file exists and IS a file, `False` otherwise.
    """

    global META_FILE_PATH

    if not isinstance(META_FILE_PATH, type(None)) or not data.exists() or not data.is_file():
        return False

    META_FILE_PATH = data

    return True


def get_data() -> Union[None, Path]:
    """Returns the filepath information for the data file.

    Returns:
        Union[None, Path]: The current state of the data filepath variable.
    """

    global DATA_FILE_PATH
    return DATA_FILE_PATH


def get_meta() -> Union[None, Path]:
    """Returns the filepath information for the meta file.

    Returns:
        Union[None, Path]: The current state of the meta filepath variable.
    """

    global META_FILE_PATH
    return META_FILE_PATH
