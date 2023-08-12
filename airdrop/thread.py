"""Multithreading code to help with aggressive rate limiting. """
"""Author: spunk-developer <xspunk.developer@gmail.com>       """

from xrpl.clients.websocket_client import WebsocketClient
from concurrent.futures            import ThreadPoolExecutor
from decimal                       import Decimal
from typing                        import Union
from time                          import sleep

from airdrop.xrpl import fetch_account_balance, get_available_client, return_client

TARGET_TOKEN: Union[None, str] = None

def fetch_trustline_balance(trustline: str) -> tuple[str, Decimal]:
    """Fetches a single trustline balance in a multithreaded context.

    Args:
        trustline (str): The given trustline which to fetch their balance for.

    Returns:
        tuple[str, Decimal]: A tuple containing the original trustline address and fetched token balance.
    """

    # Accessing a global variable from a threaded context is probably a REALLY bad idea
    # in most cases, however since we're only reading the variable it should be fine.
    #
    # If shit goes wrong, you know who to blame!
    global TARGET_TOKEN

    balance: Union[None, Decimal]         = None
    client:  Union[None, WebsocketClient] = None
    fail:    Union[None, int]             = None

    while True:
        client = get_available_client()

        if not isinstance(client, type(None)):
            break

    while True:
        try:
            if not client.is_open():
                client.open()

            balance = fetch_account_balance(trustline, TARGET_TOKEN, client)

            return_client(client)

            break

        except:
            if isinstance(fail, type(None)):
                fail = 10

            else:
                fail = fail * 2

                if fail >= 300:
                    fail = 300

            for _ in range(fail):
                sleep(1)

    return (trustline, balance)

def fetch_trustline_balances_threaded(token: str, trustlines: list[str]) -> dict[str, Decimal]:
    """Sets up a multithreaded context for fetching trustline balances from the XRPL.

    Args:
        token (str): The token in question which to get the trustline balances for.
        trustlines (list[str]): List of all trustlines which to fetch balances for.

    Returns:
        dict[str, Decimal]: Dictionary containing fetched trustline balances, which has been filtered to not include zero-balance trustlines.
    """

    global TARGET_TOKEN

    TARGET_TOKEN = token
    balances     = { }

    with ThreadPoolExecutor(max_workers=3) as pool:

        results = pool.map(fetch_trustline_balance, trustlines)

        for address, balance in results:

            # We do light filtering for trustlines that don't have anything
            if address in balances or isinstance(balance, type(None)) or balance.is_zero():
                    continue

            balances[address] = balance

    return balances
