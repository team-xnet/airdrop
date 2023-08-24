"""Token distribution.                                 """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from xrpl.clients.json_rpc_client import JsonRpcClient
from xrpl.wallet                  import Wallet
from typing                       import Union

ACTIVE_WALLET: Union[None, Wallet]        = None

XRPL_CLIENT:   Union[None, JsonRpcClient] = None


def get_client() -> JsonRpcClient:
    """Similar to `xrpl.get_client()` function, except it returns a JSON-RPC client instead.

    Returns:
        JsonRpcClient: XRPL JSON-RPC client.
    """

    global XRPL_CLIENT

    if isinstance(XRPL_CLIENT, type(None)):

        # @TODO(spunk-developer): Once it's release time change this to production URL!
        XRPL_CLIENT = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

    return XRPL_CLIENT


def get_wallet() -> Union[None, Wallet]:
    """Returns the currently active wallet.

    Returns:
        Union[None, Wallet]: Current wallet state.
    """

    global ACTIVE_WALLET
    return ACTIVE_WALLET


def register_wallet(seed: str) -> bool:
    """Sets the currently used wallet based on the secret (seed).

    Args:
        seed (str): The seed itself.

    Returns:
        bool: `True` if the seed is valid and wallet could be created, `False` otherwise.
    """

    global ACTIVE_WALLET

    if not isinstance(ACTIVE_WALLET, type(None)):
        return False

    try:
        ACTIVE_WALLET = Wallet.from_seed(seed)

        return True

    except:
        return False
