"""Distribution related data parsing.                  """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from pathlib import Path
from decimal import Decimal
from typing  import Union
from csv     import reader

DATA_FILE_CONTENTS: Union[None, dict[str, Decimal]] = None

META_FILE_CONTENTS: Union[None, dict[str, Decimal]] = None

DATA_FILE_PATH: Union[None, Path]                   = None

META_FILE_PATH: Union[None, Path]                   = None


def get_path() -> Union[None, Path]:
    """Returns the data file path.

    Returns:
        Union[None, Path]: Data file path current state.
    """

    global DATA_FILE_PATH
    return DATA_FILE_PATH


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


def get_data() -> Union[None, list[dict[str, Union[str, Decimal, tuple[str, Decimal]]]]]:
    """Returns the file contents of the data file.

    Returns:
        Union[None, Path]: The current state of the data file.
    """

    global DATA_FILE_CONTENTS
    return DATA_FILE_CONTENTS


def get_meta() -> Union[None, dict[str, Decimal]]:
    """Returns the file contents of the metadata file.

    Returns:
        Union[None, Path]: The current state of the meta file.
    """

    global META_FILE_CONTENTS
    return META_FILE_CONTENTS


def validate_metadata() -> bool:
    """Validates generated metadata file's contents while also parsing them.

    Returns:
        bool: `True` if all required lines are present and got parsed successfully, `False` otherwise.
    """

    global META_FILE_CONTENTS, META_FILE_PATH

    meta_file: Union[None, list[str]] = None
    data:      dict[str, Decimal]     = { }

    item_keys: list[str] = [
        "Filtered trustlines",
        "Fetched trustlines",
        "Trustline sum",
        "Airdrop ratio"
    ]

    try:
        with open(META_FILE_PATH) as file:

            meta_file = file.read().splitlines()

            if len(meta_file) <= 0:
                return False

        # We filter out the elapsed time due to it being cosmetic only
        meta_file       = list(filter(lambda item: "Total elapsed time" not in item, meta_file))
        validated_keys = item_keys.copy()

        for line in meta_file:

            if len(validated_keys) <= 0:
                return False

            for key in validated_keys:

                if key in line:
                    validated_keys.remove(key)
                    break

                if meta_file.index(line) == len(meta_file) - 1 and meta_file.index(key) == len(validated_keys) - 1:
                    return False

        if len(validated_keys) >= 1:
            return False

        for line in meta_file:

            idx = item_keys[meta_file.index(line)]

            # Sequential string cleanup
            line = line.replace(idx, '')
            line = line.replace(':', '')
            line = line.strip()

            line = Decimal(line)
            key  = None

            if idx == "Filtered trustlines":
                key = "filtered"

            elif idx == "Fetched trustlines":
                key = "fetched"

            elif idx == "Airdrop ratio":
                key = "ratio"

            elif idx == "Trustline sum":
                key = "sum"

            if key in data:
                continue

            data[key] = line

        META_FILE_CONTENTS = data

        return True

    except:
        return False


def validate_data() -> bool:
    """Validates and categorizes the actual airdrop data.

    Returns:
        bool: `True` if the data has been validated and parsed correctly, `False` otherwise.
    """

    global DATA_FILE_CONTENTS, DATA_FILE_PATH

    data_file: Union[None, list[str]] = None

    try:
        with open(DATA_FILE_PATH) as file:

            data_file     = file.read().splitlines()
            currency_code = None
            first_iter    = True
            data          = [ ]

            data_fields = [
                "address",
                "currency",
                "yield",
                "split"
            ]

            for row in reader(data_file):

                if first_iter:

                    first_iter = False

                    for label in row:

                        if label.lower() not in data_fields:

                            currency_code = label

                            break

                    continue

                object = { }

                for column in row:

                    idx = row.index(column)

                    if data_fields[idx] == 'address':

                        object[data_fields[idx]] = column

                        continue

                    elif data_fields[idx] == 'currency':

                        object[data_fields[idx]] = (currency_code, Decimal(column))

                        continue

                    if column.endswith('%'):
                        column = column[:-1]

                    value = Decimal(column)

                    object[data_fields[idx]] = value

                data.append(object)

            data_file = data

        DATA_FILE_CONTENTS = data_file

        return True

    except:
        return False
