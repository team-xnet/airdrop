"""Locally saved data. Includes the XRPLMeta data, and terms of use check."""
"""Author: spunk-developer <xspunk.developer@gmail.com>                   """

from os import path


from cache_to_disk import delete_disk_caches_for_function, delete_old_disk_caches
from airdrop.xrpl  import fetch_xrpl_metadata
from airdrop       import console, i18n

META_FILE_PATH:        str  = path.normpath(path.abspath(path.expanduser('~/.xnet-airdrop-meta')))

ACCEPTED_TERMS_OF_USE: bool = False

def get_terms_of_use() -> bool:
    """Gets the terms of use acceptance state.

    Returns:
        bool: `True` if the user has accepted ToU, `False` otherwise.
    """

    global ACCEPTED_TERMS_OF_USE
    return ACCEPTED_TERMS_OF_USE


def rehydrate_terms_of_use() -> None:
    """Tries to rehydrate the Terms of Use flag by reading if the acceptance file exists on disk."""

    global ACCEPTED_TERMS_OF_USE, META_FILE_PATH

    if path.isfile(META_FILE_PATH):
        ACCEPTED_TERMS_OF_USE = True
        return


def accept_terms_of_use() -> None:
    """Accepts terms of use, attempting to write result as a file on disk."""

    global ACCEPTED_TERMS_OF_USE, META_FILE_PATH

    try:
        with open(META_FILE_PATH, "w"):
            ACCEPTED_TERMS_OF_USE = True

    except:
        return


def rehydrate_metadata_cache() -> None:
    """Confirms with user if they want to use pre-existing cache or not."""

    delete_old_disk_caches()

    if not isinstance(fetch_xrpl_metadata.cache_size(), type(None)):

        user_input = console.input(i18n.rehydrate.metadata_cache)

        while True:

            if len(user_input) == 0 or user_input.lower() == "yes" or user_input.lower() == "y":
                break

            if user_input.lower() == "no" or user_input.lower() == "n":

                delete_disk_caches_for_function("fetch_xrpl_metadata")
                break

            user_input = console.input(i18n.rehydrate.metadata_error)

        console.clear()
