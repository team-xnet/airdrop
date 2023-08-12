"""CSV generation related methods.                     """
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

                elif exc.errno in { ENAMETOOLONG, ERANGE }:
                    return False

    except TypeError as exc:
        return False

    else:
        return True


def generate_metadata(output_path: str, data: list[str]) -> bool:
    """Generates a simple `txt` file containing `data`.

    Args:
        output_path (str): The path where to put the actual file.
        data (list[str]): Data to print into the file. Each element in the list represents a new line.

    Returns:
        bool: `True` if file was written succesfully, `False` otherwise.
    """

    if isinstance(output_path, type(None)):
        return

    if output_path.endswith(path.sep):
        output_path = f'{ path }airdrop_metadata.txt'

    elif not  output_path.endswith(".txt"):
        output_path = f'{ output_path + path.sep }airdrop_metadata.txt'

    try:
        with open(Path(output_path).resolve(), "w", encoding="UTF8", newline="") as file:

            for line in data:
                file.write(f'{ line }\n')

            return True

    except:
        return False


def generate_csv(output_path: str, headers: list[str], data: list[dict]) -> bool:
    """Generates and writes given `data` dictionary into `path`.

    Args:
        path (str): Output path for the CSV file. Must also include the
        headers (str): The headers for the file. The `data` list dictionaries must use the header elements as their keys.
        data (dict): CSV data itself.

    Returns:
        bool: `True` if the file was written successfully, `False` otherwise.
    """

    if isinstance(output_path, type(None)):
        return

    if output_path.endswith(path.sep):
        output_path = f'{ path }airdrop_data.csv'

    elif not  output_path.endswith(".csv"):
        output_path = f'{ output_path + path.sep }airdrop_data.csv'

    try:
        with open(Path(output_path).resolve(), "w", encoding="UTF8", newline="") as file:

            writer = DictWriter(file, fieldnames=headers)

            writer.writeheader()
            writer.writerows(data)

            return True
    except:
        return False


def get_csv() -> Union[None, str]:
    """Returns the CSV path.

    Returns:
        Union[None, str]: CSV path.
    """

    global CSV_OUTPUT_PATH
    return CSV_OUTPUT_PATH
