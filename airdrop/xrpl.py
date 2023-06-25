"""XRPL related interaction methods."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from xrpl.clients 						import WebsocketClient
from xrpl.models.requests.account_lines import AccountLines
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

def fetch_trustlines(address: str, client: WebsocketClient):
	"""Fetches all registered trustlines for XNET token for a given XRPL account.

	Args:
		address (str):            Public address of the queried account.
		client (WebsocketClient): WebSocket XRPL client.

	Raises:
		AssertionError: Upon non-successful or invalid response.

	Returns:
		list[dict]: List of all unique trustlines.
	"""
	request  = AccountLines(account=address, ledger_index="validated")
	response = client.request(request)
	# We throw if the XRPL considers this request to be unsuccessful, or the data to be invalid.
	if not response.is_successful() or not response.is_valid():
		raise AssertionError
	results: list[dict] = []
	# We use a while loop due to having paginated responses.
	while True:
		for trustline in response.result["lines"]:
			if trustline["currency"] != "584E455400000000000000000000000000000000" or trustline in results:
				continue
			results.append(trustline)
		if "marker" not in response.result:
			break
		request  = AccountLines(account=address, ledger_index=response.result["ledger_index"], marker=response.result["marker"])
		response = client.request(request)
	return results
