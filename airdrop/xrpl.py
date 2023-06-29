"""XRPL related interaction methods."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from xrpl.clients 						import WebsocketClient
from xrpl.models.requests.account_lines import AccountLines
from xrpl.models.requests.account_info  import AccountInfo
from dataclasses                        import dataclass
from typing 	  						import Optional

# XRPL WebSocket client
XRPL_CLIENT = None

def get_client(mainnet: Optional[bool]) -> WebsocketClient:
	"""Returns an active XRPL WebSocket client, or creates a new one if no active client exists.

	Args:
		mainnet (Optional[bool]): Enables production operations on the actual live XRPL.

	Returns:
		WebsocketClient: XRPL API WebSocket client.
	"""
	global XRPL_CLIENT
	if XRPL_CLIENT is None:
		url = "wss://s.altnet.rippletest.net"
		if mainnet is True:
			url = "wss://s1.ripple.com"
		XRPL_CLIENT = WebsocketClient(url)
	return XRPL_CLIENT

def fetch_trustlines(address: str, client: WebsocketClient) -> list[(str, str)]:
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
	# We use a while loop due to having paginated responses.
	while True:
		for trustline in response.result["lines"]:
			if trustline["currency"] != "584E455400000000000000000000000000000000" or trustline["account"] in results:
				continue
			results.append(trustline["account"])
		if "marker" not in response.result:
			break
		request  = AccountLines(account=address, ledger_index=response.result["ledger_index"], marker=response.result["marker"])
		response = client.request(request)
	return results

def fetch_account_balances(address: str, client: WebsocketClient) -> tuple[str, list[tuple[str, float]]]:
	"""Fetches XRP balance & ALL trustline token balances for a given account.

	Args:
		address (str): The actual account which we want to fetch balance information for.
		client (WebsocketClient): Request WebSocket client.

	Raises:
		AssertionError: If any of the requests fail.

	Returns:
		tuple[str, list[tuple[str, float]]]: A tuple containing the original account address and a list of tuples containing all tokens and balances.
	"""
	balances = []
	# Fetch base XRP balance.
	request  = AccountInfo(account=address, ledger_index="validated")
	response = client.request(request)
	if not response.is_successful() or not response.is_valid():
		raise AssertionError
	balance = response.result["account_data"]["Balance"]
	# We have to parse the balance manually if it hasn't been already.
	# And since balance can be fractions of a token, it needs to be parsed as a float.
	if not type(balance) is float:
		balance = float(balance)
	balances.append(("XRP", balance))
	# Fetch all community token balances.
	request  = AccountLines(account=address, ledger_index="validated")
	response = client.request(request)
	if not response.is_successful() or not response.is_valid():
		raise AssertionError
	while True:
		for trustline in response.result["lines"]:
			balance = trustline["balance"]
			# Convert balance into float so we can do arithmetic on it.
			if not type(balance) is float:
				balance = float(balance)
			balances.append((trustline["currency"], balance))
		if "marker" not in response.result:
			break
		request  = AccountLines(account=address, ledger_index=response.result["ledger_index"], marker=response.result["marker"])
		response = client.request(request)
	return (address, balances)
