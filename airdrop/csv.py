"""CSV generation related methods."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from pathlib import Path
from typing  import Union
from errno   import ENAMETOOLONG, ERANGE
from sys     import platform
from csv     import DictWriter
from os      import environ, lstat, path

CSV_OUTPUT_PATH: Union[None, str] = None

def set_output_path(path: str) -> bool:
    """Sets the CSV file output path to given input.

    Args:
        path (str): The path itself. If it doesn't end with `.csv` we automatically append the format.

    Returns:
        bool: `True` if the path hasn't been defined previously, `False` otherwise
    """

    global CSV_OUTPUT_PATH

    if not path.endswith(".csv"):
        path = f'{ path }.csv'

    if not isinstance(CSV_OUTPUT_PATH, type(None)):
        return False

    CSV_OUTPUT_PATH = path

    return True


def is_path_valid(pathname: str) -> bool:
    """Tests any given path independently from the operating system to see if it is valid.

    Args:
        pathname (str): Given pathname to test.

    Returns:
        bool: `True` if `pathname` is valid, `False` otherwise.
    """

    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        _, pathname = path.splitdrive(pathname)

        root_dirname = environ.get('HOMEDRIVE', 'C:') \
            if platform == 'win32' else path.sep

        assert path.isdir(root_dirname)

        root_dirname = root_dirname.rstrip(path.sep) + path.sep

        for pathname_part in pathname.split(path.sep):
            try:
                lstat(root_dirname + pathname_part)

            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == 123:
                        return False

                elif exc.errno in { ENAMETOOLONG, ERANGE}:
                    return False

    except TypeError as exc:
        return False

    else:
        return True


def generate_csv(data: list[dict], path: str) -> bool:
    """Generates and writes given `data` dictionary into `path`.

    Args:
        data (dict): CSV data itself. The dictionary structure must be as follows: Address: str, SOLO: int, XRP: int, Ratio: int, Split: str
        path (str): Output path for the CSV file. Must also include the
    """

    global CSV_OUTPUT_PATH

    if isinstance(CSV_OUTPUT_PATH, type(None)):
        return

    try:
        with open(Path(path).resolve(), "w", encoding="UTF8", newline="") as file:
            columns = ["Address", "SOLO", "XRP", "Ratio", "Split"]
            writer = DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
            return True
    except:
        return False
