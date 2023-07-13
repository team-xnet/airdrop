"""Calculation functions."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""
from typing import Union

def pick_balances_as_dict(balances: list[tuple[str, float]], pick: Union[str, list[str]]) -> dict[str, float]:
	"""Filters a list of XRPL balances, returning only balances that have a matching token `id` in `pick` list.

	Args:
		balances (list[tuple[str, float]]): Raw list of balances which to filter from.
		pick (Union[str, list[str]]): List of IDs (or singular string ID) which to filter.

	Returns:
		dict[str, float]: Dictionary including all picked balances with their IDs set as keys.
	"""
	picked_balances: dict[str, float] = { }
	for id, balance in balances:
		# We find the given id from balances whenever it's just a standalone ID.
		if type(pick) is str:
			if id is pick:
				picked_balances[id] = balance
				break
			continue
		elif type(pick) is list:
			if id in pick:
				picked_balances[id] = balance
			continue
	return picked_balances
