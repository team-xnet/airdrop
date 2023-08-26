"""Token distribution.                                 """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.clients.json_rpc_client               import JsonRpcClient
from xrpl.models.transactions                   import Payment
from xrpl.core.addresscodec                     import is_valid_classic_address
from xrpl.transaction                           import autofill_and_sign, submit_and_wait
from xrpl.wallet                                import Wallet
from xrpl.utils                                 import xrp_to_drops
from decimal                                    import Decimal
from typing                                     import Union

ACTIVE_WALLET: Union[None, Wallet]        = None

XRPL_CLIENT:   Union[None, JsonRpcClient] = None

from airdrop import console

def get_client() -> JsonRpcClient:
    """Similar to `xrpl.get_client()` function, except it returns a JSON-RPC client instead.

    Returns:
        JsonRpcClient: XRPL JSON-RPC client.
    """

    global XRPL_CLIENT

    if isinstance(XRPL_CLIENT, type(None)):

        XRPL_CLIENT = JsonRpcClient("https://xrplcluster.com/")

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


def send_token_payment(destination: str, transaction: tuple[str, str, Decimal]) -> bool:
    """Sends any amount of arbitrary token to `destination` address.

    Args:
        destination (str): Destination address. Needs to be classic address.
        transaction (tuple[str, str, Decimal]): Actual transaction.

    Returns:
        bool: `True` if the request was successful, `False` otherwise.
    """

    client = get_client()
    wallet = get_wallet()

    issuer, token, amount = transaction

    try:
        is_valid_classic_address(destination)

    except:
        return False

    try:

        request = None

        if token.lower() == "xrp":
            request = Payment(destination=destination, account=wallet.address, amount=xrp_to_drops(amount))
            request  = autofill_and_sign(request, client, wallet)

            response = submit_and_wait(request, client)

            if not response.is_successful():
                return False

        else:
            request = Payment(
                destination=destination,
                account=wallet.address,
                amount=IssuedCurrencyAmount(
                    currency=token,
                    issuer=issuer,
                    value=str(amount)
                )
            )

            response = submit_and_wait(request, client, wallet)

            if not response.is_successful():
                return False

        return True

    except:
        return False
