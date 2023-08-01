"""XRPL related interaction methods.                   """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from xrpl.models.requests.account_lines import AccountLines
from xrpl.models.requests.account_info  import AccountInfo
from xrpl.utils                         import drops_to_xrp
from cache_to_disk                      import cache_to_disk, NoCacheCondition
from xrpl.clients                       import WebsocketClient
from requests                           import get
from decimal                            import Decimal
from typing                             import Union

from airdrop import console

SELECTED_TRUSTLINE: Union[None, tuple[str, str]]              = None

YIELDING_TOKEN:     Union[None, tuple[str, Union[None, str]]] = None

XRPL_CLIENT:        Union[None, WebsocketClient]              = None

def get_issuer() -> Union[None, tuple[str, Union[None, str]]]:
    """Returns the current state for the issuer token.

    Returns:
        Union[None, tuple[str, Union[None, str]]]: Current issuer token state.
    """

    global SELECTED_TRUSTLINE
    return SELECTED_TRUSTLINE


def get_yielding() -> Union[None, tuple[str, Union[None, str]]]:
    """Returns the current state for the yielding token.

    Returns:
        Union[None, tuple[str, str]]: Current yielding token state.
    """

    global YIELDING_TOKEN
    return YIELDING_TOKEN


def update_issuing_metadata(address: str, currency: str) -> bool:
    """Updates source issuing address if it hasn't been set already.

    Args:
        address (str): Source issuing address.
        currency (str): Target token identifier.

    Returns:
        bool: `True` if issuing data hasn't been set, otherwise returns `False`.
    """

    global SELECTED_TRUSTLINE

    if not isinstance(SELECTED_TRUSTLINE, type(None)):
        return False

    SELECTED_TRUSTLINE = (address, currency)

    return True


def update_yielding_token(currency: str, name: Union[None, str]) -> bool:
    """Updates the currency identifier which we use to calculate the total yield per token for the entire airdrop.

    Args:
        currency (str): Currency ID to update with.

    Returns:
        bool: `True` if currency identifier hasn't been set, otherwise returns `False`.
    """

    global YIELDING_TOKEN

    if not isinstance(YIELDING_TOKEN, type(None)):
        return False

    YIELDING_TOKEN = (currency, name)

    return True


def get_client() -> WebsocketClient:
    """Returns an active XRPL WebSocket client, or creates a new one if no active client exists.

    Returns:
        WebsocketClient: XRPL API WebSocket client.
    """
    global XRPL_CLIENT

    if isinstance(XRPL_CLIENT, type(None)):
        XRPL_CLIENT = WebsocketClient("wss://xrplcluster.com/")

    return XRPL_CLIENT


@cache_to_disk()
def fetch_xrpl_metadata() -> dict[str, list[tuple[str, Union[None, str]]]]:
    """Fetches all token metadata from XRPMetadata.

    Returns:
        dict[str, list[tuple[str, Union[None, str]]]]: Dictionary containing issuing addresses and all the tokens they've issued as a tuple list.

    Raises:
        NoCacheCondition: If the HTTP request(s) fail we disable caching for the output.
    """

    results: dict[str, list[tuple[str, Union[None, str]]]] = { }

    iter_step  = 100
    iterations = 0

    response = get("https://s1.xrplmeta.org/tokens", params={ "limit": iter_step, "trust_level": [ 1, 2, 3 ] }).json()

    try:
        while True:

            for token in response["tokens"]:

                metadata = token["meta"]["token"]
                issuer   = token["issuer"]

                if token["issuer"] not in results:
                    results[issuer] = [ ]

                    id   = token["currency"]
                    name = None

                    if "name" in metadata:
                        name = metadata["name"]

                    results[issuer].append((id, name))

            if response["count"] <= iterations:
                break

            response = get("https://s1.xrplmeta.org/tokens", params={ "limit": iter_step, "trust_level": [ 1, 2, 3 ], "offset": iterations }).json()
            iterations += iter_step

        return results

    except:
        raise NoCacheCondition()


def fetch_trustlines(address: str, token_id: str, client: WebsocketClient) -> list[(str, str)]:
    """Fetches all registered trustlines for XNET token for a given XRPL account.

    Args:
        address (str):            Public address of the queried account.
        client (WebsocketClient): WebSocket XRPL client.

    Raises:
        AssertionError: Upon non-successful or invalid response.

    Returns:
        list[(str, str)]: List of all unique trustlines.
    """

    request  = AccountLines(account=address, ledger_index="validated")
    response = client.request(request)

    # We throw if the XRPL considers this request to be unsuccessful, or the data to be invalid.
    if not response.is_successful() or not response.is_valid():
        raise AssertionError

    results: list[str] = []

    while True:
        for trustline in response.result["lines"]:
            if trustline["currency"] != token_id or trustline["account"] in results:
                continue

            results.append(trustline["account"])

        if "marker" not in response.result:
            break

        request  = AccountLines(account=address, ledger_index=response.result["ledger_index"], marker=response.result["marker"])
        response = client.request(request)

    return results


def fetch_account_balance(address: str, token: str, client: WebsocketClient) -> Decimal:
    """Fetches XRP balance & ALL trustline token balances for a given account.

    Args:
        address (str): The actual account which we want to fetch balance information for.
        client (WebsocketClient): Request WebSocket client.

    Raises:
        AssertionError: If any of the requests fail.

    Returns:
        tuple[str, list[tuple[str, float]]]: A tuple containing the original account address and a list of tuples containing all tokens and balances.
    """

    if token.lower() == "xrp":
        request  = AccountInfo(account=address, ledger_index="validated")
        response = client.request(request)

        if not response.is_successful() or not response.is_valid():
            raise AssertionError

        balance = response.result["account_data"]["Balance"]

        if isinstance(balance, type(None)):
            raise AssertionError

        return drops_to_xrp(balance)

    request  = AccountLines(account=address, ledger_index="validated")
    response = client.request(request)

    if not response.is_successful() or not response.is_valid():
        raise AssertionError

    while True:
        for trustline in response.result["lines"]:

            if trustline["currency"] != token:
                continue

            balance = trustline["balance"]

            try:
                if not isinstance(balance, type(Decimal)):
                    balance = Decimal(balance)

            except:
                balance = Decimal()

            return balance

        if "marker" not in response.result:
            break

        request  = AccountLines(account=address, ledger_index=response.result["ledger_index"], marker=response.result["marker"])
        response = client.request(request)
