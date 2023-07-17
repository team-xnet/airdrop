"""Calculation functions."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""
from typing import Union

TOTAL_BALANCES: dict[str, float] = { }

AIRDROP_AMOUNT: Union[None, float, int] = None

AIRDROP_YIELD_PER_TOKEN: Union[None, tuple[str, float]] = None

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

def update_budget(budget: Union[float, int]) -> bool:
	"""Updates the total airdroppable budget.

	Args:
		budget (Union[float, int]): The budget of the total airdrop.

	Returns:
		bool: `True` if budget hasn't been set already, otherwise returns `False`.
	"""
	global AIRDROP_AMOUNT
	if not isinstance(AIRDROP_AMOUNT, type(None)):
		return False
	AIRDROP_AMOUNT = budget
	return True

def increment_yield(id: str, amount: float) -> None:
	"""Increments internal total balance for a given currency.

	Args:
		id (str): Currency identifier.
		amount (float): The amount to increment by.
	"""
	global TOTAL_BALANCES
	if id in TOTAL_BALANCES:
		TOTAL_BALANCES[id] += amount
		return
	TOTAL_BALANCES[id] = amount

def calculate_total_yield(id: str) -> bool:
	"""Calculates the total yield per token for the entire airdrop.

	Args:
		id (str): The identifier of the yielding token.

	Returns:
		bool: If the prequisites haven't been set, the function returns `False`. Otherwise `True`.
	"""
	global AIRDROP_YIELD_PER_TOKEN, AIRDROP_AMOUNT, TOTAL_BALANCES
	if type(AIRDROP_YIELD_PER_TOKEN) is tuple or type(AIRDROP_AMOUNT) is None or id not in TOTAL_BALANCES:
		return False
	AIRDROP_YIELD_PER_TOKEN = (id, AIRDROP_AMOUNT / TOTAL_BALANCES[id])
	return True
