"""XRPL related interaction methods."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from xrpl.clients import WebsocketClient
from typing 	  import Optional

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
		url = "s.altnet.rippletest.net"
		if mainnet is True:
			url = "s1.ripple.com"
		XRPL_CLIENT = WebsocketClient(url)
	return XRPL_CLIENT
